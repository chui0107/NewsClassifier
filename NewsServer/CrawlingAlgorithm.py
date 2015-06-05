import requests
import abc

class CrawlingAlgorithm:
	def __init__(self, url, apiKey, docLink):
		self.url = url
		self.apiKey = apiKey
		self.docLink = docLink
		self.visitedUrl = set()
	
	@abc.abstractmethod
	def __FillCrawlerQ__(self, messageQueue, newTuple):
		return
	
	@abc.abstractmethod
	def Crawl(self):
		return
	

class NYtimesCrawlingAlgorithm(CrawlingAlgorithm):
	def __init__(self, url, apiKey, docLink):
		CrawlingAlgorithm.__init__(self, url, apiKey, docLink)
		self.timeout = 60
		
	def __FillCrawlerQ__(self, messageQueue, crawlerTuple):
		
		try:
			messageQueue.crawlerQLock.acquire()
					
			messageQueue.crawlerQ.append(crawlerTuple)
					
			messageQueue.crawlerQSema.release()
						
		finally:
			messageQueue.crawlerQLock.release()	
		
	def Crawl(self, messageQueue):
		
		import time
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
					
					
				
