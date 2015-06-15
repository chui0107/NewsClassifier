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
from CrawlingAlgorithm import NYtimesCrawlingAlgorithm, USATodayCrawlingAlgorithm
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
		
		categoryString = str(category)
	
		if domain not in self.trainingCrawlerCluster.categoriesSeeds[categoryString]:
			self.trainingCrawlerCluster.categoriesSeeds[categoryString][domain] = []
		
		self.trainingCrawlerCluster.categoriesSeeds[categoryString][domain].append(url)
	
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
		with open(fileName, 'r') as f:
			
			logging.info('loading the seeds from %s', fileName)
								
			try:
				
				self.trainingCrawlerCluster.categoriesSeeds = json.load(f)
				
			except:
				logging.exception('%s.__ScrapeUrlCallBack__: exception', self.className) 
					
	# flush the categoriesSeeds to disk
	def __FlushSeeds__(self):
		
		text = json.dumps(self.trainingCrawlerCluster.categoriesSeeds)
			
		fileName = self.trainingSetPath + 'Seeds.txt'
			
		with open(fileName, 'a+') as f:	
			f.write(text)
		
			
	# populate the category words one by one
	def __ScrapeUrlCallBack__(self, category, item):
						
		try:
			self.trainingCrawlerCluster.categoriesWordsLock.acquire()
			
			title = item.get('articleTitle')
			
			body = item.get('articleBody')
			
			# Note they are lists
			if len(title):
				self.trainingCrawlerCluster.categoriesWords[category].append(title[0])
				
			if len(body):
				self.trainingCrawlerCluster.categoriesWords[category].append(body[0])
				
				
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
		
	def __CrawlSeed__(self):
		
		for host in self.newsHosts:
			
			domain = GetDomainName(host.url)
			algo = self.trainingCrawlerCluster.hostToCrawlerDict[domain]
			algo.Crawl(CrawlingOption.TrainingCrawl, domain, self.__SeedingCallBack__, self.categories)
		
		self.__FlushSeeds__()
		
				
	def Crawl(self):
		
		if self.enableCrawlSeeds:
			self.__CrawlSeed__()
			
		if self.enableCrawlPage:
			self.__ScrapeUrl__()
			
