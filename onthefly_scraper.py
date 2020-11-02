import re
import scrapy


class BrickSetSpider(scrapy.Spider):
    name = "treehouse_scraper"
    start_urls = ["https://treehousebrew.com/shop/"]

    def parse(self, response):
        for product_link in response.css(".grid-item > a.grid-item-link"):
            yield response.follow(product_link, self.parse_product_page)

    def parse_product_page(self, response):
        title = response.css(".ProductItem-details-title::text").getall()[0]
        price = response.css(".product-price > .sqs-money-native::text").getall()[0]
        beers = response.css(".ProductItem-details-excerpt > p")

        text = "".join(beers.css("::text").getall())

        case_parse = self.parse_case(title, price, text)
        mixed_parse = self.parse_mixed(title, price, beers)
        four_parse = self.parse_four_pack(title, price, beers)
        six_parse = self.parse_six_pack(title, price, beers)
        singles_parse = self.parse_singles(title, price, beers)

        if case_parse:
            yield case_parse
        elif mixed_parse:
            for m in mixed_parse:
                yield m
        elif four_parse:
            yield four_parse
        elif six_parse:
            yield six_parse
        elif singles_parse:
            yield singles_parse
        else:
            if self.is_beer(title):
                yield {"type": "unknown", "title": title, "price": price, "text": text, "debug": beers.getall()}
            else:
                yield {"type": "merch", "title": title, "price": price, "text": text}

    def parse_case(self, title, price, text):
        if re.search(r"24 cans", text):
            return {
                "type": "case",
                "title": title,
                "price": price,
                "quantity": "24",
                "beer": self.extract_beer_name(title),
            }

        return None

    def parse_mixed(self, title, price, beers):
        text = "".join(beers.css("::text").getall())
        if "Contains:" in text or "Mix Pack" in title:
            parsed_list = []
            for beer in beers:
                beer_text = "".join(beer.css("::text").getall())
                quantity_and_name = re.search(r"^(\d+)[\t|\s](.*)", beer_text)
                if quantity_and_name:
                    parsed_list.append(
                        {
                            "type": "mixed",
                            "title": title,
                            "price": price,
                            "quantity": quantity_and_name[1],
                            "beer": quantity_and_name[2],
                        }
                    )
            return parsed_list

        return None

    def parse_singles(self, title, price, beers):
        text = "".join(beers.css("::text").getall())
        if "Maximum Order" in text or "one bottle" in text:
            return {
                "type": "single",
                "title": title,
                "price": price,
                "quantity": "1",
                "beer": title,
            }

        return None

    def parse_four_pack(self, title, price, beers):
        text = "".join(beers.css("::text").getall())
        if "four-pack" in text or "4-pack" in text or "4-Pack" in title or "4 pk" in title or "4 Pack" in title:
            return {
                "type": "four",
                "title": title,
                "price": price,
                "quantity": "4",
                "beer": title,
            }

        return None

    def parse_six_pack(self, title, price, beers):
        text = "".join(beers.css("::text").getall())
        if "six-pack" in text or "6-pack" in text or "6-Pack" in title or "6 pk" in title or "6 Pack" in title:
            return {
                "type": "six",
                "title": title,
                "price": price,
                "quantity": "4",
                "beer": title,
            }

        return None

    def extract_beer_name(self, text):
        name = re.search(r"^(.+) Flagship", text)
        if name:
            return name[1]

        return text

    def is_beer(self, title):
        non_beer_terms = [
            "company hat",
            "apple cider",
            "can chiller",
            "coffee mug",
            "tote bag",
            "glass",
            "puzzle",
            "pitcher",
            "sticker",
            "tankard",
            "flexfit",
            "teku",
            "cold brew",
            "cancer",
            "logo",
            "whole bean",
            "staff acknowledgement",
            "mason jar",
            "pint",
            "blended coffee",
            "blend coffee",
            "espresso blend",
        ]
        lower_title = title.lower()
        return not any(word in lower_title for word in non_beer_terms)
