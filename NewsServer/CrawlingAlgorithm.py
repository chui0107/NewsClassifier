import requests
import abc
import time

class CrawlingAlgorithm:
	def __init__(self, newsHost):
		self.url = newsHost.url
		self.apiKey = newsHost.apiKey
		self.docLink = newsHost.docLink
		self.visitedUrl = set()
	
	def __FillCrawlerQ__(self, messageQueue, crawlerTuple):
		try:
			messageQueue.crawlerQLock.acquire()
					
			messageQueue.crawlerQ.append(crawlerTuple)
					
			messageQueue.crawlerQSema.release()
						
		finally:
			messageQueue.crawlerQLock.release()	
	
	
	@abc.abstractmethod
	def Crawl(self):
		return
	

class NYtimesCrawlingAlgorithm(CrawlingAlgorithm):
	def __init__(self, newsHost):
		CrawlingAlgorithm.__init__(self, newsHost)
		self.timeout = 600
			
	def Crawl(self, messageQueue):
		
		'''
			{u'status': u'OK', u'response': {u'docs': [], u'meta': {u'hits': 0, u'offset': 0, u'time': 54}}, u'copyright': u'Copyright (c) 2013 The New York Times Company.  All Rights Reserved.'}
		'''
		while  True:

			# crawl 30 news for now
			for page in range(3):
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
						text = text + doc['snippet'] + ' '
					if doc['lead_paragraph'] != None:
						text = text + doc['lead_paragraph'] + ' '
					if doc['abstract'] != None:
						text = text + doc['abstract'] + ' '
					if doc['headline'] != None and doc['headline']['main'] != None:
						text = text + doc['headline']['main']
					
					if not doc['web_url'] in self.visitedUrl:
						self.__FillCrawlerQ__(messageQueue, (text, doc['headline']['main'], doc['web_url']))
						self.visitedUrl.add(doc['web_url'])
			
			# crawl every minute
			time.sleep(self.timeout)
					
class USATodayCrawlingAlgorithm(CrawlingAlgorithm):
	def __init__(self, url, apiKey, docLink):
		CrawlingAlgorithm.__init__(self, url, apiKey, docLink)
		self.timeout = 600
		# no news older than 7 days 
		self.days = 7
		
	def Crawl(self, messageQueue):
		
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
					self.__FillCrawlerQ__(messageQueue, (text, doc['title'], doc['link']))
					self.visitedUrl.add(doc['link'])
				
			# crawl every minute
			time.sleep(self.timeout)
