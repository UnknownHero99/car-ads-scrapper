from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join, TakeFirst

def parseYear(values):
    for value in values:
        yield int(value)

def parseSize(values):
    for value in values:
        number = value.split(" ")[0].strip().replace(",", ".").replace('"', '')
        yield float(number)

def parsePrice(values):
    for value in values:
        number = value.split(" ")[0].strip().replace(".", "").replace(",",".").replace('"','')
        yield float(number)

def parseText(values):
    for value in values:
        yield value.lower().replace("<","").replace(">"," ").replace("/","").replace('"'," ").strip().replace("\n","").replace("  "," ")

class CarLoader(ItemLoader):
    default_output_processor = TakeFirst()
    size_in = parseSize
    price_in = parsePrice
    built_in = parseYear
    renewed_in = parseYear
    text_in = parseText
