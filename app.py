from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def hello():
  return render_template('welcome.html')

@app.route("/login")
def goToLogin():
    return render_template('login.html')

@app.route("/signup")
def goToSignUp():
    return render_template('signup.html')

@app.route('/home', methods=['POST'])
def goHome():
    return render_template('home.html')

def logIn():
    return "hi"

def signUp():
    return "hi"


if __name__ == "__main__":
  app.run()
