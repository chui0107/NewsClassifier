import requests
import abc
import time
from enum import Enum
import logging
from NewsBase import CategoryOption
from distutils.tests.setuptools_build_ext import if_dl

class CrawlingOption(Enum):
	TrainingCrawl = 1
	RunningCrawl = 2
	
class CrawlingAlgorithm:
	def __init__(self, newsHost):
		self.url = newsHost.url
		self.apiKey = newsHost.apiKey
		self.docLink = newsHost.docLink
		self.visitedUrl = set()
	
	@abc.abstractmethod
	def Crawl(self, crawlingOption, action, crawlingParams=[]):
		pass
	
	@abc.abstractmethod
	def __CategoryToCategoryString__(self, categoryOption):
		pass
	

class NYtimesCrawlingAlgorithm(CrawlingAlgorithm):
	
	className = 'NYtimesCrawlingAlgorithm'
	
	def __init__(self, newsHost):
		CrawlingAlgorithm.__init__(self, newsHost)
		
	def __Crawl__(self, page, domain, action, category=None):
		
		'''
			{u'status': u'OK', u'response': {u'docs': [], u'meta': {u'hits': 0, u'offset': 0, u'time': 54}}, u'copyright': u'Copyright (c) 2013 The New York Times Company.  All Rights Reserved.'}
		'''
		responseFormat = '.json'
		sortOrder = 'newest'
		
		try:
			categoryString = self.__CategoryToCategoryString__(category)
			
		except ValueError:
			
			logging.error('%s.__Crawl__: unknown category', self.className)
			return
		
		if category:
			params = {'fq': 'section_name:(' + categoryString + ')', 'page': page, 'sort':sortOrder, 'api-key': self.apiKey}
		else:
			params = {'page': page, 'sort':sortOrder, 'api-key': self.apiKey}
			
		try:
			r = requests.get(self.url + responseFormat, params=params)
		
			if r.status_code != 200:
				logging.error('%s.__Crawl__: %s', r)
				return
		
			response = r.json()
			
		except:
			logging.exception('%s.__Crawl__: exception')
			return
		
		# pact news into a tuple
		if response['response'] == None:
			logging.error('%s.__Crawl__: response doesn\'t exist', self.className)
			return;
		
		if response['response']['docs'] == None:
			logging.error('%s.__Crawl__: docs doesn\'t exist', self.className)
			return;
		
		for doc in response['response']['docs']:
			url = doc.get('web_url')
			if url and url not in self.visitedUrl:
				newsTuple = (category, domain, url)
				action(newsTuple)
				self.visitedUrl.add(url)
	
	def __CategoryToCategoryString__(self, categoryOption):
		if categoryOption == CategoryOption.business:
			return 'business'
		elif categoryOption == CategoryOption.technology:
			return 'technology'
		elif categoryOption == CategoryOption.sports:
			return 'sports'
		logging.error('unknown categoryOpntion %s', categoryOption)
		raise ValueError('unknown category') 
			
	def Crawl(self, crawlingOption, domain, action, crawlingParams=[]):
		
		if crawlingOption == CrawlingOption.TrainingCrawl:
			page = 0
			# nytimes only allows 10 pages per second
			nPages = 100
			timeout = 1
		elif crawlingOption == CrawlingOption.RunningCrawl:
			nPages = 3
			timeout = 600
		
		while True:
			
			if crawlingOption == CrawlingOption.TrainingCrawl:
				print 'crawling page %d' % page
				
				for category in crawlingParams:
					
					try:
						
						print 'crawling %s seeds on nyTimes' % category
						
						# crawl the nytimes section for training data
						self.__Crawl__(page, domain, action, category)
					
					except ValueError:
						logging.error('unkownn category')
						
					
				if page == nPages:
					logging.info('finished with all %d pages', page)
					break
				
				if (len(crawlingParams) >= 9):
					time.sleep(timeout)
				else:
					time.sleep(timeout / 2.0)
								
			elif crawlingOption == CrawlingOption.RunningCrawl:
				for page in range(nPages):
					self.__Crawl__(page, action)
					
				time.sleep(timeout)
						
			page += 1

					
class USATodayCrawlingAlgorithm(CrawlingAlgorithm):
	
	className = 'USATodayCrawlingAlgorithm'
	
	def __init__(self, newsHost):
		CrawlingAlgorithm.__init__(self, newsHost)
	
	def __CategoryToCategoryString__(self, categoryOption):
		if categoryOption == CategoryOption.business:
			return 'business'
		elif categoryOption == CategoryOption.technology:
			return 'tech'
		elif categoryOption == CategoryOption.sports:
			return 'sports'
		
		logging.error('%s.__CategoryToCategoryString__: unknown categoryOpntion %s', self.className, categoryOption)
		raise ValueError('unknown category') 
		
	def __Crawl__(self, domain, action, category=None):
		
		responseFormat = 'json'
		
		try:
			categoryString = self.__CategoryToCategoryString__(category)
			
		except:
			logging.exception('%s.__Crawl__: exception', self.className)
			return
		
		params = {'section':categoryString, 'count':200, 'encoding':responseFormat, 'api_key': self.apiKey}
		
		try:
			r = requests.get(self.url, params=params)
		
			if r.status_code != 200:
				logging.error('%s.__Crawl__:%s', self.className, r)
				return
		
			response = r.json()
			
		except:
			logging.exception('%s.__Crawl__: exception')
			return

		# pact news into a tuple
		for doc in response.get('stories'):
			url = doc.get('link')
			if url and url not in self.visitedUrl:
				newsTuple = (category, domain, url)
				action(newsTuple)
				self.visitedUrl.add(url)
		
	def Crawl(self, crawlingOption, domain, action, categories=[]):
		
		if crawlingOption == CrawlingOption.TrainingCrawl:
			timeout = 1
		elif crawlingOption == CrawlingOption.RunningCrawl:
			timeout = 600
		
		while True:
			
			if crawlingOption == CrawlingOption.TrainingCrawl:
				
				for category in categories:
					
					print 'crawling %s category on USAToday' % category
				
					# crawl the nytimes section for training data
					self.__Crawl__(domain, action, category)
					
					time.sleep(timeout)
						
				break
			
			elif crawlingOption == CrawlingOption.RunningCrawl:
				time.sleep(timeout)
				
