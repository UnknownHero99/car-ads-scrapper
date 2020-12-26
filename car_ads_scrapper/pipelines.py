# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import datetime
from scrapy.exporters import CsvItemExporter
from scrapy import signals

column_order = ["page","capture_date","is_dealership","manufacturer","model","vin","avtolog_url","price","manufacturing_year","kilometrage","engine_displacement","engine_power","fuel","transmission","doors","color","interior","location","url","text"]

now = datetime.datetime.now()

class CSVPipeline(object):

  def __init__(self):
    self.files = {}

  @classmethod
  def from_crawler(cls, crawler):
    pipeline = cls()
    crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
    crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
    return pipeline

  def spider_opened(self, spider):
    filename = spider.scrape_file if spider.scrape_file else spider.config_name
    file = open(filename, 'a+b')
    self.files[spider] = file
    self.exporter = CsvItemExporter(file, spider.export_headers)
    self.exporter.fields_to_export = column_order

    self.exporter.start_exporting()

  def spider_closed(self, spider):
    self.exporter.finish_exporting()
    file = self.files.pop(spider)
    file.close()

  def process_item(self, item, spider):
    self.exporter.export_item(item)
    return item

class JsonWriterPipeline(object):
    def open_spider(self, spider):
        self.file = open("scraped_data/" + spider.name + ".json", 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
