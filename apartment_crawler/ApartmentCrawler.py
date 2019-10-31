#! /usr/bin/env python3

import argparse
import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from spider.ImmoScoutSpider import ImmoScoutSpider


class ApartmentCrawler:
    def __init__(self, _args):
        self.state = _args.state
        self.city = _args.city
        self.districts = _args.districts.split(',') if _args.districts else None
        self.min_area = _args.min_area
        self.max_price = _args.max_price
        self.min_rooms = _args.min_rooms
        self.min_price = _args.min_price
        self.max_rooms = _args.max_rooms
        self.max_area = _args.max_area

        self.db_host = _args.db_host if _args.db_host else os.getenv('POSTGRESQL_HOST')
        self.db_database = _args.db_database if _args.db_database else os.getenv('POSTGRESQL_DATABASE')
        self.db_user = _args.db_user if _args.db_user else os.getenv('POSTGRESQL_USER')
        self.db_password = _args.db_password if _args.db_password else os.getenv('POSTGRESQL_PASSWORD')

        self.concurrent_requests = _args.concurrent_requests if _args.concurrent_requests \
            else os.getenv('CONCURRENT_REQUESTS', 10)
        self.download_delay = _args.download_delay if _args.download_delay \
            else os.getenv('DOWNLOAD_DELAY', 2)

        if not self.state:
            raise ValueError('Missing state!')
        if not self.city:
            raise ValueError('Missing city!')
        if not self.db_host:
            raise ValueError('Missing POSTGRESQL_HOST!')
        if not self.db_database:
            raise ValueError('Missing POSTGRESQL_DATABASE!')
        if not self.db_user:
            raise ValueError('Missing POSTGRESQL_USER!')
        if not self.db_password:
            raise ValueError('Missing POSTGRESQL_PASSWORD!')

    def crawl(self):
        configure_logging()
        settings = get_project_settings()
        settings.set('POSTGRESQL_HOST', self.db_host)
        settings.set('POSTGRESQL_DATABASE', self.db_database)
        settings.set('POSTGRESQL_USER', self.db_user)
        settings.set('POSTGRESQL_PASSWORD', self.db_password)

        settings.set('DOWNLOADER_MIDDLEWARES', {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_useragents.downloadermiddlewares.useragents.UserAgentsMiddleware': 500,
        })
        settings.set("CONCURRENT_REQUESTS", self.concurrent_requests)
        settings.set("DOWNLOAD_DELAY", self.download_delay)
        with open('user_agents.txt', 'r') as user_agents_file:
            settings.set('USER_AGENTS', user_agents_file.readlines())

        settings.set('ITEM_PIPELINES', {'pipeline.PostgresqlPipeline.PostgresqlPipeline': 300})
        process = CrawlerProcess(settings)
        results = process.crawl(ImmoScoutSpider, state=self.state, city=self.city, districts=self.districts,
                                min_area=self.min_area, max_price=self.max_price, min_rooms=self.min_rooms,
                                min_price=self.min_price, max_rooms=self.max_rooms, max_area=self.max_area)
        process.start()
        return results


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Crawl rental websites')
    arg_parser.add_argument('-s', '--state', help='State to be searched', default='Hamburg')
    arg_parser.add_argument('-c', '--city', help='City to be searched', default='Hamburg')
    arg_parser.add_argument('-d', '--districts', help='Comma-separated list of districts to be searched')
    arg_parser.add_argument('-a', '--min-area', help='Minimum area of a rental', type=float, default=0)
    arg_parser.add_argument('-p', '--max-price', help='Maximum cold rent of a rental', type=float, default=0)
    arg_parser.add_argument('-r', '--min-rooms', help='Minimum rooms of a rental', type=float, default=0)
    arg_parser.add_argument('--max-area', help='Maximum area of a rental', type=float, default=0)
    arg_parser.add_argument('--min-price', help='Minimum price of a rental', type=float, default=0)
    arg_parser.add_argument('--max-rooms', help='Maximum rooms of a rental', type=float, default=0)
    arg_parser.add_argument('--db-host', help='Host of the postgresql db. Overrides POSTGRESQL_HOST env.')
    arg_parser.add_argument('--db-database', help='Database of the postgresql db. Overrides POSTGRESQL_DATABASE env.')
    arg_parser.add_argument('--db-user', help='User of the postgresql db. Overrides POSTGRESQL_USER env.')
    arg_parser.add_argument('--db-password', help='Password of the postgresql db. Overrides POSTGRESQL_PASSWORD env.')
    arg_parser.add_argument('--concurrent-requests', help='Maximum of concurrent requests (total).')
    arg_parser.add_argument('--download-delay', help='Delay between crawls per domain in seconds.')
    args = arg_parser.parse_args()
    crawler = ApartmentCrawler(args)
    d = crawler.crawl()
    d.addCallback(lambda ignored: print("Done"))
