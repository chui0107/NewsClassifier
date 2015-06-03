import requests
import threading

class NewsHost:
	def __init__(self, url, key, docLink):
		self.url = url
		self.apiKey = key
		self.docLink = docLink
		
class CrawlerQueue:
	def __init__(self):
		import collections
		# NOTE that collections.deque() is thread-safe
		# https://docs.python.org/2/library/collections.html#collections.deque
		self.messageQ = collections.deque()
		self.messageQFillSema = threading.Semaphore()
		self.messageQEmptySema = threading.Semaphore()
		self.messageQSema = threading.Semaphore(0)
		self.messageQLock = threading.Lock()
		
class CrawlerThread(threading.Thread):
		
		def __init__(self, url, key, crawlerQueue):
			threading.Thread.__init__(self)
			self.url = url
			self.key = key
			self.crawlerQueue = crawlerQueue
			
		def run(self):
			
			'''
			{u'status': u'OK', u'response': {u'docs': [], u'meta': {u'hits': 0, u'offset': 0, u'time': 54}}, u'copyright': u'Copyright (c) 2013 The New York Times Company.  All Rights Reserved.'}
		
			'''
			
			apiKey = self.key
			
			keyword = 'business'
			
			responseFormat = '.json'
			
			filterQuery = 'subject:(' + keyword + ')'
			
			page = 0
			
			params = {'fq': filterQuery, 'page': page, 'api-key': apiKey}
			
			r = requests.get(self.url + responseFormat, params=params)
			
			response = r.json()
			
			if response == None:
				return
			
			status = response['status']
			
			if(status.lower() == 'ok'):
				
				docs = response['response']['docs']
				text = ''
				
				# pact news into a text
				for doc in docs:	
					if doc['snippet'] != None:						
						text = text + doc['snippet'] + ' '
					if doc['lead_paragraph'] != None:
						text = text + doc['lead_paragraph'] + ' '
					if doc['abstract'] != None:
						text = text + doc['abstract'] + ' '
					if doc['headline'] != None and doc['headline']['main'] != None:
						text = text + doc['headline']['main']
					
					try:
						self.crawlerQueue.messageQLock.acquire()
						
						self.crawlerQueue.messageQ.append((text, doc['headline']['main'], doc['web_url']))
					
						self.crawlerQueue.messageQSema.release()
						
					finally:
						self.crawlerQueue.messageQLock.release()
					
class NewsCrawler:
			
	def __init__(self, crawlerQueue):
		self.crawlerQueue = crawlerQueue
		self.hostDict = {}
					
	def AddHost(self, host):
		self.hostDict[host.url] = host.apiKey
			
	def Crawl(self):
			
		self.crawlingThreads = []
	
		for url in self.hostDict:
			self.crawlingThreads.append(CrawlerThread(url, self.hostDict[url], self.crawlerQueue))
			self.crawlingThreads[len(self.crawlingThreads) - 1].start()
		
	def GetCrawlerThreads(self):
		return self.crawlingThreads	
