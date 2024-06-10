from flask import Blueprint, render_template
from .sql_functions import get_song_details , get_songs
import sqlite3

songs = Blueprint('songs', __name__)

@songs.route('/song/<int:song_id>', methods=['GET'])
def song_detail(song_id):
    song, ratings = get_song_details(song_id)
    return render_template('song_detail.html', song_id=song_id, song_title=song[1], genre=song[3], artist=song[4], song_length=song[5], ratings=ratings, artist_id=song[6])

@songs.route('/all_songs')
def all_songs():
    songs = get_songs()
    return render_template('all_songs.html', songs=songs)