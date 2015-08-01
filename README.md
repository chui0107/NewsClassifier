# NewsClassifier
To Run:
	Go to the newsServer folder and run python NewsServer.py, where the starting point of the program is
	
Problem with running the program on linode:

1. python2.7 NewsServer returns error => ImportError: /usr/local/lib/python2.7/site-packages/lxml/etree.so: undefined symbol: __xmlStructuredErrorContext

2. libxslt can't be compiled anymore for some reason, and its rpm can't be installed due to dependency issue

TODO:

1.probably try to add some updated repositories and yum update the system to see if it solves the dependencies issue

2.uninstall the compiled python2.7 and reinstall it through updated repository from http://wiki.centos.org/AdditionalResources/Repositories

3. try others
 

NOTEs:
2. python2.7 is compiled from source and installed under /usr/local

3. pip is installed with get-pip.py

4. libxlst is compiled from source under /usr/local/lib

5. libxml2 is compiled from source under /usr/lib

6. yum install libxslt-devel is with package manager but clearly out of date

7. http://xmlsoft.org/sources/ is the source for libxlst and libxml2

8. scrapy http://doc.scrapy.org/en/latest/intro/install.html#pre-requisites

