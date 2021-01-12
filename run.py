#!/bin/python

# To run from python simply do:
# import run
# run.execute_spiders(run.all_spiders)
#

import sys
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiderloader import SpiderLoader
from scrapy.utils.project import get_project_settings
import pandas as pd
from datetime import datetime
import json
import geocoder
import os
import smtplib

now = datetime.now()
columns_ordering = ["new","points","price","manufacturer","model", "location", "url", "distance", "active", "first_capture_date", "last_capture_date", "found_location", "page","is_dealership","vin","avtolog_url","price","manufacturing_year","kilometrage","engine_displacement","engine_power","fuel","transmission","doors","color","interior","location","url","text"]

def execute_spiders(urls, scrape_file):

    process = CrawlerProcess(get_project_settings())

    spiders = []
    export_headers = True
    for url in urls:
        if "avto.net" in url:
            spider_name = "avtonet"
        else:
            print("No spdider for url: " + url + ", skipping ...")
            continue
        spider = process.create_crawler(spider_name)
        spiders.append(spider)
        process.crawl(spider, url = url, scrape_file = scrape_file, export_headers = export_headers)
        export_headers = False #so only first wil export them

    process.start() # the script will block here until the crawling is finished

    for spider in spiders:
        stats = spider.stats.get_stats()
        print("Spider " + spider.spider.name + " executed in " + str(stats.get("elapsed_time_seconds")))
        print("  Scraped " + str(stats.get("item_scraped_count",0)) + " items")
        if "log_count/ERROR" in stats:
            print("  Errors in spider " + spider.name + "!!!")
        print()


def analyze_data(name, ignore_list, calculate_points, distance_from, scrape_file, archive_data_file, print_columns):
    print("###############")
    print("Getting data for analysis")


    scraped_data = pd.read_csv(scrape_file, parse_dates = ["capture_date"])
    scraped_data["new"] = True
    scraped_data["active"] = True
    scraped_data["first_capture_date"] = scraped_data.capture_date
    scraped_data["last_capture_date"] = scraped_data.capture_date
    scraped_data["found_location"] = None
    scraped_data["distance"] = None

    print("###############")
    print("Getting archived data")

    if os.path.exists(archive_data_file):
        current_data = pd.read_csv(archive_data_file, parse_dates = ["first_capture_date", "last_capture_date"])
        current_data.new = False
    else:
        current_data = scraped_data
        current_data = current_data.drop(columns = ["capture_date"])


    # mark all current_data not in the scraped_data as gone
    current_data.active = current_data.apply(lambda x: x.url in scraped_data.url.values, axis = 1)
    # update capture dates
    current_data.loc[current_data.url.isin(scraped_data.url), "last_capture_date"] = current_data.loc[current_data.url.isin(scraped_data.url),"url"].map(scraped_data.loc[scraped_data.url.isin(current_data.url)].set_index("url").capture_date)

    # add new data
    scraped_data = scraped_data.drop(columns = ["capture_date"])
    current_data = pd.concat([current_data, scraped_data.loc[~scraped_data.url.isin(current_data.url)]])

    current_data["captured_today"] = current_data.first_capture_date.dt.date == now.date()
    # fix locations
    current_data.location = current_data.location.apply(lambda x: clear_location(x))
    print("###############")
    print("Removing ignored ads")
    current_data = current_data.loc[~current_data.url.isin(ignore_list)]
    for ignore_word in ignore_list:
        if "http" in ignore_word:
            continue
        ignore_word = ignore_word.lower()
        print(ignore_word)
        current_data = current_data.loc[~(current_data.text.astype(str).str.lower().str.contains(ignore_word))]
        current_data = current_data.loc[~current_data.location.str.contains(ignore_word)]
    print("###############")
    print("Finding locations")
    # fix locations
    center = geocoder.osm(distance_from)

    #get locations
    found_locations = []
    current_data.loc[current_data.found_location.isnull(), "found_location"] = current_data[current_data.found_location.isnull()].apply(lambda x: find_location(x.location, center), axis=1)

    print("###############")
    print("Getting distances")
    # get distance
    current_data.loc[current_data.distance.isnull(), "distance"] = current_data[current_data.distance.isnull()].apply(lambda x: get_distance(x.found_location, center), axis=1)

    print("###############")
    print("Calculating points")
    current_data["points"] = current_data.apply(lambda x: calculate_points(x), axis=1)

    print("###############")
    print("sorting and storing data")

    sorted_list = current_data.sort_values(by="points", ascending = False)

    sorted_list[columns_ordering].to_csv(archive_data_file, index = False, encoding='utf-8')

    print("###############")
    print("Top 20")
    pd.set_option('display.max_colwidth', None)
    print(sorted_list[print_columns].head(20).to_string(index=False))

    print("Got a total of: " + str(len(sorted_list.index)) + " ads")

    print("###############")
    print("New since last run: " + str(len(sorted_list.loc[sorted_list.new])))
    print(sorted_list.loc[sorted_list.new, print_columns].to_string(index=False))

    print("###############")
    print("Statistics")
    print(sorted_list.describe())
    print()

    print("###############")
    print("All done archive saved to: " + archive_data_file)
    output = {"all":sorted_list, "new":sorted_list.loc[sorted_list.new, print_columns].to_string(index=False), "top20": sorted_list[print_columns].head(20).to_string(index=False)}
    return output


def clear_location(location):
     location = str(location)
     locations = location.lower().replace("-", ",").replace("lj.", "ljubljana,").split(",")
     return ",".join([x for x in locations if x.find("lokac") == -1])

def find_location(location, center):
    locations = location.split(",")
    loc = geocoder.osm(location)
    if (not loc.ok or loc.city != center.city) and len(locations) > 1:
        loc = geocoder.osm(center.city + "," + locations[-1])
    if (not loc.ok or loc.city != center.city) and len(locations) > 2:
        loc = geocoder.osm(center.city + "," + locations[-2])
    if not loc.ok:
        loc = geocoder.osm(center.city)
    return loc

def get_distance(location, center):
    if location.country == center.country and location != center:
        distance = geocoder.distance(center, location)
    else:
        distance = -1
    return distance


def send_mail(gmail_user, gmail_password, to, message):

    sent_from = gmail_user
    subject = 'RealestateScrapper report'

    email_text = """\
        From: %s
        To: %s
        Subject: %s

        %s
        """ % (sent_from, ", ".join(to), subject, message)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text.encode("utf-8"))
        server.close()
        print('Email sent!')
    except:
        print('Something went wrong...')

def main(name, urls, ignore_list, calculate_points, distance_from, scrape_file, archive_data_file, print_columns, mails = None):
    # if os.path.exists(scrape_file):
    #     os.remove(scrape_file)
    # execute_spiders(urls, scrape_file)
    data = analyze_data(name, ignore_list, calculate_points, distance_from, scrape_file, archive_data_file, print_columns)
    return data
