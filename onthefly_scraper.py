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

        mixed_parse = self.parse_mixed(title, price, beers)
        case_parse = self.parse_case(title, price, text)
        four_parse = self.parse_four_pack(title, price, beers)
        six_parse = self.parse_six_pack(title, price, beers)
        twelve_parse = self.parse_twelve_pack(title, price, beers)
        singles_parse = self.parse_singles(title, price, beers)

        if mixed_parse:
            for m in mixed_parse:
                yield m
        elif case_parse:
            yield case_parse
        elif four_parse:
            yield four_parse
        elif six_parse:
            yield six_parse
        elif twelve_parse:
            yield twelve_parse
        elif singles_parse:
            yield singles_parse
        else:
            if self.is_beer(title):
                yield {"type": "unknown", "title": title, "price": price, "text": text, "debug": beers.getall()}
            else:
                yield {"type": "merch", "title": title, "price": price}

    def parse_case(self, title, price, text):
        if "24 cans" in text or "one case" in text:
            return {
                "type": "case",
                "title": self.extract_beer_name(title) + " Case",
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
                            "beer": self.extract_beer_name(quantity_and_name[2]),
                        }
                    )
            return parsed_list

        return None

    def parse_singles(self, title, price, beers):
        text = "".join(beers.css("::text").getall()).lower()
        if (
            "maximum mrder" in text
            or "one bottle" in text
            or "bottles per order" in text
            or "one 12 oz. bottle" in text
            or re.match(r"limit \d+ bottle", text)
            or re.match(r"limit \w+ bottle", text)
        ):
            return {
                "type": "single",
                "title": title,
                "price": price,
                "quantity": "1",
                "beer": self.extract_beer_name(title),
            }

        return None

    def parse_four_pack(self, title, price, beers):
        text = "".join(beers.css("::text").getall())
        if (
            "four-pack" in text
            or "4-pack" in text
            or "4-Pack" in title
            or "4-Pack" in text
            or "4 pk" in title
            or "4 Pack" in title
            or "four pack" in text
        ):
            return {
                "type": "four",
                "title": title,
                "price": price,
                "quantity": "4",
                "beer": self.extract_beer_name(title),
            }

        return None

    def parse_six_pack(self, title, price, beers):
        text = "".join(beers.css("::text").getall())
        if "six-pack" in text or "6-pack" in text or "6-Pack" in title or "6 pk" in title or "6 Pack" in title:
            return {
                "type": "six",
                "title": title,
                "price": price,
                "quantity": "6",
                "beer": self.extract_beer_name(title),
            }

        return None

    def parse_twelve_pack(self, title, price, beers):
        text = "".join(beers.css("::text").getall())
        if "12 pack" in text or "12-pack" in title:
            return {
                "type": "twelve",
                "title": title,
                "price": price,
                "quantity": "12",
                "beer": self.extract_beer_name(title),
            }

        return None

    def extract_beer_name(self, text):
        name = re.search(r"^(.+) Flagship", text)
        if name:
            return name[1].strip()

        maybe_beer_names = [
            "Homemade",
            "King Julius",
            "JJJULIUSSS",
            "Very Green",
            "GGGreennn",
            "Abstraction",
            "AAAlterrr Ego",
            "Alter Ego",
            "At Ease",
            "Autumn",
            "Bear",
            "Beginner's Mind",
            "BBBrighttt Galaxy",
            "Brisk",
            "Cachet",
            "Catharsis",
            "Crew Beer",
            "Curiosity One Hundred Five",
            "Daze",
            "Fall Classic",
            "Force of Will",
            "Free To Roam",
            "Fruit Project",
            "Fudge",
            "Ghost Emoji",
            "Green",
            "Harmony",
            "Haze",
            "Hold On To Sunshine",
            "Impermanence",
            "Juice Machine",
            "Juice Project Citra + Amarillo",
            "Julius",
            "Little Fire",
            "Little Nugget",
            "Moment of Clarity",
            "New Decade Do-Over",
            "Nomad",
            "Old Man",
            "On The Fly",
            "Peach Tart",
            "Perfect Storm",
            "Permanence",
            "Persist",
            "Raven",
            "Rover",
            "Snow",
            "Space & Time Russian Imperial Stout",
            "Super Radiant",
            "Super Sap",
            "Super Treat",
            "Super Vivid",
            "Sweet Ride",
            "The Universe Is Indifferent",
            "Trail",
            "Thankful",
            "Tranquility",
            "Trick",
            "Unity",
            "Wanderer",
            "Warmth",
            "Whisper Oktoberfest",
        ]

        for beer_name in maybe_beer_names:
            if beer_name.lower() in text.lower():
                return beer_name.strip()

        return text.strip()

    def is_beer(self, title):
        non_beer_terms = [
            "company hat",
            "apple cider",
            "heritage cider",
            "chemex",
            "can chiller",
            "coffee mug",
            "diner mug",
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
            "ornament",
        ]
        lower_title = title.lower()
        return not any(word in lower_title for word in non_beer_terms)

    def extract_hops(self, text):
        hops = ["Amarillo", "Citra", "Galaxy", "El Dorado", "Mosaic", "Simcoe", "Strata", "Warrior"]
        lower_title = text.lower()

        return None
