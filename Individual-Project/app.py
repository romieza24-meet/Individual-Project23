from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase
from libretranslatepy import LibreTranslateAPI




app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'

config = {
  "apiKey": "AIzaSyBCSC5C4GLUzG6r5SQHp6dr-8TlOXrUCGI",
  "authDomain": "fridge-y2-individual-project.firebaseapp.com",
  "projectId": "fridge-y2-individual-project",
  "storageBucket": "fridge-y2-individual-project.appspot.com",
  "messagingSenderId": "192768672163",
  "appId": "1:192768672163:web:b258af1b34984d40ce5a16",
  "measurementId": "G-ZPDF6WZ9GS",
  "databaseURL": "https://fridge-y2-individual-project-default-rtdb.europe-west1.firebasedatabase.app/"
}


firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
lt = LibreTranslateAPI("https://translate.argosopentech.com/")

# print(lt.translate("bon sang", "es", "en"))
# print(lt.detect("Hello World"))
print(lt.languages())


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = ""
    if request.method == 'POST':
       email = request.form['email']
       password = request.form['password']
       username = request.form['username']
       try:
            login_session['user'] = auth.create_user_with_email_and_password(email, password)
            UID = login_session['user']['localId']
            user = {
            'email': email,
            'username': username
            }
            db.child("Users").child(UID).set(user)
            return render_template("translate.html")
       except:
           error = "Authentication failed"
    return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        login_session['user'] = auth.sign_in_with_email_and_password(email, password)
        return render_template("translate.html")
        # try:
        #     login_session['user'] = auth.sign_in_with_email_and_password(email, password)
        #     return render_template("translate.html")
        # except:
        #     error = "Authentication failed"
            # print(error)
    return render_template("login.html", error = error)

@app.route('/translate', methods=['GET', 'POST'])
def translate():
    translated_lang = ''
    current_lang = ''
    translation = ''
    history = ''
    if request.method == 'POST':
        try:
            text = request.form['text']
            translated_lang = request.form["translated_lang"] 
            current_lang = lt.detect(text)[0]['language']
            text = lt.translate(text, current_lang, translated_lang)
            UID = login_session['user']['localId']
            history = {'translation': text}
            db.child("Users").child(UID).child("translations").push(history)
            translation = db.child("Users").child(UID).child("translations").get().val()
        except:
            text = 'Error: could not detect language'
        return render_template('translate.html', text = text, history = translation)
    return render_template('translate.html')

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    UID = login_session['user']['localId']
    db.child("Users").child(UID).child("translations").remove()
    return redirect(url_for('translate'))

@app.route('/signout')
def signout():
    login_session['user'] = None
    auth.current_user = None
    return redirect(url_for('login'))




if __name__ == '__main__':
    app.run(debug=True)