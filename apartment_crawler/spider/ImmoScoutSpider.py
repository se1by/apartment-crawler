import re
import scrapy

from Apartment import Apartment


def css_selector_value(response, selector, element_index=0):
    value = response.css(selector).extract()
    if value:
        return value[element_index].strip()
    else:
        return None


def get_number(number_string):
    result_array = re.findall(r'\d+(?:[,.]?\d)*', number_string)
    if len(result_array) == 0:
        return 0
    result = max(result_array)
    if len(result) == 1 or ('.' not in result and ',' not in result):
        return result

    if result[-3] == ',' or result[-3] == '.':
        result = result.replace(',', '').replace('.', '')
        return result[:-2] + '.' + result[-2:]
    elif result[-2] == ',' or result[-2] == '.':
        result = result.replace(',', '').replace('.', '')
        return result[:-1] + '.' + result[-1:]
    else:
        result = result.replace(',', '').replace('.', '')
        return result


class ImmoScoutSpider(scrapy.Spider):
    name = 'ImmoScoutSpider'

    def __init__(self, state, city, districts=None, min_area=0, max_price=0, min_rooms=0,
                 min_price=0, max_rooms=0, max_area=0):
        super().__init__()

        self.start_urls = [
            (self.generate_url(state, city, districts, min_area, max_price, min_rooms, min_price, max_rooms, max_area))
        ]

    @staticmethod
    def generate_url(state, city, districts, min_area=0, max_price=0, min_rooms=0,
                     min_price=0, max_rooms=0, max_area=0):
        if districts is None:
            districts = []
        elif isinstance(districts, str):
            districts = [districts]

        districts_string = '_'.join(districts).replace('ä', 'ae').replace('ö', 'oe')\
            .replace('ü', 'ue').replace('ß', 'ss') if len(districts) > 0 else '-'

        def format_number(number):
            return '{0:.2f}'.format(number).replace('.', ',') if number > 0 else ''

        min_rooms_string = format_number(min_rooms)
        max_rooms_string = format_number(max_rooms)
        min_area_string = format_number(min_area)
        max_area_string = format_number(max_area)
        max_price_string = format_number(max_price)
        min_price_string = format_number(min_price)

        url = f'https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/{state}/{city}/{districts_string}' \
              f'/{min_rooms_string}-{max_rooms_string}' \
              f'/{min_area_string}-{max_area_string}' \
              f'/EURO-{min_price_string}-{max_price_string}'
        return url

    def parse(self, response):
        for url in response.css('.result-list__listing a.result-list-entry__brand-title-container'):
            yield response.follow(url, ImmoScoutSpider.parse_listing)
        for next_page in response.css('a[data-nav-next-page="true"]'):
            yield response.follow(next_page, self.parse)

    @staticmethod
    def parse_listing(response):
        title = css_selector_value(response, '#expose-title::text')
        cold_rent = css_selector_value(response, '.is24qa-kaltmiete::text')
        total_rent = css_selector_value(response, '.is24qa-gesamtmiete::text')
        utility_cost = css_selector_value(response, '.is24qa-nebenkosten::text', 1)
        heating_cost = css_selector_value(response, '.is24qa-heizkosten::text', 1)
        heating_included = "zzgl. Heizkosten" not in total_rent
        deposit = css_selector_value(response, '.is24qa-kaution-o-genossenschaftsanteile::text')
        area = css_selector_value(response, '.is24qa-flaeche::text')
        rooms = css_selector_value(response, '.is24qa-zi::text')
        street = css_selector_value(response, '.address-block span::text')
        zip_code = css_selector_value(response, '.address-block span.zip-region-and-country::text')
        address = street + ' ' + zip_code if street != zip_code else zip_code
        description = css_selector_value(response, '.is24qa-objektbeschreibung::text')
        images = response.css('img.sp-image::attr(data-src)').getall()
        yield Apartment(title=title, cold_rent=get_number(cold_rent),
                        total_rent=get_number(total_rent), utility_cost=get_number(utility_cost),
                        heating_cost=get_number(heating_cost), heating_included=heating_included,
                        deposit=get_number(deposit), area=get_number(area), rooms=get_number(rooms), address=address,
                        description=description, link=response.url, images=images)

