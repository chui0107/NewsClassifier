import logging
import json
import threading
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log, signals
from NewsScaper import NYTimesScraper, USATodayScraper, PageLinkScraper
from scrapy.utils.project import get_project_settings
from CrawlingAlgorithm import CrawlingOption
from NewsBase import CategoryOption
from CrawlingAlgorithm import NYtimesCrawlingAlgorithm, USATodayCrawlingAlgorithm
from Util import GetDomainName
import csv
import os

class TrainingCrawlerCluster:
	import collections
	className = 'TrainingCrawlerCluster'
	
	hostToCrawlerDict = collections.defaultdict()
	hostToScraperDict = collections.defaultdict()
	
	categoriesSeeds = collections.defaultdict()
	categoriesSeedsLock = threading.Lock()
	
	categoriesWords = collections.defaultdict(lambda:[])
	categoriesWordsLock = threading.Lock()
		
	# create specific crawler according to its domain
	def CreateCrawler(self, host):
		if host.domain == 'usatoday.com':
			self.hostToCrawlerDict[host.domain] = USATodayCrawlingAlgorithm(host)
		elif host.domain == 'nytimes.com':
			self.hostToCrawlerDict[host.domain] = NYtimesCrawlingAlgorithm(host)
		else:
			raise ValueError('Unknown domain')
	
	# fake a dictionary and create a new spider in each call
	def hostToScraperDict(self, urls):
		assert len(urls) > 0, 'empty urls'
		
		if len(urls) == 1:
			domain = GetDomainName(urls[0]).lower()
			if domain.lower() == 'usatoday.com':
				return USATodayScraper()
			elif domain.lower() == 'nytimes.com':
				return NYTimesScraper()
				
		raise NotImplemented()
			
class TrainingCrawler:
	
	trainingCrawlerCluster = TrainingCrawlerCluster()
	className = 'TrainingCrawler'
	
	def __init__(self, newsHosts, categories, trainingSetPath):
			
		self.newsHosts = newsHosts
		
		for host in self.newsHosts:
			try:
				self.trainingCrawlerCluster.CreateCrawler(host)
				
			except ValueError:
				logging.error('%s', ValueError)
				return
			
		self.categories = categories
		self.trainingSetPath = trainingSetPath 
		
		# control variables
		self.enableCrawlSeeds = True
		self.enableCrawlPage = False
		
		self.spiderCounter = 0
		
		self.__FillSeeds__()
		
	# event is fire when a spider is quit
	def __SpiderQuitEvent__(self):
		logging.info('a spider just quit')
		self.spiderCounter -= 1
		print '%d spider remaining' % self.spiderCounter
		# all crawls are finished
		if self.spiderCounter == 0:
			self.__FlushWords__()
			logging.info('stopped the reactor')
			reactor.stop()
	
	# save the url seeds to a file
	def __SeedingCallBack__(self, newsTuple):
		assert newsTuple != None and len(newsTuple) == 3, 'newsTuple invalid'
		
		category = newsTuple[0]
		domain = newsTuple[1]
		urls = newsTuple[2]
		categoryString = str(category)
		try:
			self.trainingCrawlerCluster.categoriesSeedsLock.acquire()
			
			if categoryString not in self.trainingCrawlerCluster.categoriesSeeds:
				self.trainingCrawlerCluster.categoriesSeeds[categoryString] = {}
			
			if domain not in self.trainingCrawlerCluster.categoriesSeeds[categoryString]:
				self.trainingCrawlerCluster.categoriesSeeds[categoryString][domain] = []
			
			for url in urls:
				self.trainingCrawlerCluster.categoriesSeeds[categoryString][domain].append(url)
			
		finally:
			self.trainingCrawlerCluster.categoriesSeedsLock.release()
		
	# flush the self.categoriesWords to disk
	def __FlushWords__(self):
		
		try:
			self.trainingCrawlerCluster.categoriesWordsLock.acquire()
			
			fileName = self.trainingSetPath + 'Words.txt'
			
			logging.info('flushing to file %s', fileName)
			
			text = json.dumps(self.trainingCrawlerCluster.categoriesWords)
						
			with open(fileName, 'w+') as f:	
				f.write(text)
		
		finally:
			self.trainingCrawlerCluster.categoriesWordsLock.release()	
		
	
	# fill the starting urls for the scraper
	def __FillSeeds__(self):

		fileName = self.trainingSetPath + 'Seeds.txt'
		if os.path.exists(fileName) == False:
			return
		
		with open(fileName, 'r') as f:
			
			logging.info('loading the seeds from %s', fileName)
								
			try:
				
				self.trainingCrawlerCluster.categoriesSeeds = json.load(f)
				
			except:
				logging.exception('%s.__ScrapeUrlCallBack__: exception', self.className) 
					
	# flush the categoriesSeeds to disk
	def __FlushSeeds__(self):
		
		logging.info('%s.__FlushSeeds__: Flushing seeds to disk', self.className)
		try:
			self.trainingCrawlerCluster.categoriesSeedsLock.acquire()
			
			
			# get unique urls
			for category in self.trainingCrawlerCluster.categoriesSeeds:
				for domain in self.trainingCrawlerCluster.categoriesSeeds[category]:
					self.trainingCrawlerCluster.categoriesSeeds[category][domain] = list(set(self.trainingCrawlerCluster.categoriesSeeds[category][domain]))
				
			text = json.dumps(self.trainingCrawlerCluster.categoriesSeeds)
			
			fileName = self.trainingSetPath + 'Seeds.txt'
			
			with open(fileName, 'w') as f:	
				f.write(text)
				
		finally:
			self.trainingCrawlerCluster.categoriesSeedsLock.release()	
	
	# populate the category words one by one
	def __ScrapeUrlCallBack__(self, category, item):
						
		try:
			self.trainingCrawlerCluster.categoriesWordsLock.acquire()
			
			title = item.get('articleTitle')
			
			body = item.get('articleBody')
			
			# Note they are lists
			title = title[0] if len(title) else ''
			body = body[0] if len(body) else ''
			
			self.trainingCrawlerCluster.categoriesWords[category].append((title, body))				
				
		except:
			logging.exception('%s.__ScrapeUrlCallBack__: exception', self.className)	
		finally:
			self.trainingCrawlerCluster.categoriesWordsLock.release()
	
			
	# scrape the url 
	def __ScrapeUrl__(self):
		
		# start to scrape from the seeds files
		for category in self.trainingCrawlerCluster.categoriesSeeds:
				
			print 'scraping in category: %s' % category
			
			for domain in self.trainingCrawlerCluster.categoriesSeeds[category]:
				# return the urls for this domain under this category
				
				try:
					urls = self.trainingCrawlerCluster.categoriesSeeds[category][domain]
							
					spider = self.trainingCrawlerCluster.hostToScraperDict([domain])
					spider.SetUrls(urls)
					spider.SetCategory(category)
					spider.SetScraperCallBack(self.__ScrapeUrlCallBack__)
					
					settings = get_project_settings()
					crawler = Crawler(settings)
					crawler.signals.connect(self.__SpiderQuitEvent__, signal=signals.spider_closed)
					crawler.configure()
					crawler.crawl(spider)
					crawler.start()
					self.spiderCounter += 1
								
				except:
					logging.exception('%s.__GetItem__: exception', self.name)
				
		# the script will block here until the spider_closed signal was sent
		reactor.run()
				
	def __CrawlSeed__(self):
		
		'''
		for host in self.newsHosts:
			algo = self.trainingCrawlerCluster.hostToCrawlerDict[host.domain]
			algo.Crawl(CrawlingOption.TrainingCrawl, host.domain, self.__SeedingCallBack__, self.categories)
		'''
		
		# will be edit later		
		with open(self.trainingSetPath + 'Seeds.csv', 'r') as f:
			
			try:
				reader = csv.reader(f)
			except:
				logging.exception('%s.__CrawlSeed__: exception', self.name)
				return
			
			# log.start()	
			for row in reader:
				if row[0].lower() == 'categoryoption.technology' or row[0].lower() == 'categoryoption.sports' or row[0].lower() == 'categoryoption.business':  
					
					try:
						urls = row[1].split('\n')
						logging.info('%s.__CrawlSeed__: crawling for seeds in category %s', self.className, row[0])
						spider = PageLinkScraper()
						
						spider.SetUrls(urls)
						spider.SetCategory(row[0])
						spider.SetScraperCallBack(self.__SeedingCallBack__)
					
						settings = get_project_settings()
						settings.set('DOWNLOAD_TIMEOUT', 30, 'cmdline')
						crawler = Crawler(settings)
						crawler.signals.connect(self.__SpiderQuitEvent__, signal=signals.spider_closed)
						crawler.configure()
						crawler.crawl(spider)
						crawler.start()
						self.spiderCounter += 1
						
					except:
						logging.exception('%s.__CrawlSeed__: exception', self.className)
						self.spiderCounter = 0
						return
						
			# the script will block here until the spider_closed signal was sent
			reactor.run()
			
		self.__FlushSeeds__()
				
	def Crawl(self):
		
		if self.enableCrawlSeeds:
			self.__CrawlSeed__()
			
		if self.enableCrawlPage:
			self.__ScrapeUrl__()
			
