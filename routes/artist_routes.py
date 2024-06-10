from flask import Blueprint, render_template
from .sql_functions import get_artist_details , get_artists
import sqlite3

artists = Blueprint('artists', __name__)

@artists.route('/artist/<int:artist_id>', methods=['GET'])
def artist_detail(artist_id):
    artist, songs = get_artist_details(artist_id)
    return render_template('artist.html', artist_name=artist[0], real_name=artist[1], phone_number=artist[2], songs=songs, artist_id=str(artist_id))

@artists.route('/all_artists')
def all_artists():
    artists = get_artists()
    return render_template('all_artists.html', artists=artists)