import re
from urlparse import urlparse

def GetDomainName(url):
	return re.sub(r'^www\.', '', urlparse(url).hostname)