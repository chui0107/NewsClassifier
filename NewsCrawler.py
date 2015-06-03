import requests
import threading

class NewsHost:
    
    def __init__(self,url,key,docLink):
        self.url = url
        self.apiKey = key
        self.docLink = docLink

class NewsCrawler:
    
    def __init__(self):
        
        self.hostDict = {}
            
    def __SaveNewsInArchive__(self,path):
        return
    
    def AddHost(self,host):
        
        url = host.url
        key = host.apiKey
        
        self.hostDict[url] = key
        
    def Crawl(self):
        
        import re
        
        '''
        
        {u'status': u'OK', u'response': {u'docs': [], u'meta': {u'hits': 0, u'offset': 0, u'time': 54}}, u'copyright': u'Copyright (c) 2013 The New York Times Company.  All Rights Reserved.'}
        
        '''
        articles = []
        
        for url in self.hostDict:
            
            apiKey = self.hostDict[url]
            
            keyword = 'business'
            
            responseFormat = '.json'
            
            filterQuery = 'subject:(' + keyword +  ')'
            
            page = 0
            
            params = {'fq': filterQuery,'page': page,'api-key': apiKey}
            
            r = requests.get(url + responseFormat, params = params)
            
            response = r.json()
            
            if response == None:
                continue
            
            status = response['status']
            
            if(status.lower() == 'ok'):
                
                docs = response['response']['docs']
                text = ''
                
                #pact news into a text
                for doc in docs:    
                    if doc['snippet'] != None:                        
                        text = text + doc['snippet'] + ' '
                    if doc['lead_paragraph'] != None:
                        text = text + doc['lead_paragraph'] + ' '
                    if doc['abstract'] != None:
                        text = text + doc['abstract'] + ' '
                    if doc['headline'] != None and doc['headline']['main'] != None:
                        text = text + doc['headline']['main']
                    
                    articles.append(text)
                    
        return articles
        