import requests
import json
import pandas as pd
import numpy as np
import configparser

from flask import Flask
from flask import render_template
from flask import request
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


config = configparser.ConfigParser()
config.read('config.ini')
API_KEY = config['DEFAULT']['api_key']


_df_data = None
_similarity_matrix = None


def create_similarity():
    global _df_data, _similarity_matrix

    _df_data = pd.read_csv('dataset/movies.csv')
    _df_data['original_title'] = _df_data['original_title'].str.lower()

    count_vectorizer = CountVectorizer()
    # Create count matrix.
    count_matrix = count_vectorizer.fit_transform(_df_data['metadata']) 

    df_count = pd.DataFrame(count_matrix.todense(), 
                            columns=count_vectorizer.get_feature_names())
    
    _similarity_matrix = cosine_similarity(count_matrix)


def get_movies_recommended(movie_title):

    movie_title = movie_title.lower()
    if _df_data is None:
        create_similarity()

    if movie_title not in _df_data['original_title'].unique():
        return []
    else:
        idx = _df_data.loc[_df_data['original_title'] == movie_title].index[0]

        similarity_list = list(enumerate(_similarity_matrix[idx]))
        similarity_list = sorted(similarity_list, key=lambda x: x[1], 
                                reverse=True)
        # Excluding first element since it is the requested movie itself.
        similarity_list = similarity_list[1:11]  

        movies_list = []
        for i in range(len(similarity_list)):
            idx = similarity_list[i][0]
            movies_list.append(_df_data['original_title'][idx])

        return movies_list
        

def get_movie_details(movie_title):
    url = 'https://api.themoviedb.org/3/search/movie?api_key={}&query={}'. \
            format(API_KEY, movie_title)
    response = requests.get(url)
    dict_response = json.loads(response.text)

    if len(dict_response['results']) > 0:
        movie_id = dict_response['results'][0]['id']
        url = 'https://api.themoviedb.org/3/movie/{}?api_key={}'. \
            format(movie_id, API_KEY)
        response = requests.get(url)
        return json.loads(response.text)

    return {}


def get_movie_suggestions():
    df_movies =  pd.read_csv('dataset/movies.csv')
    return list(df_movies['original_title'].str.capitalize())



app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    suggestions_list = get_movie_suggestions()
    return render_template('home.html', movie_suggestions=suggestions_list)


@app.route('/api_key')
def get_api_key():
    with open('files/tmdb_api') as file:
        api_key = file.readline()
    return api_key


@app.route('/recommend', methods=['POST'])
def recommend_movies():
    movie_title = request.form['movie_title']
    dict_details = get_movie_details(movie_title)
    
    if bool(dict_details):

        movies_list = get_movies_recommended(dict_details['original_title'])
        if not movies_list:
            return ('Sorry! The movie you requested is not in database. ' 
                    'Please check the spelling or try with other movies!')
        else:

            title = dict_details['original_title']
            poster = 'https://image.tmdb.org/t/p/original/{}'. \
                    format(dict_details['poster_path'])
            overview = dict_details['overview']
            rating = dict_details['vote_average']
            vote_count = dict_details['vote_count']
            rating = str(rating) + '/10 ({} votes)'.format(str(vote_count))
            release_date = datetime.strptime(dict_details['release_date'], 
                                            '%Y-%m-%d')
            release_date = release_date.strftime('%b %d %Y')
            runtime = str(dict_details['runtime']) + ' minutes'
            status = dict_details['status']

            language_list = ', '.join([language['name'] 
                            for language in dict_details['spoken_languages']])
            genre_list = ', '.join([genre['name'] 
                            for genre in dict_details['genres']])

            # Get details of movies recommended.
            recommend_dict = []
            for movie_title in movies_list:
                dict_details = get_movie_details(movie_title)

                if dict_details['poster_path'] is not None:
                    temp_poster = 'https://image.tmdb.org/t/p/original/{}'. \
                            format(dict_details['poster_path'])
                    temp_dict = {
                        'title': movie_title,
                        'poster': temp_poster
                    } 
                    recommend_dict.append(temp_dict)


            return render_template('recommend.html', title=title, 
                                    poster=poster, language=language_list, 
                                    genre=genre_list, rating=rating, 
                                    release_date=release_date, runtime=runtime, 
                                    status=status, overview=overview,
                                    recommend_dict=recommend_dict)

   
    return ('Sorry! The movie you requested is not in database. '
            'Please check the spelling or try with other movies!')





if __name__ == '__main__':
    app.run(debug=True)

