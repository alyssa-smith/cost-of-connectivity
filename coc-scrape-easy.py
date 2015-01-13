import mechanize
import urllib2, urllib, re
from mechanize._opener import urlopen
from mechanize._form import ParseResponse
from bs4 import BeautifulSoup
from selenium import webdriver
import os, datetime, ast
import pandas as pd

#"easy to scrape": time warner, istep, lmi, comcast, lus fiber
#DONE: google fiber

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
    #note that this can also be generalize to other cities w/ google fiber like austin, tx
    capping = re.findall('[A-Za-z]+ data caps', urllib2.urlopen(webAddress).read())
    #checks for mention of data caps; 
    noCaps = True
    
    for i in capping:
        if i!= "No data caps":
            noCaps = False
            print "Google changed their data cap policy!"
            
    monthlyCosts = []
    #cost you pay per month on this plan
    setupFees = []
    #any setup fees for you to start getting google fiber
    
    #i'm really sorry for the ugliness of the following regular expressions.
    
    for m in re.findall('div class="pricing-table widget".{2000}', re.sub('\n', '', urllib2.urlopen(webAddress).read())):
        #pricing-table-widget is the div name for the table lines holding most of the pricing information we care about. 
        #so if we grab the 2000 characters after the pricing-table-widget begins
        #we can get the information we need. 
        
        for t in re.findall('\<p\>[/A-Z a-z0-9\&;\$()\<\>="\*+]+', m):
            #iterates over columns of table, which correspond to plans (they always scrape in the same order)
            if re.findall('.span class="strikethrough".\$[0-9]+./span. construction fee', t) != []:
                #checks for mention of a construction fee--if it's crossed out, there isn't one. 
                #this instance is much more people-readable than scraper-readable. :(
                setupFees.append('none')
            else:
                #else we check for for the mention of a construction fee and record its existence. 
                t = re.sub('.span class="strikethrough".\$[0-9]+./span. construction fee|.span class="c2".|\<[a-z]\>|\<\/[a-z]\>  +','', t)
                setupFees.append( re.findall('[ a-zA-Z\$0-9/()]+\<', t))
                
        plans = {}
        #make a nested dict of plans; each plan has a dict with its attributes that are relevant to coc.
        planList = []
        #list of plans mentioned in the tables
        
        for q in re.findall('h3 class="blue". +\$[0-9]+\/mo', m):
            #gets monthly costs by $[numbers]/mo; there should be as many instances of this as there are plans, and ordered in the same way the plans are (because the order of the columns is invariant)
            monthlyCosts.append(re.sub('h3 class="blue"|  +|\>|\<', '', q))
            #cleans up monthly cost info so it is more readable
            
        for n in re.findall('data-plan-id="[a-zA-Z+-]+"', m):
            #initializes plan name -> empty plan dict
            plans[(re.sub('data-plan-id="|"', '', n))] = {}
            planList.append(re.sub('data-plan-id="|"', '', n))
            
    bobbyTables = re.findall('div class="feature-table".{2000}', re.sub('\n', '', urllib2.urlopen(webAddress).read()))
    #gets features and claimed internet speed
    featureList = []
    speedList = []
    for r in re.findall('\<p\>[A-Za-z 0-9\-&();,]+', bobbyTables[0]):
        #finds speeds, which are in between <p> tags and should have numbers and letters and a few other chars involved (that's what the regular expression is searching for)
        #the regex below is just cleaning up the expression of the speed
        r = re.sub('\<p\>|  +', '', r)
        r = re.sub('&amp;', 'and', r)
        speedList.append(r)
    s = 0
    for plan in planList:
        #writing down when the data was scraped; perhaps we can track how prices change over time
        plans[plan]['time_scraped'] = datetime.datetime.now()
        speeds = sorted(re.findall('[0-9, ]+[Mm]bps', speedList[s]))
        #we take it as invariant that upload speed is always <= download speed. at the very least it is a maximum-likelihood estimate to make.
        if len(speeds) == 1:
            plans[plan]['upload speed'] = speeds[0]
            plans[plan]['download speed'] = speeds[0]
        elif len(speeds) == 2:
            plans[plan]['upload speed'] = speeds[0]
            plans[plan]['download speed'] = speeds[1]
        plans[plan]['monthly cost'] = monthlyCosts[s]
        if noCaps:
            #existence of data cap is a boolean value. 
            plans[plan]['data caps'] = False
        if setupFees[s] != 'none':
            setupCost = 'none'
            for i in setupFees[s]:
                #checks for setupCost and cleans it up should terms exist
                setupCost += re.sub('  +|\<|[()]', '', i) + ' '
            plans[plan]['setup'] = setupCost
        else:
            plans[plan]['setup'] = setupFees[s]
        s += 1
        
    for i in bobbyTables:
        features = re.findall('\<h4\>[A-Z a-z\-&$\<\>0-9]+\</h4', i)
        florp = re.findall('h4 class="blue"\>[A-Za-z&\- ,0-9();,]+', i)

        if len(features) == 3:
            p = 0
            for k in planList:
                #need to add information on contract length.
                attribute = re.sub('h4 class="blue"\>|  +', ' ', florp[0])
                parameter = re.sub('\<.{2}|.{3}\>|  +|4|\>', ' ', features[p])
                if 'Contract' in attribute:
                    if 'No contract' not in parameter:
                        #adds contract length and special terms
                        plans[k]['contract length'] = re.findall('[0-9]+ year', parameter)[0]
                    else:
                        plans[k]['contract length'] = parameter
                p += 1

                

    google = pd.DataFrame.from_dict(plans)
    #make pandas dataframe from dict containing data; a pandas dataframe a) writes neatly to .csv (and back from .csv) and b) turns dicts into a very nicely readable table format. 
    return google

#google = scrape_google_fiber()
#print google
    
def scrape_istep():
    plans = {}
    when = datetime.datetime.now()
    webAddress = 'http://www.istep.com/internet/'
    content = urllib2.urlopen(webAddress).read()
    soup = BeautifulSoup(content)
    services  = soup.find_all('h3')
    services.pop(0)
    index = 0
    for s in services:
        services[index] =re.sub('.h3.|\<', '', str(s))
        
        plans[services[index]] = {}
        index += 1
    #print services
    #services are the types of internet service they offer
    #wait is that too obvious?
    #not for future me probably
    #dear future me, this is exactly how good at things i think you are.
    #ps-i'm so sorry
    #print plans
    content = re.sub('\n',' ', content)
    paramTables =  soup.find_all('table')
    paramTables.pop(0)
    #print len(services)
   # print len(paramTables)
    o = 0
    for p in paramTables:
        tableEntries =  p.find_all('tr')
        attrs = re.sub('\<th\>|\</th\>|\[|\]', '', str(tableEntries[0].find_all('th'))).split(',')
        #attrs contains package attributes
        for t in tableEntries[1:]:
            #for each type of internet service and then for each attribute in the list of attributes, write the cost/attributes
            b = 1
            params = t.find_all('td')
            #print params
            
            
            if services[o] != 'Dialup':
                name = re.sub('\<td\>|\</td\>|\<strong\>|\</strong\>|\<span class="alert"\>|[\*]+|\</span\>', '', str(params[0]))
                plans[services[o]][name] = {}
                for a in attrs[1:]:
                    plans[services[o]][name][re.sub('td', '', str(a))] = re.sub('\<td\>|\</td\>', '', str(params[b]))
                    b += 1
            else:
                b = 0
                for a in attrs:
                    #print a
                    pr = re.sub('\<td\>|\</td\>', '', str(params[b]))
                    #print pr
                    b += 1
                    plans[services[o]][a] = pr
                
            
        o += 1
    
    #print plans
    plansNeater = {}
    for internet in plans.keys():
        #print internet
        #print plans[internet]
        if internet != 'Dialup':
            for level in plans[internet].keys():
                plansNeater[str(internet) + ' ' + str(level)] = plans[internet][level]
        else:
            for k in plans[internet].keys(): 
                plansNeater[str(internet) + ' ' + str(k)] = {}
                plansNeater[str(internet) + ' ' + str(k)][' Monthly'] = plans[internet][k]
        
            
    #print plansNeater
    istep = pd.DataFrame.from_dict(plansNeater)
    return istep
    
print scrape_istep()
    
    


