# -*- coding: utf-8 -*-
"""
Telecom Paris
MS Big Data
Kit Data Science Assignment
"""

import re
import time
import requests
from bs4 import BeautifulSoup

URL_START = "https://en.wikipedia.org/wiki/Special:Random"
URL_START = requests.get(URL_START).url
# URL_START = "https://en.wikipedia.org/wiki/Master_System"
# URL_START = "https://en.wikipedia.org/wiki/Object_of_the_mind"
# URL_START = "https://en.wikipedia.org/wiki/Game_cartridge"
# URL_START = "https://en.wikipedia.org/wiki/Epistemic"
URL_FINAL = "https://en.wikipedia.org/wiki/Philosophy"

def getFirstWikipediaLink(urlInput, skipFirstLink=False):
    
    requestPageObj = requests.get(urlInput)
    htmlPageObj = requestPageObj.text
    htmlParsedPageObj = BeautifulSoup(htmlPageObj, 'html.parser')
    
    ### Print the Title of the Article
    
    htmlParsedPageContentObj = htmlParsedPageObj.find(id="mw-content-text") \
                                .find(class_="mw-parser-output")
    htmlParsedPageParagraphs = htmlParsedPageContentObj.find_all("p")
    
    foundTargetHref = False
    linksFoundResult = []
    paragraphsSearched = 0
    # i = 0
    for tempParagraph in htmlParsedPageParagraphs:
        
        # print(tempParagraph)
        
        if tempParagraph.find("a", recursive=False):
            
            # print(tempParagraph.find("a", recursive=True))
            tempCleanParagraph = tempParagraph
            
            # for _ in range(0, 2):
            #    tempCleanParagraph = tempCleanParagraph.prettify()
            #    tempCleanParagraph = re.sub(r"\([^()]*\)", ' ', tempCleanParagraph)
            #    tempCleanParagraph = BeautifulSoup(tempCleanParagraph, 'lxml')
            
            # if i == 0:
                # print(tempParagraph.prettify()[:300], '\test\n')
                # print(tempCleanParagraph.prettify()[:300])
                # ans = tempParagraph
                # print(ans)
            
            # i+=1
            
            for hrefPageLink in tempCleanParagraph.findAll("a", recursive=True):
                
                hrefPageLink = hrefPageLink.get('href')
                # print('Link:', hrefPageLink)
                
                # Ensure it is a Wikipedia article
                if foundTargetHref == False:
                    
                    # Skip wikitionary articles
                    if len(re.findall('^\/wiki', hrefPageLink)) > 0:
                        
                        # Skip all links with '<word>:' pattern
                        if len(re.findall(r'\b(\w\w*)\b\:', hrefPageLink)) == 0:
                            
                            # Skip First Link (if checked above)
                            linksFoundResult.append(hrefPageLink)
                            
            # First paragraph: Terminate
            if paragraphsSearched > 1:
                break
            
            paragraphsSearched += 1
            
            # hrefPageLink = tempParagraph.find("a", recursive=True).get('href')
            # print(hrefPageLink)
    
    linksFoundResult = ['https://en.wikipedia.org{}'.format(tempTargetHref)
                        for tempTargetHref in linksFoundResult]
    
    # Click on second link if already searched
    if skipFirstLink == False:
        firstUrlLink = linksFoundResult[0]
    else:
        firstUrlLink = linksFoundResult[1] 
    
    # If Philosophy is Found on First Paragraphs
    if URL_FINAL in linksFoundResult:
        # print('FOUND IT !')
        firstUrlLink = URL_FINAL
    
    return firstUrlLink

# print(getFirstWikipediaLink('https://en.wikipedia.org/wiki/Latin'))
# print(getFirstWikipediaLink('https://en.wikipedia.org/wiki/Russian_language'))
# print(getFirstWikipediaLink('https://en.wikipedia.org/wiki/Data_storage_device'))
# print(getFirstWikipediaLink('https://en.wikipedia.org/wiki/Epistemology'))
    
#%%

maxSearchLimit = 100
nbSearchCount = 0
pagesSearchList = [URL_START]
distStartToFinal = 0
boolPageNotFound = True
boolSkipFirstLink = False

print('Wikipedia: Getting to Philosophy')
print(URL_START)

while boolPageNotFound:
    
    # Wikipedia Search
    urlInputNextLink = getFirstWikipediaLink(pagesSearchList[-1],
                                             boolSkipFirstLink)
    
    # Append result
    pagesSearchList.append(urlInputNextLink)
    
    print(urlInputNextLink)
    
    # Update
    nbSearchCount += 1
    distStartToFinal += 1
    boolSkipFirstLink = False
    
    # Found Philosophy Page :)
    if urlInputNextLink == URL_FINAL:
        print('Found Philosophy Wikipedia Page :) !')
        
        if distStartToFinal > 1:
            plural = 's'
        else:
            plural = ''
        
        print('Distance From random article to Philosophy page:',
              distStartToFinal, 'page{}.'.format(plural))
        break
    
    # Article Repeats (Cycle Detected): Terminate search.
    if urlInputNextLink in pagesSearchList[::-1][1:]:
        boolSkipFirstLink = True
        print('Loop. We have entered a cycle. Attempt second link.')
    
    # To many searches: Terminate.
    if nbSearchCount > maxSearchLimit:
        break
    
    time.sleep(2)
