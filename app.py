from flask import Flask, render_template, session
from flask_bcrypt import Bcrypt

from routes.auth_routes import auth
from routes.song_routes import songs
from routes.artist_routes import artists
from routes.genre_routes import genres
from routes.rating_routes import ratings
from routes.report_routes import reports_bp
from routes.eventvenue_routes import eventvenues

from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = "wahootunes123"

app.register_blueprint(auth)
app.register_blueprint(songs)
app.register_blueprint(artists)
app.register_blueprint(genres)
app.register_blueprint(ratings)
app.register_blueprint(reports_bp)
app.register_blueprint(eventvenues)

@app.route("/")
def hello():
    if('user' in session):
        return render_template("home.html")
    else:
        return render_template('welcome.html')

if __name__ == '__main__':
    app.run(debug=True)

