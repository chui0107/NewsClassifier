import logging
from scrapy.item import Item, Field
from urlparse import urlparse
from scrapy.http import Request, HtmlResponse
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.contrib.linkextractors import LinkExtractor
from lxml.html.builder import TITLE, BODY
from NewsBase import CategoryOption

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
		
		self.start_urls = kw.get('urls')
		self.scraperCallBack = kw.get('scraperCallBack')
		self.category = kw.get('category')
		
		for i in range(len(self.start_urls)):
			if not self.start_urls[i].startswith('http://') and not self.start_urls[i].startswith('https://'):
				self.start_urls[i] = 'http://%s/' % self.start_urls[i]
		
		'''	
		self.allowed_domains = [re.sub(r'^www\.', '', urlparse(url).hostname)]
		
		self.link_extractor = LinkExtractor()
		
		self.cookies_seen = set()
		
		'''
				
	def __ExtractPath__(self, response):
		# print self.category
		if self.category == str(CategoryOption.business):
			title = Selector(response).xpath('//h1[@class="articleHeadline"]/text()').extract() or ''
			body = Selector(response).xpath('//div[@class="articleBody"]/p/text()').extract() or ''
			return (title, body)
		
		elif self.category == str(CategoryOption.sports) or self.category == str(CategoryOption.technology):
			title = Selector(response).xpath('//h1[@id="story-heading"]/text()').extract() or ''
			body = Selector(response).xpath('//div[@id="story-body"]/p/text()').extract() or ''
			return (title, body)
		
		logging.error('unknown category: %s', self.category)
		raise ValueError('unknown category')
	
	def __GetItem__(self, response):
		
		item = nyTimesPage()
		
		if isinstance(response, HtmlResponse):
			
			try:
				
				newsTuple = self.__ExtractPath__(response)
				
				item['articleTitle'] = newsTuple[0]
			
				item['articleBody'] = newsTuple[1]
				
			except ValueError:
				item['articleTitle'] = ''
			
				item['articleBody'] = ''
			
				
		return item
		
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

	# this is the default callback function when scraping finishes, it gets called
	def parse(self, response):
		
		item = self.__GetItem__(response)
		
		# delegate callback to the crawler
		self.scraperCallBack((self.category, item))
		
		# r.extend(self._extract_requests(response))
