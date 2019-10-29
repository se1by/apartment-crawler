# Apartment Crawler

A simple web crawler for rental apartments.
Currently only contains crawler for german sites.

## Use case:

I'm looking for a new apartment in a major town, and it sucks.
To ease the pain a little bit, this project scans rental websites for new flats that match the specified requirements,
and saves those in a postgresql database so another project can send me periodic emails about them.

## Configuration
Note: commandline arguments always override their environment variable counterpart.
### Environment variables
|        Name         |                   Description                       | Default | Required |
| ------------------- | --------------------------------------------------- | ------- | -------- |
| POSTGRESQL_HOST     | The database host                                   | None    | Yes      |
| POSTGRESQL_DATABASE | The database schema                                 | None    | Yes      |
| POSTGRESQL_USER     | The database user                                   | None    | Yes      |
| POSTGRESQL_PASSWORD | The database password                               | None    | Yes      |
| CONCURRENT_REQUESTS | Maximum number of concurrent requests (total).      | 10      | No       |
| DOWNLOAD_DELAY      | Delay between scraping the same website in seconds. | 2       | No       |

### Commandline arguments
| Flag |      Long flag        |                      Description                   | Default | Required |
| ---- | --------------------- | -------------------------------------------------- | ------- | -------- |
| -s   | --state               | The state to be searched                           | None    | Yes      |
| -c   | --city                | The city to be searched                            | None    | Yes      |
| -d   | --districts           | Comma-seperated list of districts to be searched   | None    | No       |
| -a   | --min-area            | Minimum area of a rental in m²                     | None    | No       |
| -p   | --max-price           | Maximum cold rent of a rental in €                 | None    | No       |
| -r   | --min-rooms           | Minimum number of rooms of a rental                | None    | No       |
|      | --max-area            | Maximum area of a rental in m²                     | None    | No       |
|      | --min-price           | Minimum cold rent of a rental in €                 | None    | No       |
|      | --max-rooms           | Maximum number of rooms of a rental                | None    | No       |
|      | --db-host             | The database host                                  | None    | No       |
|      | --db-database         | The database schema                                | None    | No       |
|      | --db-user             | The database user                                  | None    | No       |
|      | --db-password         | The database password                              | None    | No       |
|      | --concurrent-requests | Maximum number of concurrent requests (total).     | 10      | No       |
|      | --download-delay      | Delay between scraping the same website in seconds | 2       | No       |