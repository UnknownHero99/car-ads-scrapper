# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from car_ads_scrapper.items import Car
from car_ads_scrapper.itemLoaders import CarLoader
from datetime import datetime
import csv

now = datetime.now()

api_url = "https://www.doberavto.si/internal-api/v1"
ads_endpoint = "/marketplace/search?&&&&&&&&&&&results=60&from={offset}"
details_endpoint = "/postings/{ad_id}"
visit_url = "https://www.doberavto.si/oglas/{ad_id}"

avtolog_url="https://avtolog.si/search/{vin}"

class DoberAvtoSpider(scrapy.Spider):
    name = 'doberavto'
    allowed_domains = ['doberavto.si']
    start_urls = [api_url+ads_endpoint.format(offset=0)]
    custom_settings = {}
    custom_settings["CONCURENT_REQUESTS"] = 32

    def __init__(self, url=None, scrape_file="doberavto.csv", export_headers=True, *args, **kwargs):
        super(DoberAvtoSpider, self).__init__(*args, **kwargs)
        self.scrape_file = scrape_file
        self.export_headers = export_headers

    def parse(self, response, offset=0):
        json_data = response.json()
        if not json_data.get("results"):
            return #end of pagination

        for ad in json_data.get("results"):
            ad_id = ad.get("postId")
            print(ad_id)
            yield Request(api_url+details_endpoint.format(ad_id=ad_id), callback=self.parse_ad)

        offset = offset + len(json_data.get("results"))
        yield Request(api_url+ads_endpoint.format(offset=offset), callback=self.parse, cb_kwargs={"offset":offset})


    def parse_ad(self, response):
        json_data = response.json()

        loader = CarLoader(item=Car(), response=response)
        loader.add_value('page', self.name)
        loader.add_value('capture_date', now.isoformat())
        loader.add_value('url', visit_url.format(ad_id=json_data.get("code")))

        loader.add_value('manufacturer', json_data.get("vehicleManufacturerName"))
        loader.add_value('model', json_data.get("vehicleBaseModelName"))

        loader.add_value('price', json_data.get("price"))
        loader.add_value('manufacturing_year', json_data.get("vehicleTrimYear"))
        loader.add_value('engine_displacement', json_data.get("vehicleEngineDisplacement"))
        loader.add_value('engine_power', json_data.get("vehicleEnginePower"))
        loader.add_value('fuel', json_data.get("vehicleFuelType"))
        loader.add_value('transmission', json_data.get("vehicleTransmissionType"))
        loader.add_value('kilometrage', json_data.get("vehicleCurrentOdometer"))
        loader.add_value('doors', json_data.get("vehicleDoors"))
        loader.add_value('color', json_data.get("vehicleExteriorColorDescription"))
        loader.add_value('is_dealership', json_data.get("contactIsDealership"))
        loader.add_value('location', json_data.get("contactPlace"))
        loader.add_value('vin', json_data.get("vin"))
        loader.add_value('avtolog_url', avtolog_url.format(vin=json_data.get("vin")))



        return loader.load_item()
