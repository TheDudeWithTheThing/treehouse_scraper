import re
import scrapy


class BrickSetSpider(scrapy.Spider):
    name = "treehouse_scraper"
    start_urls = ["https://treehousebrew.com/shop/"]

    def parse(self, response):
        for product_link in response.css(".grid-item > a.grid-item-link"):
            yield response.follow(product_link, self.parse_product_page)

    def clean_up(self, text):
        return re.sub(r"\n\s+", "", text)

    def parse_product_page(self, response):
        title = self.clean_up(response.css(".ProductItem-details-title::text").getall()[0])
        price = response.css(".product-price > .sqs-money-native::text").getall()[0]
        beers = response.css(".ProductItem-details-excerpt > p")

        text = "".join(beers.css("::text").getall())

        mixed_parse = self.parse_mixed(title, price, beers)
        case_parse = self.parse_case(title, price, text)
        four_parse = self.parse_four_pack(title, price, beers)
        six_parse = self.parse_six_pack(title, price, beers)
        twelve_parse = self.parse_twelve_pack(title, price, beers)
        singles_parse = self.parse_singles(title, price, beers)
        merch_parse = self.parse_merch(title, price)

        if merch_parse:
            yield merch_parse
        elif mixed_parse:
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

    def parse_merch(self, title, price):
        if not self.is_beer(title):
            return {"type": "merch", "title": title, "price": price, "quantity": 1, "beer": title}

        return None

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
        if "Contains:" in text or "mix pack" in title.lower():
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
            "maximum order" in text
            or "one bottle" in text
            or "single can" in title.lower()
            or "bottles per order" in text
            or "per person" in text
            or "one 12 oz. bottle" in text
            or "500 ml bottle" in title.lower()
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
            "four-pack" in text.lower()
            or "4-pack" in text.lower()
            or "4-pack" in title.lower()
            or "4 pk" in title.lower()
            or "4 pack" in title.lower()
            or "four pack" in text.lower()
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
            "Very GGGreennn",
            "Very Green",
            "GGGreennn",
            "Abstraction",
            "AAAlterrr Ego",
            "Alter Ego",
            "At Ease",
            "Autumn",
            "Bear",
            "Beginner's Mind",
            "Beneficiaries of Chance",
            "BBBrighttt Galaxy",
            "Big Nugget",
            "Brisk",
            "Brownie",
            "Cachet",
            "Catharsis",
            "Cozy",
            "Crew Beer",
            "Curiosity One Hundred Five",
            "Daze",
            "Doubleganger",
            "Fall Classic",
            "Force of Will",
            "Free To Roam",
            "Fudge",
            "Ghost Emoji",
            "Green",
            "Harmony",
            "Haze",
            "Hold On To Sunshine",
            "Human Condition",
            "Impermanence",
            "Iridescent",
            "Juice Machine",
            "Juice Project Citra + Amarillo",
            "Juice Project Citra + Simcoe",
            "Juice Project",
            "Julius",
            "Little Fire",
            "Little Nugget",
            "Moment of Clarity",
            "Nervous Energy",
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
            "Spring",
            "Steadfast",
            "Super Radiant",
            "Super Sap",
            "Super Treat",
            "Super Typhoon",
            "Super Vivid",
            "Sweet Ride Fluffernutter",
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
            if re.search(rf"\b{beer_name.lower()}\b", text.lower()):
                return beer_name.strip()

        return text.strip()

    def is_beer(self, title):
        non_beer_terms = [
            "leather patch",
            "bottle opener",
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
            "starter kit",
            "ornament",
        ]
        lower_title = title.lower()
        return not any(word in lower_title for word in non_beer_terms)

    def extract_hops(self, text):
        hops = ["Amarillo", "Citra", "Galaxy", "El Dorado", "Mosaic", "Simcoe", "Strata", "Warrior"]
        lower_title = text.lower()

        return None
