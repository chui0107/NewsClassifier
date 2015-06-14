import logging
import abc
from scrapy.item import Item, Field
from scrapy.http import Request, HtmlResponse
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.contrib.linkextractors import LinkExtractor
from lxml.html.builder import TITLE, BODY
from NewsBase import CategoryOption
import sys

class articlePage(Item):
	articleTitle = Field()
	articleBody = Field()

class NewsScraper(Spider):
	name = 'NewsScraper'

	def __init__(self, **kw):
		super(NewsScraper, self).__init__(**kw)
		
	@abc.abstractmethod			
	def __ExtractPath__(self, response):
		pass
	
	def __GetItem__(self, response):
		
		item = articlePage()
		item['articleTitle'] = None	
		item['articleBody'] = None
		
		if isinstance(response, HtmlResponse):
			
			try:
				
				newsTuple = self.__ExtractPath__(response)
				
				if len(newsTuple[0]):
					item['articleTitle'] = newsTuple[0][0] 
				
				if len(newsTuple[1]):
					item['articleBody'] = newsTuple[1][0]
		
			except:
				item['articleTitle'] = None	
				item['articleBody'] = None
				logging.exception('%s.__GetItem__: exception', self.name)
		else:
			logging.info('%s.__GetItem__: reponse is not of type HtmlResponse', self.name)
					
		return item
	
	# this is the default callback function when scraping finishes, it gets called
	def parse(self, response):
		
		item = self.__GetItem__(response)
		
		# delegate callback to the crawler
		self.scraperCallBack(self.category, item)
		
		# r.extend(self._extract_requests(response))
		
	def SetUrls(self, urls):
		self.start_urls = urls
		for i in range(len(self.start_urls)):
			if not self.start_urls[i].startswith('http://') and not self.start_urls[i].startswith('https://'):
				self.start_urls[i] = 'http://%s/' % self.start_urls[i]
	
	
	def SetCategory(self, category):
		self.category = category
		
	def SetScraperCallBack(self, callBack):
		self.scraperCallBack = callBack
		
class USATodayScraper(NewsScraper):
	name = 'USATodayScraper'
	
	def __init__(self, **kw):
		super(USATodayScraper, self).__init__(**kw)
	
	def __ExtractPath__(self, response):
		
		# NOTE that the xpath selector returns a list
		# articles layout are similar among all categories on USAtoday
		if self.category == str(CategoryOption.business) or self.category == str(CategoryOption.sports) or self.category == str(CategoryOption.technology):
			
			title = Selector(response).xpath('//h1[@itemprop="headline"]/text()').extract()
			body = Selector(response).xpath('//div[@itemprop="articleBody"]/p/text()').extract()
			
			return (title, body)
		
		logging.error('%s.__ExtractPath__: unknown category: %s', self.name, self.category)
		raise ValueError('unknown category')
		
		
class NYTimesScraper(NewsScraper):
	name = 'nyTimesScraper'

	def __init__(self, **kw):
		super(NYTimesScraper, self).__init__(**kw)
		
		'''	
		self.allowed_domains = [re.sub(r'^www\.', '', urlparse(url).hostname)]
		
		self.link_extractor = LinkExtractor()
		
		self.cookies_seen = set()
		
		'''
				
	def __ExtractPath__(self, response):
		
		# NOTE that the xpath selector returns a list
		if self.category == str(CategoryOption.business):
			title = Selector(response).xpath('//h1[@class="articleHeadline"]/text()').extract()
			body = Selector(response).xpath('//div[@class="articleBody"]/p/text()').extract()
			return (title, body)
		
		elif self.category == str(CategoryOption.sports) or self.category == str(CategoryOption.technology):
			title = Selector(response).xpath('//h1[@id="story-heading"]/text()').extract()
			body = Selector(response).xpath('//div[@id="story-body"]/p/text()').extract()
			return (title, body)
		
		logging.error('%s.__ExtractPath__: unknown category: %s', self.name, self.category)
		raise ValueError('unknown category')
			
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
