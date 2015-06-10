import requests
import abc
import time
from enum import Enum
import logging
from unicodedata import category

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
		return
	

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
			text = ''	
			if doc['snippet'] != None:						
				text += doc['snippet'] + ' '
			if doc['lead_paragraph'] != None:
				text += doc['lead_paragraph'] + ' '
			if doc['abstract'] != None:
				text += doc['abstract'] + ' '
			if doc['headline'] != None and doc['headline']['main'] != None:
				text += doc['headline']['main']
			
			if not doc['web_url'] in self.visitedUrl:
				self.visitedUrl.add(doc['web_url'])
				if category:
					newsTuple = (category, text, doc['headline']['main'], doc['web_url'])
				else:
					newsTuple = (text, doc['headline']['main'], doc['web_url'])
				action(newsTuple)
			
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
					print 'crawling %s category on USAToday' % category
					# crawl the nytimes section for training data
					self.__Crawl__(page, action, category)
					
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
				