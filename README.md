# Treehouse Scraper

Scrapes treehouse beer list for name and prices. The output is a csv of a beer name row and the price below it. This is then copied to a google sheet to do the allotments and cost of hauls.

This uses scrapy (https://scrapy.org/) to do all the heavy lifting and css style selection of text.

To run:

`scrapy runspider onthefly_scraper.py -O beers.json`


Outputs `beers.json` for use in [Treehouse Cases](https://github.com/TheDudeWithTheThing/treehouse-cases)
