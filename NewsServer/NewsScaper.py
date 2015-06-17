import logging
import abc
from scrapy.item import Item, Field
from scrapy.http import Request, HtmlResponse
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import Rule
from lxml.html.builder import TITLE, BODY
from NewsBase import CategoryOption
from Util import GetDomainName
import sys
import re

class Article(Item):
	articleTitle = Field()
	articleBody = Field()

# the pass in urls have to follow the same pattern to be scraped
class NewsScraper(Spider):
	name = 'NewsScraper'

	def __init__(self, **kw):
		super(NewsScraper, self).__init__(**kw)
		
	@abc.abstractmethod			
	def __ExtractPath__(self, response):
		pass
	
	def __GetItem__(self, response):
		
		item = Article()
		item['articleTitle'] = None	
		item['articleBody'] = None
		
		if isinstance(response, HtmlResponse):
			
			try:
				
				newsTuple = self.__ExtractPath__(response)
				item['articleTitle'] = newsTuple[0] 
				item['articleBody'] = newsTuple[1]
		
			except:
				item['articleTitle'] = None	
				item['articleBody'] = None
				logging.exception('%s.__GetItem__: exception', self.name)
		else:
			logging.info('%s.__GetItem__: response is not of type HtmlResponse', self.name)
					
		return item
	
	# this is the default callback function when scraping finishes, it gets called
	def parse(self, response):
		
		item = self.__GetItem__(response)
		
		# delegate callback to the crawler
		self.scraperCallBack(item)
		
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
			
			
		elif self.category == str(CategoryOption.sports) or self.category == str(CategoryOption.technology):
			title = Selector(response).xpath('//h1[@id="story-heading"]/text()').extract()
			body = Selector(response).xpath('//div[@id="story-body"]/p/text()').extract()
		
		else:
			logging.error('%s.__ExtractPath__: unknown category: %s', self.name, self.category)
			raise ValueError('unknown category')
		
		return (title, body)
			
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

# the crawler is used to crawler links on a page to feed seeds.txt	
class PageLinkScraper(NewsScraper):
	
	name = 'PageLinkScraper'
		
	def __init__(self, **kw):
		super(PageLinkScraper, self).__init__(**kw)
		
		# r.extend(self._extract_requests(response))
		
	def __ExtractLinks__(self, response):
		
		articleLinks = []
		if isinstance(response, HtmlResponse):
			try:
				domain = GetDomainName(response.url)
				# regex = '^https?://www.' + domain + '/.*-n(\d+)$'
				# regex = '^https?://www.' + domain + '/.*$'				
				links = LxmlLinkExtractor(allow=(), allow_domains=(domain,), restrict_xpaths=('//body',)).extract_links(response)
				
				# print links
				for link in links:
					# extract only links with text longer than 30, usually its an article
					if(len(link.text) > 30):
						articleLinks.append(link.url)
			except:
				logging.exception('%s.__ExtractLinks__: exception')
			
		logging.info('%s.__ExtractLinks__: non HtmlReponse response', self.name)
		return articleLinks
		
	def __GetItem__(self, response):
		
		item = None
		if isinstance(response, HtmlResponse):
			
			try:
				
				links = self.__ExtractLinks__(response)
				item = (self.category, GetDomainName(self.start_urls[0]), links)
				
			except:
				logging.exception('%s.__GetItem__: exception', self.name)
		else:
			logging.info('%s.__GetItem__: response is not of type HtmlResponse', self.name)
					
		return item	
