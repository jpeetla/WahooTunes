from flask import Flask, render_template, request, session, jsonify
from flask_bcrypt import Bcrypt
import json
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


if __name__ == '__main__':
    app.run(debug=True)

