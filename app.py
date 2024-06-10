from flask import Flask, render_template, request, session, jsonify
from flask_bcrypt import Bcrypt
import json
import sqlite3
import pyrebase

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = 'wahootunes123'

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
            session['user'] = email
            return jsonify({"message": "Login successful"}), 200
        else:
            print("Authentication failed...")
    return render_template('login.html')

@app.route("/signup", methods=['POST', 'GET'])
def goToSignUp():
    if request.method == "POST":
        data = request.get_json()

        firstname, lastname = data["fullname"].split()
        email = data["email"]
        password = data["password"]
        
        conn = sqlite3.connect('music.sqlite3')
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT Email FROM User WHERE Email = ?", (email,))
            existing_user = cursor.fetchone()
            if existing_user:
                # print("1: Email already exists in database")
                return jsonify({"error": "Email already exists"}), 409

            if email in users:
                # print("2: Email already exists in JSON file")
                return jsonify({"error": "Email already exists"}), 409

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            users[email] = hashed_password
            save_users()

            cursor.execute("INSERT INTO User (FirstName, LastName, Email) VALUES (?, ?, ?)", (firstname, lastname, email))
            
            conn.commit()
            session['user'] = email
            
            return jsonify({"message": "Signup successful"}), 201
        except sqlite3.IntegrityError:
            # print("3: Integrity error occurred")
            return jsonify({"error": "Integrity error occurred"}), 500
        finally:
            conn.close()
    
    return render_template('signup.html')

@app.route('/home', methods=['POST', 'GET'])
def goHome():
    user = session.get('user')
    if user is None:
        return render_template('login.html')
    return render_template('home.html', user=user)

@app.route('/welcome')
def logout():
    session.pop('user', None) 
    return render_template('welcome.html')

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

def get_artist_details(artist_id):
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT StageName, RealName, PhoneNumber FROM Artist WHERE ArtistID = ?", (artist_id,))
    artist = cursor.fetchone()
    cursor.execute("""
        SELECT Song.SongTitle, IFNULL(AVG(Rating.RatingValue), 'No ratings yet') as AvgRating
        FROM Song
        JOIN SongArtist ON Song.SongID = SongArtist.SongID
        LEFT JOIN Rating ON Song.SongID = Rating.SongID
        WHERE SongArtist.ArtistID = ?
        GROUP BY Song.SongID
    """, (artist_id,))
    songs = cursor.fetchall()
    conn.close()
    return artist, songs

def get_genre_details(genre_id):
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT Name FROM Genre WHERE GenreID = ?", (genre_id,))
    genre = cursor.fetchone()
    cursor.execute("""
        SELECT Song.SongTitle, IFNULL(AVG(Rating.RatingValue), 'No ratings yet') as AvgRating
        FROM Song
        LEFT JOIN Rating ON Song.SongID = Rating.SongID
        WHERE Song.GenreID = ?
        GROUP BY Song.SongID, Song.SongTitle
    """, (genre_id,))
    songs = cursor.fetchall()
    conn.close()
    return genre, songs

def get_user_id(user_email):
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT UserID FROM User WHERE Email = ?", (user_email,))
    user_id = cursor.fetchone()
    conn.close()
    return user_id[0] if user_id else None

@app.route('/rate', methods=['GET', 'POST'])
def rate():
    if request.method == 'POST':
        song_id = request.form['song']
        rating = request.form['rating']
        review = request.form['review']
        user_id = get_user_id(session['user'])
        
        conn = sqlite3.connect('music.sqlite3')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Rating (RatingValue, Review, SongID, UserID) VALUES (?, ?, ?, ?)", (rating, review, song_id, user_id))
        conn.commit()
        conn.close()
        
        return render_template('rating.html', message="Rating submitted successfully.")
    
    songs = get_songs()
    return render_template('rating.html', songs=songs)

@app.route('/song/<int:song_id>', methods=['GET'])
def song_detail(song_id):
    song, ratings = get_song_details(song_id)
    return render_template('song_detail.html', song_title=song[0], genre=song[2], artist=song[3], song_length=song[4], ratings=ratings)

@app.route('/artist/<int:artist_id>', methods=['GET'])
def artist_detail(artist_id):
    artist, songs = get_artist_details(artist_id)
    return render_template('artist.html', artist_name=artist[0], real_name=artist[1], phone_number=artist[2], songs=songs)

@app.route('/genre/<int:genre_id>', methods=['GET'])
def genre_detail(genre_id):
    genre, songs = get_genre_details(genre_id)
    return render_template('genre.html', genre_name=genre[0], songs=songs)

@app.route('/all_songs')
def all_songs():
    songs = get_songs()
    return render_template('all_songs.html', songs=songs)

@app.route('/all_artists')
def all_artists():
    artists = get_artists()
    return render_template('all_artists.html', artists=artists)

def get_artists():
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT ArtistID, StageName FROM Artist")
    artists = cursor.fetchall()
    conn.close()
    return artists

@app.route('/all_genres')
def all_genres():
    genres = get_genres()
    return render_template('all_genres.html', genres=genres)

def get_genres():
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT GenreID, Name FROM Genre")
    genres = cursor.fetchall()
    conn.close()
    return genres

@app.route('/my_ratings')
def my_ratings():
    user_id = get_user_id(session['user'])
    print(user_id)
    if 'user' not in session:
        return render_template('login.html')
    
    user_ratings = get_user_ratings(session['user'])
    return render_template('my_ratings.html', user_ratings=user_ratings)

def get_user_ratings(user_email):
    user_id = get_user_id(user_email)
    if not user_id:
        return []
    
    conn = sqlite3.connect('music.sqlite3')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Rating.RatingValue, Rating.Review, Song.SongTitle, Artist.StageName, Song.SongID, Artist.ArtistID
        FROM Rating
        JOIN Song ON Rating.SongID = Song.SongID
        JOIN SongArtist ON Song.SongID = SongArtist.SongID
        JOIN Artist ON SongArtist.ArtistID = Artist.ArtistID
        WHERE Rating.UserID = ?
    """, (user_id,))
    user_ratings = cursor.fetchall()
    conn.close()
    return user_ratings

if __name__ == '__main__':
    app.run(debug=True)

