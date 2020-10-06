# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Car(scrapy.Item):
    page = scrapy.Field()
    url = scrapy.Field()
    capture_date = scrapy.Field()
    model = scrapy.Field()
    price = scrapy.Field()
    manufacturing_year = scrapy.Field()
    kilometrage = scrapy.Field()
    engine_displacement = scrapy.Field()
    engine_power = scrapy.Field()
    transmission = scrapy.Field()
    fuel = scrapy.Field()
    VIN = scrapy.Field()
    is_dealership = scrapy.Field()
    doors = scrapy.Field()
    color = scrapy.Field()
    location = scrapy.Field()