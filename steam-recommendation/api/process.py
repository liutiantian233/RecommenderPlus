import json
from urllib.request import urlopen
import requests,json,os,sys,time,re
import pandas as pd
import numpy as np
import urllib
import bs4
from bs4 import BeautifulSoup
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel,cosine_similarity

def show_work_status(singleCount, totalCount, currentCount):
    currentCount+=singleCount
    percentage=1.*currentCount/totalCount*100
    status='>'*int(percentage/2)+'-'*(50-int(percentage/2))
    if percentage % 3:
        sys.stdout.write('\rStatus:[{0}]{1:.2f}%'.format(status,percentage))
        sys.stdout.flush()
    if percentage>=100: print('\n')

def set_up():
    # get game info from csv as dataframe
    content_data = pd.read_csv('new_steam_games.csv')

    # get game descriptions from url
    Game_description = pd.Series([]) 
    current_count = 0
    for i in range(100):
        url = content_data['Link'][i]
        url_contents = urllib.request.urlopen(url).read()
        soup = bs4.BeautifulSoup(url_contents, 'html.parser')
        div = soup.find("div", {"id": "game_area_description"})
        Game_description[i]=div
        show_work_status(1,100,current_count)
        current_count+=1

    soup = bs4.BeautifulSoup(url_contents, 'html.parser')
    div = soup.find("div", {"id": "game_area_description"})

    content = str(div)
    content_data['Game_description'] = Game_description
    content_data['Game_description'] = content_data['Game_description'].apply(str)

    current_count = 0
    for i in range(0,100):
        content_data['Game_description'][i] = re.sub('<.*?>', ' ', content_data['Game_description'][i])
        content_data['Game_description'][i] = re.sub('\\n.*\\n', ' ', content_data['Game_description'][i])
        content_data['Game_description'][i] = content_data['Game_description'][i].replace("\t","")
        content_data['Game_description'][i] = content_data['Game_description'][i].translate(content_data['Game_description'][i].maketrans(' ',' ',string.punctuation))

        show_work_status(1,100,current_count)
        current_count+=1

    return content_data

def tf_idf(content_data):
    # create tf-idf weighting for the entire dataset
    tfidf_vectorizer = TfidfVectorizer(strip_accents = 'unicode',stop_words='english')
    tfidf = tfidf_vectorizer.fit_transform(list(content_data['Game_description']))
    tfidf_vectorizer.get_feature_names()

    list_app_name = list(content_data['Game_name'])
    return tfidf, list_app_name


# get recommendation list from an input user profile
def get_recommendation(user_profile, content_data, tfidf, list_app_name):
    names = []
    for i in range(len(user_profile)):
        names.append(user_profile[i][0])
        if user_profile[i][1] <= 2:
            user_profile[i][1] = 0.1
        elif user_profile[i][1] > 2 and user_profile[i][1] <= 10:
            user_profile[i][1] = 0.5
        elif user_profile[i][1] > 10 and user_profile[i][1] <= 50:
            user_profile[i][1] = 0.8
        elif user_profile[i][1] > 50 and user_profile[i][1] <= 100: 
            user_profile[i][1] = 1
        else:
            user_profile[i][1] = 1.2

    recommendations = {}
    for game in user_profile:
        name = game[0]
        id = content_data.index[content_data['Game_name'] == name][0]
        similarities = linear_kernel(tfidf[id],tfidf).flatten()
        related_docs_indices = (-similarities).argsort()[1:11]
        lam = 0
        for i in related_docs_indices:
            new_game = list_app_name[i]
            if new_game not in names:
                if new_game not in recommendations:
                    recommendations.update({new_game: game[1]-lam})
                else:
                    value = recommendations.get(new_game)
                    recommendations.update({new_game: value+game[1]-lam})
            lam += 0.01

    recommendations = dict(sorted(recommendations.items(), key=lambda item: item[1], reverse=True))

    output = []
    count = 0
    for key in recommendations:
        output.append(key)
        count += 1
        if count >= 10:
            break

    return output