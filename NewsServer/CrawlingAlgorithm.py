import requests

class CrawlingAlgorithm:
	def __init__(self, url, apiKey, docLink):
		self.url = url
		self.apiKey = apiKey
		self.docLink = docLink

	def __FillCrawlerQ__(self, messageQueue, newTuple):
		return
	
	def Crawl(self):
		return
	

class NYtimesCrawlingAlgorithm(CrawlingAlgorithm):
	def __init__(self, url, apiKey, docLink):
		CrawlingAlgorithm.__init__(self, url, apiKey, docLink)
		
	def __FillCrawlerQ__(self, messageQueue, crawlerTuple):
		
		try:
			messageQueue.crawlerQLock.acquire()
					
			messageQueue.crawlerQ.append(crawlerTuple)
					
			messageQueue.crawlerQSema.release()
						
		finally:
			messageQueue.crawlerQLock.release()	
		
	def Crawl(self, messageQueue):
		
		'''
			{u'status': u'OK', u'response': {u'docs': [], u'meta': {u'hits': 0, u'offset': 0, u'time': 54}}, u'copyright': u'Copyright (c) 2013 The New York Times Company.  All Rights Reserved.'}
		'''		
		responseFormat = '.json'
		sortOrder = 'newest'
		# filterQuery = 'subject:(business)'						
		page = 0
		# params = {'fq': filterQuery, 'page': page, 'sort':sortOrder, 'api-key': apiKey}
		
		params = {'page': page, 'sort':sortOrder, 'api-key': self.apiKey}
			
		r = requests.get(self.url + responseFormat, params=params)
		
		if r.status_code != 200:			
			return
			
		response = r.json()
						
		text = ''
				
		# pact news into a text
		for doc in response['response']['docs']:	
			if doc['snippet'] != None:						
				text = text + doc['snippet'] + ' '
			if doc['lead_paragraph'] != None:
				text = text + doc['lead_paragraph'] + ' '
			if doc['abstract'] != None:
				text = text + doc['abstract'] + ' '
			if doc['headline'] != None and doc['headline']['main'] != None:
				text = text + doc['headline']['main']		
			
			self.__FillCrawlerQ__(messageQueue, (text, doc['headline']['main'], doc['web_url']))	
			
		
