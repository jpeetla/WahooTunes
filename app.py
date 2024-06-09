from flask import Flask, render_template, request, session, jsonify
from flask_bcrypt import Bcrypt
import json
import sqlite3
import pyrebase

app = Flask(__name__)
bcrypt = Bcrypt(app)


try:
    with open('users.json', 'r') as f:
        users = json.load(f)
except FileNotFoundError:
    users = {}

def save_users():
    with open('users.json', 'w') as f:
        json.dump(users, f)

@app.route("/")
def hello():
    if('user' in session):
        return render_template("home.html")
    else:
        return render_template('welcome.html')

@app.route("/login", methods=['POST', 'GET'])
def goToLogin():
    if request.method == "POST":
        data = request.get_json()
        email = data["email"]
        password = data["password"]
        hashed_password = users.get(email)

        if hashed_password and bcrypt.check_password_hash(hashed_password, password):
            return jsonify({"message": "Login successful"}), 200
        else:
            print("Authentication failed...")
    return render_template('login.html')

@app.route("/signup", methods=['POST', 'GET'])
def goToSignUp():
    if request.method == "POST":
        data = request.get_json()

        fullname = data["fullname"]
        uvaID = data["uvaId"]
        email = data["email"]
        password = data["password"]

        if email in users:
            return jsonify({"error": "Email already exists"}), 409

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        users[email] = hashed_password
        save_users()
        return jsonify({"message": "Signup successful"}), 201
    return render_template('signup.html')

@app.route('/home', methods=['POST', 'GET'])
def goHome():
    return render_template('home.html')

def get_songs():
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT SongID, SongTitle FROM Song")
    songs = cursor.fetchall()
    conn.close()
    return songs

def get_song_details(song_id):
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT SongTitle, GenreID, (SELECT Name FROM Genre WHERE GenreID = Song.GenreID) as Genre, (SELECT StageName FROM Artist WHERE ArtistID = (SELECT ArtistID FROM SongArtist WHERE SongID = ?)) as Artist, SongLength FROM Song WHERE SongID = ?", (song_id, song_id))
    song = cursor.fetchone()
    cursor.execute("SELECT RatingValue, Review, (SELECT Email FROM User WHERE UserID = Rating.UserID) as User FROM Rating WHERE SongID = ?", (song_id,))
    ratings = cursor.fetchall()
    conn.close()
    return song, ratings

@app.route('/rate', methods=['GET', 'POST'])
def rate():
    if request.method == 'POST':
        song_id = request.form['song']
        rating = request.form['rating']
        review = request.form['review']
        
        conn = sqlite3.connect('music.sqlite3')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Rating (RatingValue, Review, SongID, UserID) VALUES (?, ?, ?, ?)", (rating, review, song_id, 1))
        conn.commit()
        conn.close()
        
        return redirect(url_for('rate'))
    
    songs = get_songs()
    return render_template('rating.html', songs=songs)

@app.route('/song/<int:song_id>', methods=['GET'])
def song_detail(song_id):
    song, ratings = get_song_details(song_id)
    return render_template('song_detail.html', song_title=song[0], genre=song[2], artist=song[3], song_length=song[4], ratings=ratings)

if __name__ == '__main__':
    app.run(debug=True)

