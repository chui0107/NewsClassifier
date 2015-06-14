import logging
import sys
import os
import json
import threading
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log, signals
from NewsScaper import *
from scrapy.utils.project import get_project_settings
from CrawlingAlgorithm import CrawlingOption
from NewsBase import CategoryOption
from CrawlingAlgorithm import NYtimesCrawlingAlgorithm
from CrawlingAlgorithm import USATodayCrawlingAlgorithm
from Util import GetDomainName

class TrainingCrawlerCluster:
	import collections
	
	hostToCrawlerDict = collections.defaultdict()
	hostToScraperDict = collections.defaultdict()
	
	categoriesSeeds = collections.defaultdict(lambda:{})
	categoriesWords = collections.defaultdict(lambda:[])
	categoriesWordsLock = threading.Lock()
		
	# create specific crawler according to its domain
	def CreateCrawler(self, host):
		domain = GetDomainName(host.url).lower()
		if domain == 'api.usatoday.com':
			self.hostToCrawlerDict[domain] = USATodayCrawlingAlgorithm(host)
		elif domain == 'api.nytimes.com':
			self.hostToCrawlerDict[domain] = NYtimesCrawlingAlgorithm(host)
		else:
			raise ValueError('Unknown domain')
	
	# fake a dictionary and create a new spider in each call
	def hostToScraperDict(self, domain):
		# domain = GetDomainName(domain).lower()
		if domain.lower() == 'api.usatoday.com':
			return USATodayScraper()
		elif domain.lower() == 'api.nytimes.com':
			return NYTimesScraper()
		else:
			raise ValueError('Unknown domain')
			
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
		self.enableCrawlSeeds = False
		self.enableCrawlPage = True
		
		self.spiderCounter = 0
		
		if self.enableCrawlSeeds == False:
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
	def __SeedingCallBack__(self, newsTuple):
		category = newsTuple[0]
		domain = newsTuple[1]
		url = newsTuple[2]
		
		if domain not in self.trainingCrawlerCluster.categoriesSeeds[category]:
			self.trainingCrawlerCluster.categoriesSeeds[category][domain] = []
		
		self.trainingCrawlerCluster.categoriesSeeds[category][domain].append(url)
	
	# flush the self.categoriesWords to disk
	def __FlushWords__(self):
		
		try:
			self.trainingCrawlerCluster.categoriesWordsLock.acquire()
					
			for category in self.trainingCrawlerCluster.categoriesWords:
										
				fileName = self.trainingSetPath + str(category) + '.txt'
				
				logging.info('flushing %s to file %s', category, fileName)
		
				with open(fileName, 'w+') as f:	
					f.write(str(self.trainingCrawlerCluster.categoriesWords[category]))				
		
		finally:
			self.trainingCrawlerCluster.categoriesWordsLock.release()	
		
	
	# fill the starting urls for the scraper
	def __FillSeeds__(self):

		for fileName in os.listdir(self.trainingSetPath):
			
			if not fileName.lower().endswith("seeds.txt"):
				continue
			
			category = fileName[:-9]
			
			with open(self.trainingSetPath + fileName, 'r') as f:
				
				logging.info('loading the seeds from %s', fileName)
								
				try:
					
					self.trainingCrawlerCluster.categoriesSeeds[category] = json.load(f)
														
				except:
					logging.error('Unexpected error: %s' % sys.exc_info()[0]) 
		
	# flush the categoriesSeeds to disk
	def __FlushSeeds__(self):
		
		for category in self.trainingCrawlerCluster.categoriesSeeds:
			
			text = json.dumps(self.trainingCrawlerCluster.categoriesSeeds[category])
			
			fileName = self.trainingSetPath + str(category) + 'Seeds.txt'
			
			with open(fileName, 'a+') as f:	
				f.write(text)
	
	# populate the category words one by one
	def __ScrapeUrlCallBack__(self, category, item):
						
		try:
			self.trainingCrawlerCluster.categoriesWordsLock.acquire()
			
			title = item.get('articleTitle')
			body = item.get('articleBody')
			
			if title and body:
				self.trainingCrawlerCluster.categoriesWords[category].append((title, body))
				
		except:
			logging.exception('%s.__ScrapeUrlCallBack__:: exception', self.className)	
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
							
					spider = self.trainingCrawlerCluster.hostToScraperDict(domain)
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
				
	def Crawl(self):
		
		if self.enableCrawlSeeds:
			
			for host in self.newsHosts:
				domain = GetDomainName(host.url)
				algo = self.trainingCrawlerCluster.hostToCrawlerDict[domain]
				algo.Crawl(CrawlingOption.TrainingCrawl, domain, self.__SeedingCallBack__, self.categories)
		
			self.__FlushSeeds__()
		
		if self.enableCrawlPage:
			self.__ScrapeUrl__()
			
