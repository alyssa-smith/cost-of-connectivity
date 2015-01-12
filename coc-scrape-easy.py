import mechanize
import urllib2, urllib, re
from mechanize._opener import urlopen
from mechanize._form import ParseResponse
from bs4 import BeautifulSoup
from selenium import webdriver
import os

#easy to scrape: time warner, google fiber, istep, lmi, comcast, lus fiber

zipCodes = {}
zipCodes['dc'] = 20036

def scrape_time_warner(city):
    
    #PARAMETERS THAT MIGHT CHANGE:
    
    webAddress = 'http://www.timewarnercable.com/en/plans-packages/internet/internet-service-plans.html'
    zipCode = zipCodes[city]
    
    #br = mechanize.Browser()
    #respstr =  br.open(webAddress).read()
   #respstr = urllib2.urlopen(webAddress).read()
   # print re.findall('class="[a-zA-Z ]+"', respstr)
    
    #print BeautifulSoup(urllib2.urlopen(webAddress))
    #form_data = {'geolocation':10001}
    #br = mechanize.Browser()
    #br.open(urllib2.urlopen(webAddress,urllib.urlencode(form_data)))
   # response = BeautifulSoup(urllib2.urlopen(webAddress,urllib.urlencode(form_data)).read())
   # print str(response)
   # print re.findall('<span class="dollars">[0-9]+</span>', respstr)
   # with open('coc-test.html', 'w') as f:
       # f.write(respstr)
       # f.close()
    
    #chromedriver = "/Users/serenity/Applications/chromedriver"
    #os.environ["webdriver.chrome.driver"] = chromedriver
    browser = webdriver.Chrome()
    browser.get(webAddress)
    #browser.quit()
    #elem = browser.find_element_by_name('geolocation')
    #elem.send_keys(zipCode + Keys.RETURN)
    
    
   # except:
        #print webAddress
        #print 'may be out of date or otherwise not working. check to see if it opens in your browser.'
        #print "if it doesn't work in your browser either, you may need to update the link and possibly also the scraping technique."
    


scrape_time_warner('dc')

def scrape_google_fiber(city):
    webAddress = 