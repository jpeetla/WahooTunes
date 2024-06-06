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

if __name__ == '__main__':
    app.run(debug=True)

