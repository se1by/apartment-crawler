import os
import pickle
import unittest

from scrapy.http import Request, HtmlResponse
from spider.ImmoScoutSpider import ImmoScoutSpider
from spider.ImmoScoutSpider import get_number


class ImmoScoutSpiderTest(unittest.TestCase):

    def test_any_apartment_in_hamburg(self):
        spider = ImmoScoutSpider('Hamburg', 'Hamburg')
        result = spider.parse(load_fake_response('immoscout_fake.html'))
        self.assertIsNotNone(next(result))

    def test_generates_correct_apartment(self):
        result = ImmoScoutSpider.parse_listing(load_fake_response('immoscout_fake_listing.html'))
        with open('immoscout_fake_listing.pkl', 'rb') as f:
            self.assertEqual(next(result), pickle.load(f))

    def test_generates_correct_url(self):
        self.assertEqual('https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Hamburg/Hamburg'
                         '/Wandsbek/-/56,00-/EURO--1200,00',
                         ImmoScoutSpider.generate_url("Hamburg", "Hamburg", "Wandsbek", 56, 1200))

    def test_parses_correct_numbers(self):
        self.assertEqual(get_number('2'), '2')
        self.assertEqual(get_number('20'), '20')
        self.assertEqual(get_number('20,4'), '20.4')
        self.assertEqual(get_number('20.4'), '20.4')
        self.assertEqual(get_number('20.45 €'), '20.45')
        self.assertEqual(get_number('20,45 €'), '20.45')
        self.assertEqual(get_number('20.4 m²'), '20.4')
        self.assertEqual(get_number('in Nebenkosten enthalten'), 0)


def load_fake_response(file_name, url=None):
    if not url:
        url = 'https://example.com'

    request = Request(url=url)
    if not file_name[0] == '/':
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, file_name)
    else:
        file_path = file_name

    with open(file_path, 'r', encoding='utf-8') as file_content:
        response = HtmlResponse(url=url,
                                request=request,
                                body=file_content.read(),
                                encoding='utf-8')
    return response


if __name__ == '__main__':
    unittest.main()
