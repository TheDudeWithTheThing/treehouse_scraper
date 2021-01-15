run:
	scrapy runspider scraper.py

datas:
	rm beers.json; scrapy runspider onthefly_scraper.py -O beers.json; cp beers.json ../treehouse-cases/src/datas
