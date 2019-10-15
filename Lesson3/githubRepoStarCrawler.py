# -*- coding: utf-8 -*-
"""
Created on Sun Oct 13 21:14:03 2019

@author: Sebastien David
"""
# LIBRAIRIES
import re
import pickle
import time
import requests
import numpy as np
from collections import OrderedDict
from tqdm import tqdm
from bs4 import BeautifulSoup
from github import Github
from pathToToken import PATH_TO_TOKEN, read_token_from_txt

# PATH
GIST_WEB_URL = "https://gist.github.com/paulmillr/2657075"
GIT_API_URL  = 'https://api.github.com'
ACCESS_TOKEN = read_token_from_txt(PATH_TO_TOKEN)


#%%

# Get Users From Gist GitHub Webpage
def get_top_256_github_users(website):
    data = requests.get(website)
    data = data.text
    soup = BeautifulSoup(data, 'html.parser')
    
    soupObj = soup.find(id="file-active-md")
    soupTable = soupObj.find('table', cellspacing=0)
    soupTableElements = soupTable.find_all("td")
    soupTableHrefs = [el.findAll('a') for el in soupTableElements]
    soupTableHrefs = [el.get('href') for sublist in soupTableHrefs for el in sublist]
    users = [el for el in soupTableHrefs
             if len(re.findall('^https://github.com/', el))>0]
    users = [el.split('/')[-1] for el in users]
    return users

# Get All Public Repos for 1 User
class GithubCrawler(object):
    """ AAA """
    @classmethod
    def __init__(self, access_token):
        # Connect to GitHub API with Access Token
        apiGitHub = Github(access_token)
        
        # Store Variables
        self.apiGitHub = apiGitHub
        self.access_token = access_token
    
    @classmethod
    def get_all_users_public_repos(self, userList):
        allRepos = [(user, self.get_user_public_repos(user))
                    for user in userList]
        return allRepos
    
    @classmethod
    def get_all_users_mean_repo_stars(self, allRepos):
        allRepos = [(userTuple[0],
                     self.get_user_mean_repo_stars(userTuple[1]))
                    for userTuple in allRepos]
        return allRepos
    
    @classmethod
    def get_user_public_repos(self, user):
        tempUserAPI = self.apiGitHub.get_user(user)
        tempUserRepos = tempUserAPI.get_repos()
        listOfRepos = []
        pageNb = 0
        boolTerminate = False
        while boolTerminate == False:
            tempPageList = tempUserRepos.get_page(pageNb)
            listOfRepos.append(tempPageList)
            pageNb += 1
            if len(tempPageList) == 0:
                boolTerminate = True
        listOfRepos = [item for sublist in listOfRepos
                       for item in sublist]
        return listOfRepos
    
    @classmethod
    def get_user_mean_repo_stars(self, repos):
        listOfRepoStars = [float(repo.stargazers_count)
                           for repo in repos]
        arrayOfRepoStars = np.array(listOfRepoStars)
        meanRepoStars = np.mean(arrayOfRepoStars)
        return meanRepoStars
    
    @classmethod
    def print_rate_limit(self):
        rate_limit = self.apiGitHub.get_rate_limit()
        rate_limit = rate_limit.raw_data['core']['remaining']
        print(rate_limit)


#%%

# MAIN
if __name__ == '__main__':
    
    resultDict = dict()
    
    # Check Pickle File Exists (Else Creates)
    try:
        with open('crawlerResults.pkl', 'rb') as f:
            resultDict = pickle.load(f)
    except:
        with open('crawlerResults.pkl', 'wb') as f:
            pickle.dump(resultDict, f)
    
    # Get Top 256 GitHub Users
    usersList = get_top_256_github_users(GIST_WEB_URL)
    # usersList = usersList[:15] # for testing
    
    # Prepare API
    crawler = GithubCrawler(access_token = ACCESS_TOKEN)
    
    # Update Checkpoint
    try:
        for user in tqdm(usersList, total=len(usersList),
                         position=0):
            
            if resultDict.get(user):
                # Already exists don't update
                pass
            else:
                # Get User Repos
                tempUserRepos = crawler.get_user_public_repos(user)
                
                # Compute Mean Stars for User Repos
                tempMeanStars = \
                    crawler.get_user_mean_repo_stars(tempUserRepos)
                
                # Checkpoint
                resultDict[user] = tempMeanStars
                with open('crawlerResults.pkl', 'wb') as f:
                    pickle.dump(resultDict, f)
            
                # Delay
                time.sleep(2)
    except:
        print('Failure. Required to restart.')
        
    
    # Write results to text file
    for key in resultDict:
        if np.isnan(resultDict.get(key)):
            resultDict[key] = 0.0
    
    resultDictSorted = sorted(resultDict.items(), key=lambda x:-x[1])
    
    with open('top256UsersAvgStars.txt', 'w') as resultFile:
        for el in resultDictSorted:
            stringWrite = '{} : \t\t {} \n'
            resultFile.write(stringWrite.format(el[0], el[1]))

    
