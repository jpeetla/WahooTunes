from flask import Blueprint, render_template, request, session, flash, jsonify
from flask_bcrypt import Bcrypt
from .sql_functions import get_user_id
from dotenv import load_dotenv

import json
import sqlite3
import os


auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()

load_dotenv()

try:
    with open('users.json', 'r') as f:
        users = json.load(f)
except FileNotFoundError:
    users = {}

def save_users():
    with open('users.json', 'w') as f:
        json.dump(users, f)
        
@auth.route("/login", methods=['POST', 'GET'])
def goToLogin():
    if request.method == "POST":
        data = request.get_json()
        email = data["email"]
        password = data["password"]
        hashed_password = users.get(email)
        userId = get_user_id(email)

        if hashed_password and bcrypt.check_password_hash(hashed_password, password):
            session['user'] = email
            session['userId'] = userId

            if userId is None:
                conn = sqlite3.connect('music.sqlite3')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO User (Email) VALUES (?)", (email,))
                conn.commit()
                conn.close()
                session['userId'] = get_user_id(email)

            flash("Login successful", "success")
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"message": "Authentication failed. Check your email and password again."}), 401
    return render_template('login.html')

@auth.route("/signup", methods=['POST', 'GET'])
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

@auth.route('/home', methods=['POST', 'GET'])
def goHome():
    # venues = get_venues()
    # geocoded_venues = []
    # for venue in venues:
    #     name, street, city, state = venue
    #     lat, lng = geocode_address(street, city, state)
    #     if lat and lng:
    #         geocoded_venues.append((name, lat, lng))
    user = session.get('user')
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    # print("API KEY: ", google_maps_api_key)
    if user is None:
        return render_template('login.html')
    return render_template('home.html', user=user, api_key = google_maps_api_key)

@auth.route('/welcome')
def logout():
    session.pop('user', None)
    return render_template('welcome.html', message = "Logout successful")