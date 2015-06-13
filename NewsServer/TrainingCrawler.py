import logging
import sys
import os
import threading
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log, signals
from NewsScaper import NYTimesScraper
from scrapy.utils.project import get_project_settings
from CrawlingAlgorithm import CrawlingOption
from scrapy.xlib.pydispatch import dispatcher
		
class TrainingCrawlerCluster:
	import collections
	
	categoriesSeeds = collections.defaultdict(lambda: [])
	categoriesWords = collections.defaultdict(lambda: [])
	categoriesWordsLock = threading.Lock()		
		
class TrainingCrawler:
	
	trainingCrawlerCluster = TrainingCrawlerCluster()
	
	def __init__(self, newsHosts, categories, trainingSetPath):
		
		self.newsHost = newsHosts
		self.categories = categories
		self.trainingSetPath = trainingSetPath 
		
		self.enableCrawlSeeds = False
		self.enableCrawlPage = True
		
		self.spiderCounter = 0
		
		# second param is instance of spder about to be closed.
		self.__FillSeeds__()
	
	# event is fire when a spider is quit
	def __SpiderQuitEvent__(self):
		logging.info('a spider just quit')
		self.spiderCounter -= 1
		
		# all crawls are finished
		if self.spiderCounter == 0:
			self.__FlushWords__()
			logging.info('stopped the reactor')
			reactor.stop()
	
	# save the url seeds to a file
	def __SaveToFile__(self, newsTuple):
		category = newsTuple[0]
		url = newsTuple[1]
		self.trainingCrawlerCluster.categoriesSeeds[category].append(url)
	
	# flush the self.categoriesWords to disk
	def __FlushWords__(self):
		
		logging.info('flushing categorized words to disk')
		
		try:
			self.trainingCrawlerCluster.categoriesWordsLock.acquire()
					
			for category in self.trainingCrawlerCluster.categoriesWords:
			
				fileName = self.trainingSetPath + category + '.txt'
		
				with open(fileName, 'w+') as f:	
					f.write(str(self.trainingCrawlerCluster.categoriesWords[category]))				
		
		finally:
			self.trainingCrawlerCluster.categoriesWordsLock.release()	
		
		
	# flush the categoriesSeeds to disk
	def __FlushSeeds__(self):
		
		for category in self.trainingCrawlerCluster.categoriesSeeds:
			logging.info('flushing %s news to the disk', category)
			
			text = str(self.trainingCrawlerCluster.categoriesSeeds[category])
			
			fileName = self.trainingSetPath + category + 'Seeds.txt'
			
			with open(fileName, 'w+') as f:	
				f.write(text)
	
	# populate the category words one by one
	def __ScrapeUrlCallBack__(self, itemTuple):
		category = itemTuple[0]
		item = itemTuple[1]
		
		try:
			self.trainingCrawlerCluster.categoriesWordsLock.acquire()
					
			self.trainingCrawlerCluster.categoriesWords[category].append((item['articleTitle'], item['articleBody']))
			
		finally:
			self.trainingCrawlerCluster.categoriesWordsLock.release()	
	
	# scrape the url 
	def __ScrapeUrl__(self, category, urls):
		
		spider = NYTimesScraper(category=category, urls=urls, scraperCallBack=self.__ScrapeUrlCallBack__)
		settings = get_project_settings()
		crawler = Crawler(settings)
		crawler.signals.connect(self.__SpiderQuitEvent__, signal=signals.spider_closed)
		crawler.configure()
		crawler.crawl(spider)
		crawler.start()
		self.spiderCounter += 1
		
	# fill the starting urls for the scraper
	def __FillSeeds__(self):
		import ast

		for fileName in os.listdir(self.trainingSetPath):
			
			if not fileName.lower().endswith("seeds.txt"):
				continue
			
			category = fileName[:-9]
			
			with open(self.trainingSetPath + fileName, 'r') as f:
				
				logging.info('loading the seeds')
								
				try:
						
					text = f.read()
					
					self.trainingCrawlerCluster.categoriesSeeds[category] = ast.literal_eval(text) 
									
				except:
					logging.error('Unexpected error: %s' % sys.exc_info()[0]) 
		
	def Crawl(self):
		
		if self.enableCrawlSeeds:
			
			for host in self.newsHost:
				algo = host[1]
				algo.Crawl(CrawlingOption.TrainingCrawl, self.__SaveToFile__, self.categories)
				break
		
			self.__FlushSeeds__()
		
		if self.enableCrawlPage:		
			# start to scrape from the seeds files
			for category in self.trainingCrawlerCluster.categoriesSeeds:
				
				print 'scraping in category: %s' % category
				self.__ScrapeUrl__(category, self.trainingCrawlerCluster.categoriesSeeds[category])
			
			# the script will block here until the spider_closed signal was sent
			reactor.run()

