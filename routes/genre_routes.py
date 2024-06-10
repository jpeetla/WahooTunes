from flask import Blueprint, render_template
from .sql_functions import get_genre_details, get_genres
import sqlite3

genres = Blueprint('genres', __name__)

@genres.route('/genre/<int:genre_id>', methods=['GET'])
def genre_detail(genre_id):
    genre, songs = get_genre_details(genre_id)
    return render_template('genre.html', genre_name=genre[0], songs=songs)

@genres.route('/all_genres')
def all_genres():
    genres = get_genres()
    return render_template('all_genres.html', genres=genres)