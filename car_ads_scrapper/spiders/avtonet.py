# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from car_ads_scrapper.items import Car
from car_ads_scrapper.itemLoaders import CarLoader
from datetime import datetime
import csv

now = datetime.now()
avtolog_url="https://avtolog.si/search/{vin}"

class BolhaSpider(scrapy.Spider):
    name = 'avtonet'
    allowed_domains = ['avto.net']

    def __init__(self, url=None, scrape_file=None, export_headers=True, *args, **kwargs):
        super(BolhaSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]
        self.scrape_file = scrape_file
        self.export_headers = export_headers

    def parse(self, response):
        ads = response.xpath(
            '//form[contains(@id, "results")]//div[contains(@class, "GO-Results-Row")]//a[contains(@class, "stretched-link")]/@href').extract()
        for ad in ads:
            yield Request(response.urljoin(ad), callback=self.parse_ad)

        next_page = response.xpath(
            '//ul[contains(@class, "pagination")]//li[contains(@class, "GO-Rounded-R")]//a/@href').extract_first()
        yield response.follow(response.urljoin(next_page))

    def parse_ad(self, response):

        loader = CarLoader(item=Car(), response=response)
        loader.add_value('page', self.name)
        loader.add_value('capture_date', now.isoformat())
        loader.add_value('url', response.url)

        model = response.xpath('//div[contains(@class, "container")]//h3/text()').extract_first().strip().split("\xa0")
        loader.add_value('manufacturer', model[0])
        loader.add_value('model', model[-1])

        price = response.xpath('//div[contains(@class, "h-100")]//p/text()').extract_first().strip()
        if not price:
            price = response.xpath('//div[contains(@class, "h-100")]//p/span/text()').extract()[-1].strip()
        price = price.split(" ")[0].replace(".", "")
        if "Pokličite" in price:
            price = None
        loader.add_value('price', price)

        data = response.xpath('//div[contains(@class, "container")]//table//thead//tr//th[contains(text(), "Osnovni podatki")]/../../../tbody/tr')
        for property in data:
            title = property.xpath('./th/text()').extract_first()
            value = property.xpath('./td/text()').extract_first()
            if not title or not value:
                continue
            value = " ".join(value.split())
            title = title.strip()
            if "VIN" in title:
                loader.add_value('vin', value)
                loader.add_value('avtolog_url', avtolog_url.format(vin=value))
            if "Leto proizvodnje:" in title:
                loader.add_value('manufacturing_year', value)
            if "Motor" in title:
                value = value.split(", ")
                loader.add_value('engine_displacement', value[0])
                loader.add_value('engine_power', value[-1])
            if "Gorivo" in title:
                loader.add_value('fuel', value)
            if "Menjalnik" in title:
                loader.add_value('transmission', value)
            if "Prevoženi km" in title:
                loader.add_value('kilometrage', value)
            if "Št.vrat" in title:
                loader.add_value('doors', value)
            if "Notranjost" in title:
                loader.add_value('interior', value)
            if "Barva" in title:
                loader.add_value('color', value)
            if "Kraj ogleda" in title:
                if value == ",":
                    address = property.xpath('//script[contains(text(), "DealerAddress")]/text()').extract_first()
                    start = address.find('\'')
                    end = address.rfind('\';')
                    value = address[start:end]
                    loader.add_value('is_dealership', True)
                else:
                    loader.add_value('is_dealership', False)
                loader.add_value('location', value)

        return loader.load_item()
