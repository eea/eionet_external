# URLSuck(url,timeout=2.5):
# Return page content from url and 
# wait for a specific amount of seconds (timeout).
# We could say that this is a multi-threaded version of urllib2.urlopen(url).
# by
# Antonio De Marinis
# antonio.de.marinis@eea.eu.int
#
# Library mainly made for getting a Report
# from Cocoon and a glossary box
# from glossary.eea.eu.int
# ver 1.3 with threads

import urllib2
from urllib import quote_plus
from threading import Thread
from threading import Event

def URLEncodedFormat(s):
    return quote_plus(s)

def URLSuck(url,timeout=2.5):
    msg=Event() # Event used to get notification from URLSucker
    US=URLSucker(url,msg)
    US.setName('URLSuckerThread')
    US.setDaemon(1) # The URLSucker is a daemonic thread, main thread doesn't wait for it.
    US.start()
    msg.wait(timeout) # we wait timeout seconds for the URLSucker to finish
    if US.isAlive():
        return '' # here we could also log which url took so long time or wait more
    else:
        if US.getURLContent() != '':
            return 'OK'
    return ''

class URLSucker(Thread):
     URLContent=''
     notification=None
     url=''

     def __init__(self,url,msg):
       Thread.__init__(self)
       self.notification=msg
       self.url=url

     def setURL(self,url):
          self.url=url

     def setEvent(self,msg):
          self.notification=msg

     def run(self):
          self.notification.clear() # Stop signal, the parent thread waits
          self.suckURL(self.url)
          self.notification.set() # URL sucked, notify the parent thread
           
     def suckURL(self,url):
          try:
           fd = urllib2.urlopen(url) #try to retrieve the url
           self.URLContent = fd.read()
           fd.close()
          except urllib2.HTTPError, errorinfo:
              if errorinfo.code < 400 or errorinfo.code >= 500: # Code 5XX is ok
	          self.URLContent = 'OK'
              else:
                  self.URLContent = ''
          except:
              self.URLContent = ''

     def getURLContent(self):
          return self.URLContent
     
import unittest
class TestSuck(unittest.TestCase):
    def testSuck(self):
        self.assertEqual(URLSuck('http://www.ekpaa.gr/documents/NCESD-GR-State_of_the_Environment.pdf'),'')
        self.assertEqual(URLSuck('http://www.eionet.europa.eu'),'OK')
        self.assertEqual(URLSuck('http://www.scotland.gov.uk/Home'),'OK')
        self.assertEqual(URLSuck('http://'),'')
        self.assertEqual(URLSuck('http://www.nosuchthingy.dk'),'')


if __name__ == "__main__":
    unittest.main()
