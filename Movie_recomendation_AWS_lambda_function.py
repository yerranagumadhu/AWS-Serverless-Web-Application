import pandas as pd
import numpy as np
import wikipedia
import pickle
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy  import process
import boto3
from json.decoder import JSONDecodeError

s3 = boto3.client('s3')

    
movies = pd.read_csv("https://happi2learn.s3.us-east-2.amazonaws.com/movie_dataset.csv")

features = ['keywords','cast','genres','director']

def test():
    print('testing sample function')

# We are considering the 4 features i.e. keywords, cast, genres and director for the movie reocomedation 
def combine_features(row):
    return row['keywords']+' '+row['cast']+' '+row['genres']+' '+row['director']

# Helper function to get the title from the index
def get_title_from_index(index):
    return movies[movies.index == index]['title'].values[0]

# Helper function to get the index from the Title
def  get_index_from_title(title):
    return movies[movies.title == title]['index'].values[0]
    
#Predict the Movie function    
def movie_predict(movie_user_like):

    for feature in features:
        movies[feature] = movies[feature].fillna('')

    movies['combined_features'] = movies.apply(combine_features, axis = 1)

    # Convert a collection of text into a  matrix of token counts
    count_matrix = CountVectorizer().fit_transform(movies['combined_features'])

    # Get the cosine similarity matrix from the count matrix
    cosine_sim = cosine_similarity(count_matrix)

    #Get the Movie name from the user and fetch the index from the movie
    movie_name = process.extractOne(movie_user_like, movies['title'])
    movie_index = get_index_from_title(movie_name[0])

    ## Enumerate all the simillarty score for the movie to make a tuple of movie index and similarity scores 
    # Note : we will return a list of tuples in the form 

    similar_movies = list(enumerate(cosine_sim[movie_index]))

    # Now sort the similar movies based on the similarity score  in descinding order and fetch only the top 5 matching movies and remove the 1st record since it matches with it's own record

    recomended_movies =  []

    for i in sorted(similar_movies, key = lambda x: x[1], reverse= True)[1:6]:
        recomended_movies.append(get_title_from_index(i[0]))


    return recomended_movies
    
# Get the Wikipedia data 
def GetWikipediaData(title_name):
    try:
        description = wikipedia.page(title_name).content
        description = description.split('\n\n')[0]
        image = 'https://www.wikipedia.org/static/apple-touch/wikipedia.png'
        images = wikipedia.page(title_name).images
        for image in images:
            if('poster' in image.lower()):
                break;            
    except:
        description = " No wikipedia Description avaialbe"
        image = 'https://www.wikipedia.org/static/apple-touch/wikipedia.png'
        pass
    return(description, image)

#Main lambda function
def lambda_handler(event, context):
    
    r = json.dumps(event) #json.dumps() will convert the json object to string
    #event = json.dumps(event)
    #event = json.load(event)
    loaded_r = json.loads(r) #json.loads() will convert the string to dict object
    # print(event)
    # print(type(event))
    # print(r)
    # print(type(r))
    # print(loaded_r)
    # print(type(loaded_r))
    
    try:
        if loaded_r['context']['http-method'] == 'GET':
            return {
                'statusCode': 200,
                'body': json.dumps(list(movies['original_title'].unique()))
            }
        
        else:
    
            movie_predicted = movie_predict(loaded_r['body-json'])
            
            # Added to fetch the Wiki data
            wiki_movie = {}
            for i,j in enumerate(movie_predicted):
                wiki_movie_description, wiki_movie_poster  = GetWikipediaData(j +' film') 
                wiki_movie[i] = [j, wiki_movie_description, wiki_movie_poster]
        
            
            #Now return all the objects as a DICT
            rslt = {}
            #rslt['movie_predicted'] = movie_predicted
            #rslt['movie_list'] = movie_list
            rslt['wiki_movie'] = wiki_movie
            rslt['title']= 'Movie Recommendation'
            rslt['req'] = loaded_r['body-json']
            
            #print(event)
            
            
            return {
                'statusCode': 200,
                'body': json.dumps(rslt),
                'headers': json.dumps({ 'Access-Control-Allow-Origin': '*'})
            }
    except JSONDecodeError as e:
        print("Not able to decode")
        pass