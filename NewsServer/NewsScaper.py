import re
from scrapy.item import Item, Field
from urlparse import urlparse
from scrapy.http import Request, HtmlResponse
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.contrib.linkextractors import LinkExtractor

class nyTimesPage(Item):
	articleTitle = Field()
	articleBody = Field()

class NewsScraper(Spider):
	name = 'NewsScraper'

	def __init__(self, **kw):
		super(NewsScraper, self).__init__(**kw)
		
class NYTimesScraper(NewsScraper):
	name = 'nyTimesScraper'

	def __init__(self, **kw):
		super(NewsScraper, self).__init__(**kw)
		
		self.trainingSetPath = kw.get('trainingSetPath')
		
		self.__FillStartUrls__()
		
		'''
		if not url.startswith('http://') and not url.startswith('https://'):
			url = 'http://%s/' % url
			
		self.url = url
		self.allowed_domains = [re.sub(r'^www\.', '', urlparse(url).hostname)]
		
		self.link_extractor = LinkExtractor()
		
		self.cookies_seen = set()
		
		'''
	def __FillStartUrls__(self):
		import ast
		import os
		
		for eachClass in os.listdir(self.trainingSetPath):
			
			fileName = eachClass.lower()
				
			# class file 
			extension = fileName[-4:]
			
			if extension != '.txt':
				continue
				
			self.className = fileName[:-4]
			
			with open(self.trainingSetPath + eachClass, 'r') as f:
					
				text = f.read()
				
				self.start_urls = ast.literal_eval(text)
			
				return
	
	def __GetItem__(self, response):
		
		item = nyTimesPage()
						
		if isinstance(response, HtmlResponse):
			
			title = Selector(response).xpath('//h1[@class="articleHeadline"]/text()').extract()
			if title:
				item['articleTitle'] = title[0]
			
			body = Selector(response).xpath('//div[@class="articleBody"]/p/text()').extract()
			if body:
				item['articleBody'] = body
		
	def _extract_requests(self, response):
		r = []
		if isinstance(response, HtmlResponse):
			links = self.link_extractor.extract_links(response)
			r.extend(Request(x.url, callback=self.parse) for x in links)
		return r

	'''
	def _set_new_cookies(self, page, response):
		cookies = []
		for cookie in [x.split(';', 1)[0] for x in response.headers.getlist('Set-Cookie')]:
			if cookie not in self.cookies_seen:
				self.cookies_seen.add(cookie)
				cookies.append(cookie)
		if cookies:
			page['newcookies'] = cookies
	
	def start_requests(self):
		return [Request(self.url, callback=self.parse, dont_filter=True)]
		
	'''

	def parse(self, response):
		
		self.__GetItem__(response)
		
		# r.extend(self._extract_requests(response))

