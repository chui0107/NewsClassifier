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
	def __init__(self, newsHost):
		CrawlingAlgorithm.__init__(self, newsHost)
		
	def __Crawl__(self, page, action, category=None):
		
		'''
			{u'status': u'OK', u'response': {u'docs': [], u'meta': {u'hits': 0, u'offset': 0, u'time': 54}}, u'copyright': u'Copyright (c) 2013 The New York Times Company.  All Rights Reserved.'}
		'''
		responseFormat = '.json'
		sortOrder = 'newest'
		
		if category:
			params = {'fq': 'section_name:(' + category + ')', 'page': page, 'sort':sortOrder, 'api-key': self.apiKey}
		else:
			params = {'page': page, 'sort':sortOrder, 'api-key': self.apiKey}
			
		r = requests.get(self.url + responseFormat, params=params)
		
		if(category == 'entertainment'):
			print r.text
	
		if r.status_code != 200:
			print 'stop %s ' % category
			logging.error('Http request failed with %s ', r.text)
			return
		
		response = r.json()
		
		# pact news into a text
		for doc in response['response']['docs']:
			url = doc['web_url']	
			if not url in self.visitedUrl:
				newsTuple = (category, url)
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
			
	def Crawl(self, crawlingOption, action, crawlingParams=[]):
		
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
				print 'Crawling page %d' % page
				
				for category in crawlingParams:
					
					try:
						
						categoryString = self.__CategoryToCategoryString__(category) 
					
						print 'crawling %s category on nyTimes' % categoryString
					
						# crawl the nytimes section for training data
						self.__Crawl__(page, action, categoryString)
					
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
	
	def __init__(self, newsHost):
		CrawlingAlgorithm.__init__(self, newsHost)
		
	def Crawl(self, crawlingOption, action, categories=[]):
		
		if crawlingOption == CrawlingOption.TrainingCrawl:
			timeout = 1
		elif crawlingOption == CrawlingOption.RunningCrawl:
			timeout = 600
		
		while  True:
			
			for category in categories:
				
				print 'crawling %s category on USAToday' % category 
				# crawl 30 news for now
				responseFormat = 'json'
				
				params = {'section':category, 'count':100, 'encoding':responseFormat, 'api_key': self.apiKey}
				
				r = requests.get(self.url, params=params)
				
				if r.status_code != 200:
					print 'stop %s ' % r.text
				
				response = r.json()
				
				# pact news into a text
				for doc in response['stories']:
					text = ''
					if doc['title'] != None:
						text += doc['title'] + ' '
					
					if doc['description'] != None:						
						text += doc['description']
					
					if not doc['link'] in self.visitedUrl:
						
						if crawlingOption == CrawlingOption.TrainingCrawl:
							newsTuple = (category, text, doc['title'], doc['link'])
						else:
							newsTuple = (text, doc['title'], doc['link'])
						
						# print newsTuple	
						action(newsTuple)
						self.visitedUrl.add(doc['link'])
						
				# crawl every minute
				time.sleep(timeout)
				
			return		
				
