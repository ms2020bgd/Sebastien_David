# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 13:30:31 2019

@author: Sebastien David
"""

# LIBRAIRIES
import re
import time
import requests
import pandas as pd
from itertools import combinations
from bs4 import BeautifulSoup

# PATH
WIKI_URL = "https://fr.wikipedia.org/wiki/Liste_des_communes_de_France_les_plus_peupl%C3%A9es"
GEO_API  = "https://fr.distance24.org/route.json?stops={}|{}"


#%%

request = requests.get(WIKI_URL)
data = request.text
soup = BeautifulSoup(data, 'html.parser')

    
#%%


soupObj = soup.find(id="mw-content-text")
soupObj = soupObj.find('table',
                       {"class":"wikitable sortable"})
soupObj = soupObj.find('tbody')

frenchCities = []
for el in soupObj.findAll('tr'):
    
    if len(el.findAll('td')) > 0:
        
        #rank = el.findAll('td')[0].text.strip('\n')
        city = el.findAll('td')[1].text.strip('\n')
        city = re.sub("([\\W_]|[0-9])", "", city)
        
        frenchCities.append(city)
        #frenchCities.append((rank, city))

top10Cities = frenchCities[:10]
print(top10Cities)
# print(frenchCities[-1])


#%%

cityPairDistances = []
cityPairs = combinations(top10Cities, 2)
for cityA, cityB in cityPairs:
    tempAPIUrl = GEO_API.format(cityA, cityB)
    tempRequest = requests.get(tempAPIUrl)
    tempRequestJson = tempRequest.json()
    tempDistance = tempRequestJson['distance']
    tempResult = [cityA, cityB, tempDistance]
    cityPairDistances.append(tempResult)
    time.sleep(1)


#%%

results = pd.DataFrame(cityPairDistances, columns=['City A', 'City B',
                                                   'Distance'])
results = results.sort_values('Distance').reset_index(drop=True)
print(results)
