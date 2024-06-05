from flask import Flask, render_template, request, session
import pyrebase
app = Flask(__name__)

config = {
    'apiKey': "AIzaSyBASkRSuh9GQdz95cPf2DHGtiI3tDCifEY",
    'authDomain': "wahootunes.firebaseapp.com",
    'projectId': "wahootunes",
    'storageBucket': "wahootunes.appspot.com",
    'messagingSenderId': "701311223380",
    'appId': "1:701311223380:web:d8203363409f77dbeccfc1",
    'measurementId': "G-HRS3VHRX00",
    'databaseURL': ""
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

app.secret_key = 'secret'
@app.route("/")
def hello():
    if('user' in session):
        return render_template("home.html")
    else:
        return render_template('welcome.html')

@app.route("/login")
def goToLogin():
    return render_template('login.html')

@app.route("/signup")
def goToSignUp():
    return render_template('signup.html')

@app.route('/home', methods=['POST'])
def goHome():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        uvaID = request.form.get("uvaID")
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            user = auth.create_user_with_email_and_password(email, password)
            session["user"] = email
        except:
            return "Failed to Sign Up"

    return render_template('home.html')

if __name__ == "__main__":
  app.run()
