import requests
import abc
import time
from enum import Enum

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
	def Crawl(self, crawlingOption, action):
		return
	

class NYtimesCrawlingAlgorithm(CrawlingAlgorithm):
	def __init__(self, newsHost):
		CrawlingAlgorithm.__init__(self, newsHost)
			
	def Crawl(self, crawlingOption, action):
		
		if crawlingOption == CrawlingOption.TrainingCrawl:
			self.nPages = 10
		elif crawlingOption == CrawlingOption.RunningCrawl:
			self.nPages = 10
			self.timeout = 600
			
		'''
			{u'status': u'OK', u'response': {u'docs': [], u'meta': {u'hits': 0, u'offset': 0, u'time': 54}}, u'copyright': u'Copyright (c) 2013 The New York Times Company.  All Rights Reserved.'}
		'''
		while  True:

			# crawl 30 news for now
			for page in range(self.nPages):
				responseFormat = '.json'
				sortOrder = 'newest'
				# filterQuery = 'subject:(business)'						
				# params = {'fq': filterQuery, 'page': page, 'sort':sortOrder, 'api-key': apiKey}
			
				params = {'page': page, 'sort':sortOrder, 'api-key': self.apiKey}
				
				r = requests.get(self.url + responseFormat, params=params)
			
				if r.status_code != 200:
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
						
						if crawlingOption == CrawlingOption.TrainingCrawl:
							action()
						elif crawlingOption == CrawlingOption.RunningCrawl:
							action((text, doc['headline']['main'], doc['web_url']))
						
			# crawl every minute
			time.sleep(self.timeout)
					
class USATodayCrawlingAlgorithm(CrawlingAlgorithm):
	
	def __init__(self, newsHost):
		CrawlingAlgorithm.__init__(self, newsHost)
		self.timeout = 600
		# no news older than 7 days 
		self.days = 7
		
	def Crawl(self, crawlingOption, action):
		
		while  True:
			
			# crawl 30 news for now
			responseFormat = 'json'
			
			params = {'days': self.days, 'count':30, 'encoding':responseFormat, 'api_key': self.apiKey}
			
			r = requests.get(self.url, params=params)
			
			if r.status_code != 200:
				return
			
			response = r.json()
			
			# pact news into a text
			for doc in response['stories']:
				text = ''
				if doc['title'] != None:
					text += doc['title'] + ' '
				
				if doc['description'] != None:						
					text += doc['description']
				
				if not doc['link'] in self.visitedUrl:
					self.visitedUrl.add(doc['link'])
					# self.__FillCrawlerQ__(messageQueue, (text, doc['title'], doc['link']))
				
			# crawl every minute
			time.sleep(self.timeout)
