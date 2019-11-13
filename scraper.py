import csv
import re
import scrapy


class BrickSetSpider(scrapy.Spider):
    name = "treehouse_scraper"
    start_urls = ["https://www.treehousebrew.com/on-tap"]

    def parse(self, response):
        beer_names_prices = dict()

        for beer in response.css(".sqs-block-content > p"):

            beer_name = beer.css("strong ::text").extract_first()
            beer_desc = beer.xpath("text()").get()

            if beer_desc is None:
                continue

            beer_price = re.search("(\d\.\d\d)[^%]", beer_desc)
            if beer_price is None:
                continue

            beer_price = beer_price[1]

            if beer_name and beer_price:
                beer_names_prices[beer_name] = beer_price

        write_csv(beer_names_prices)


def write_csv(names_prices):
    name_row = list()
    price_row = list()

    for name in sorted(names_prices.keys()):
        name_row.append(name)
        price_row.append(names_prices[name])

    with open("treehouse.csv", "w") as the_csv:
        csv_writer = csv.writer(the_csv)
        csv_writer.writerow(name_row)
        csv_writer.writerow(price_row)
