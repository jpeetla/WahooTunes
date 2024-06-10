from flask import Blueprint, render_template, flash, request, redirect, session
from .sql_functions import get_songs, get_user_id, has_user_rated_song, get_user_ratings
import sqlite3


ratings = Blueprint('ratings', __name__)

@ratings.route('/rate', methods=['GET', 'POST'])
def rate():
    if request.method == 'POST':
        song_id = request.form['song']
        rating = request.form['rating']
        review = request.form['review']
        user_id = get_user_id(session['user'])

        if has_user_rated_song(user_id, song_id):
            flash("You have already rated this song", "fail")
            return redirect('/rate')

        conn = sqlite3.connect('music.sqlite3')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Rating (RatingValue, Review, SongID, UserID) VALUES (?, ?, ?, ?)", (rating, review, song_id, user_id))
        conn.commit()
        conn.close()

        flash("Rating added successfully", "success")

    songs = get_songs()
    return render_template('rating.html', songs=songs)

@ratings.route('/my_ratings')
def my_ratings():
    # print(session)
    if 'user' not in session:
        return render_template('login.html')
    user_ratings = get_user_ratings(session['user'])
    return render_template('my_ratings.html', user_ratings=user_ratings)