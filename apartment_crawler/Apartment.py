import scrapy


class Apartment(scrapy.Item):
    title = scrapy.Field()
    cold_rent = scrapy.Field()
    total_rent = scrapy.Field()
    heating_included = scrapy.Field()
    area = scrapy.Field()
    rooms = scrapy.Field()
    address = scrapy.Field()
    description = scrapy.Field()
    link = scrapy.Field()
    images = scrapy.Field()
