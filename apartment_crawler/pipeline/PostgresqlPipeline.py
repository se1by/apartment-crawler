import psycopg2 as psycopg2

from Apartment import Apartment


class PostgresqlPipeline(object):

    def __init__(self, host, user, password, database):
        self.conn = None
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('POSTGRESQL_HOST'),
            user=crawler.settings.get('POSTGRESQL_USER'),
            password=crawler.settings.get('POSTGRESQL_PASSWORD'),
            database=crawler.settings.get('POSTGRESQL_DATABASE')
        )

    def open_spider(self, spider):
        self.conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password)
        with self.conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS apartment (
                    link VARCHAR(255) PRIMARY KEY,
                    title VARCHAR(512) NOT NULL,
                    area NUMERIC(6,2) NOT NULL,
                    rooms NUMERIC(5,2),
                    cold_rent NUMERIC(7,2) NOT NULL,
                    total_rent NUMERIC(7,2),
                    utility_cost NUMERIC(6, 2),
                    heating_cost NUMERIC(6, 2),
                    heating_included BOOLEAN,
                    address VARCHAR(256) NOT NULL,
                    description VARCHAR(5120),
                    insertion_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    apartment_link VARCHAR(255) REFERENCES apartment(link),
                    src VARCHAR(512) NOT NULL,
                    index INT NOT NULL,
                    PRIMARY KEY (apartment_link, src)
                );
            """)

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        if not isinstance(item, Apartment):
            raise ValueError('PostgresqlPipeline can only handle apartment items!')

        with self.conn.cursor() as cursor:
            cursor.execute('INSERT INTO apartment VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, DEFAULT)'
                           'ON CONFLICT (link) DO UPDATE SET title = %s, area = %s, rooms = %s, cold_rent = %s,'
                           'total_rent = %s, utility_cost = %s, heating_cost = %s, heating_included = %s,'
                           ' address = %s, description = %s;',
                           [item['link'], item['title'], item['area'], item['rooms'], item['cold_rent'],
                            item['total_rent'], item['utility_cost'], item['heating_cost'], item['heating_included'],
                            item['address'], item['description'], item['title'], item['area'], item['rooms'],
                            item['cold_rent'], item['total_rent'], item['utility_cost'],
                            item['heating_cost'], item['heating_included'], item['address'], item['description']])
            for index, image in enumerate(item['images']):
                cursor.execute('INSERT INTO images VALUES(%s, %s, %s) ON CONFLICT DO NOTHING;',
                               [item['link'], image, index])
        self.conn.commit()
