import os
import json
import re
from NewsCrawler import NewsCrawler
from NewsCrawler import NewsHost

class NaiveBayes:
    
    def __init__(self,path):
        self.Train(path)
                
    def __Tokenize__(self,news):
        
        text = ''
        
        for eachnews in news:
            
            title = eachnews[1]
        
            description = eachnews[2]
        
            text += title + description
        
        return re.findall('[a-z]+', text.lower())
    
    def __TokenizeText__(self,text):
        return re.findall('[a-z]+', text.lower())
    
    def __PopulateClass__(self,className,words):
        
        classes = self.vocabulary[0]
        
        classes[className] = []
        
        wordCount = {}
        wordSize = 0
        
        for word in words:
            if word in wordCount:
                wordCount[word] = wordCount[word] + 1
            else:
                wordCount[word] = 1
                wordSize = wordSize + 1
                        
        classes[className].append(wordCount)
        classes[className].append(wordSize)
    
    def __ComputeClass__(self,words):
        
        import math
        
        classes = self.vocabulary[0]
        vocabularySize = self.vocabulary[1]
        
        classMaxProb = -float("inf");
        className = ''
        
        for classKey in classes:
            
            classTuple = classes[classKey]
            classDict = classTuple[0]
            classWordSize = classTuple[1]
            classPrior = classTuple[2]
            denominator = classWordSize + vocabularySize
            classProb = 0.0
            
            #bag of words model
            for word in words:
                
                #add one smoothing
                wordProb = 1.0 / denominator
                
                if word in classDict:    
                    wordProb = wordProb + float(classDict[word]) / denominator
                
                #use log arithmetic to avoid multiplication overflow
                classProb = classProb + math.log(wordProb)
                    
            classProb = classProb * classPrior
            #choose the class with max probablity
            if classProb > classMaxProb:
                classMaxProb = classProb
                className = classKey
        
        return className
            
    def Train(self,path):
        
        self.vocabulary = []
        self.vocabulary.append({})
        
        for eachClass in os.listdir(path):
            
            fileName = eachClass.lower()
                
            #class file 
            extension = fileName[len(fileName) - 4:]
            if extension != '.txt':
                continue
                
            className = fileName[:len(fileName) - 4]
                
            with open(path + eachClass,'r') as f:
                    
                news = json.load(f)
                    
                words = self.__Tokenize__(news)
                
                self.__PopulateClass__(className,words)
                    
        #populate prior probabilities
        classes = self.vocabulary[0]
        totolWords = 0
        
        for eachClass in classes:
            
            eachClassPriorProbability = 1.0 / len(classes)
            
            classes[eachClass].append(eachClassPriorProbability)
            
            #populate total words
            wordInEachClass = classes[eachClass][1]
            totolWords = totolWords + wordInEachClass
            
        self.vocabulary.append(totolWords)
        
    def Classify(self,path):
        
        for fileName in os.listdir(path):
            
            #class file 
            extension = fileName[len(fileName) - 4:]
            if extension != '.txt':
                continue
                
            with open(path + fileName,'r') as f:
                    
                news = json.load(f)
                    
                words = self.__Tokenize__(news)
                                
                className = self.__ComputeClass__(words)
                
                print '%s has been classified as %s\n' % (fileName,className)
                
    
    def Classify(self,text):
        
        words = self.__TokenizeText__(text)
        
        className = self.__ComputeClass__(words)
            
def GetCommondLineInput():
    
    import readline
    import shlex
    
    print 'Enter a subject of news to browse'
    print 'To get help, enter `help`.'
    
    subjects = frozenset(['business','politics','entertainment'])
    
    while True:
        
        inputs = shlex.split(raw_input('Subject: '))
        if len(inputs) != 1:
            print 'Only support 1 input at this time'
            continue
            
        cmd = inputs[0].lower()
        
        if cmd in subjects:
            print 'in'
            continue;
                        
        if cmd == 'exit':
            break

        elif cmd == 'help':
            print 'To be added'
    
        else:
            print('Unknown command: {}'.format(cmd))         
                
def main():
                
    curPath = os.getcwd()
    
    trainingSetPath = curPath + '/TrainingSet/'
    
    testSetPath = curPath + '/TestSet/'
    
    naiveBayes = NaiveBayes(trainingSetPath)
    
    GetCommondLineInput()
    
    newsCrawler = NewsCrawler()
    
    nyTimes = NewsHost('http://api.nytimes.com/svc/search/v2/articlesearch','f01308a5d8db23dd5722469be240a909:14:67324777', 'http://developer.nytimes.com/docs/read/article_search_api_v2')
    
    newsCrawler.AddHost(nyTimes)
    
    articles = newsCrawler.Crawl()
    
    #for article in articles:
        #naiveBayes.Classify(article)
    
if __name__ == "__main__":
    main()        