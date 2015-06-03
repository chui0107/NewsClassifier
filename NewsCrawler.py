import requests
import threading
from numpy.f2py.rules import typedef_need_dict

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
					
					self.crawlerQueue.messageQ.append((text, doc['headline']['main'], doc['web_url']))	 	

class NewsCrawler:
			
	def __init__(self, crawlerQueue):
		self.crawlerQueue = crawlerQueue
		self.hostDict = {}
					
	def AddHost(self, host):
		self.hostDict[host.url] = host.apiKey
			
	def Crawl(self):
			
		crawlingThreads = []
	
		for url in self.hostDict:
			crawlingThreads.append(CrawlerThread(url, self.hostDict[url], self.crawlerQueue))
			crawlingThreads[len(crawlingThreads) - 1].start()
		
		for crawlingThread in crawlingThreads:
			crawlingThread.join()
		
	
