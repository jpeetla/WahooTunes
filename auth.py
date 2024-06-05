import pyrebase

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

email = 'test@gmail.com'
password = '123456'

user = auth.create_user_with_email_and_password(email, password)
user = auth.sign_in_with_email_and_password(email, password)
info = auth.get_account_info(user['idToken'])
