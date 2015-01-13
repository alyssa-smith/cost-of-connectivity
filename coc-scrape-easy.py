import mechanize
import urllib2, urllib, re
from mechanize._opener import urlopen
from mechanize._form import ParseResponse
from bs4 import BeautifulSoup
from selenium import webdriver
import os, datetime
import pandas as pd

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
    #<div class="feature-table">.+<div class="feature-detail">

def scrape_google_fiber():
    
    webAddress = 'https://fiber.google.com/cities/kansascity/plans/'
    capping = re.findall('[A-Za-z]+ data caps', urllib2.urlopen(webAddress).read())
    #print capping
    noCaps = True
    for i in capping:
        #print i
        #print i=="No data caps"
        if i!= "No data caps":
            noCaps = False
            print "Google changed their data cap policy!"
            
    monthlyCosts = []
    setupFees = []
    for m in re.findall('div class="pricing-table widget".{2000}', re.sub('\n', '', urllib2.urlopen(webAddress).read())):
        for t in re.findall('\<p\>[/A-Z a-z0-9\&;\$()\<\>="\*+]+', m):
            if re.findall('.span class="strikethrough".\$[0-9]+./span. construction fee', t) != []:
                setupFees.append('none')
            else:
                t = re.sub('.span class="strikethrough".\$[0-9]+./span. construction fee|.span class="c2".|\<[a-z]\>|\<\/[a-z]\>  +','', t)
                setupFees.append( re.findall('[ a-zA-Z\$0-9/()]+\<', t))
            #print
        plans = {}
        planList = []
        for q in re.findall('h3 class="blue". +\$[0-9]+\/mo', m):
            monthlyCosts.append(re.sub('h3 class="blue"|  +|\>|\<', '', q))
        for n in re.findall('data-plan-id="[a-zA-Z+-]+"', m):
            plans[(re.sub('data-plan-id="|"', '', n))] = {}
            planList.append(re.sub('data-plan-id="|"', '', n))
    #print setupFees
   # print plans
    bobbyTables = re.findall('div class="feature-table".{2000}', re.sub('\n', '', urllib2.urlopen(webAddress).read()))
    #print len(bobbyTables)
    featureList = []
    speedList = []
    for r in re.findall('\<p\>[A-Za-z 0-9\-&();,]+', bobbyTables[0]):
        r = re.sub('\<p\>|  +', '', r)
        r = re.sub('&amp;', 'and', r)
        speedList.append(r)
    s = 0
    for plan in planList:
        #print s
        #plans[plan]['speed'] = speedList[s]
        plans[plan]['time_scraped'] = datetime.datetime.now()
        speeds = sorted(re.findall('[0-9, ]+[Mm]bps', speedList[s]))
        if len(speeds) == 1:
            plans[plan]['upload speed'] = speeds[0]
            plans[plan]['download speed'] = speeds[0]
        elif len(speeds) == 2:
            plans[plan]['upload speed'] = speeds[0]
            plans[plan]['download speed'] = speeds[1]
        plans[plan]['monthly cost'] = monthlyCosts[s]
        if noCaps:
            plans[plan]['data caps'] = False
        if setupFees[s] != 'none':
            setupCost = ''
            for i in setupFees[s]:
                setupCost += re.sub('  +|\<|[()]', '', i) + ' '
            #print setupFees[s]
            #print setupCost
            plans[plan]['setup'] = setupCost
        else:
            plans[plan]['setup'] = setupFees[s]
        s += 1
        
    for i in bobbyTables:
       # print i
       # print
       # print
       # print
        #costs = re.findall('$', i)
        #print costs
        features = re.findall('\<h4\>[A-Z a-z\-&$\<\>0-9]+\</h4', i)
        florp = re.findall('h4 class="blue"\>[A-Za-z&\- ,0-9();,]+', i)

        if len(features) == 3:
            p = 0
            for k in planList:
                attribute = re.sub('h4 class="blue"\>|  +', ' ', florp[0])
                parameter = re.sub('\<.{2}|.{3}\>|  +|4|\>', ' ', features[p])
                if 'Contract' in attribute:
                    #print parameter
                    if 'No contract' not in parameter:
                        plans[k]['contract length'] = re.findall('[0-9]+ year', parameter)[0]
                    else:
                        plans[k]['contract length'] = parameter
                #plans[k][attribute] = parameter
                p += 1
        for j in florp:
            j = re.sub('  +', '', j.split('>')[1])
            #print j
            featureList.append(j)
            #for k in planList:
                #plans[k][j] = ''
                
   # for key in plans.keys():
      #  print key
      #  print
      #  for feat in plans[key].keys():
           # print feat
          #  print plans[key][feat]
          #  print
       # print
       # print
    google = pd.DataFrame.from_dict(plans)
    return google
    
google = scrape_google_fiber()
print google

