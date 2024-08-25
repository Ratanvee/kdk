from flask import Flask, render_template, jsonify, redirect, request, flash, url_for
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import pandas as pd
import requests

app = Flask(__name__)

# Global variables for data
movies = None
similarity = None

def fetch_poster(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=9ba9b8b675c31561091a4aa35820c8f5&language=en-US')
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

def fetch_posters(movie_ids):
    # Sequentially fetch each poster
    posters = []
    for movie_id in movie_ids:
        poster_url = fetch_poster(movie_id)
        posters.append(poster_url)
    return posters

def recommend(movie):
    # Find the index of the input movie in the dataframe
    movie_index = movies[movies['title'] == movie].index[0]
    
    # Calculate distances from the input movie to all other movies
    distances = similarity[movie_index]
    
    # Create a list of (index, distance) tuples
    indexed_distances = list(enumerate(distances))
    
    # Sort the list based on distance in descending order and take the top 20 (excluding the first one)
    sorted_movies = sorted(indexed_distances, key=lambda x: x[1], reverse=True)[1:21]
    
    # Get the titles and movie IDs of the recommended movies
    recommend_movies = [movies.iloc[i[0]].title for i in sorted_movies]
    movie_ids = [movies.iloc[i[0]].movie_id for i in sorted_movies]
    
    # Fetch posters for the recommended movies
    recommended_movie_poster = fetch_posters(movie_ids)
    
    # Add the input movie to the list of recommended movies
    recommend_movies.insert(0, movie)  # Adding the input movie at the beginning
    recommended_movie_poster.insert(0, fetch_poster(movies.iloc[movie_index].movie_id))  # Fetch and insert the poster
    
    return recommend_movies, recommended_movie_poster



# Load the data at the global level
def load_data():
    global movies, similarity
    # Load movie data
    movies_dict = pickle.load(open('templates/models/movies1.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    
    # Load and combine similarity data
    with open("templates/models/similarity/new_part_1.pkl", "rb") as file:
        first_half = pickle.load(file)
    with open("templates/models/similarity/new_part_2.pkl", "rb") as file:
        second_half = pickle.load(file)
    
    similarity = first_half + second_half

# Call load_data() function at the time of app initialization
load_data()

@app.route('/')
def index():
    data = movies['title'].values
    return render_template('index.html', my_dict=data)

@app.route('/', methods=['POST'])
def button_click():
    input_movie = request.form.get('input')
    data = movies['title'].values
    
    if input_movie in movies['title'].values:
        name, poster = recommend(input_movie)
        dictionary = dict(zip(name, poster))
    else:
        name = 'movie not exist'
        poster = 'movie not exist'
        dictionary = {}
    
    default_value = 0
    dictionary1 = dict.fromkeys(data, default_value)
    
    return render_template('index.html', my_dict=data, input1=input_movie, dict1=dictionary, dictionary1=dictionary1)

if __name__ == "__main__":
    app.run(port=8000, debug=True)
