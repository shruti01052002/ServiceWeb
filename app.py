from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json
from instamojo_wrapper import Instamojo

import os

# with open('config.json', 'r') as c:
#     params = json.load(c)["params"]

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///signup.db'
app.config['TEMPLATES_AUTO_RELOAD'] = True
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contact.db'
db = SQLAlchemy(app)
API_KEY = "test_8b73385262d5777a16da8a8337f"
AUTH_TOKEN = "test_6cb6f0a8a52ad17a891e5942dc8"

api = Instamojo(api_key=API_KEY,auth_token=AUTH_TOKEN,endpoint='https://test.instamojo.com/api/1.1/')

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME='shrutiyadav26072002@gmail.com',
    MAIL_PASSWORD='2019b121002'
)
mail = Mail(app)


# User model which takes the data of users and saves it in database
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(200), nullable=False)
    password1 = db.Column(db.String(200), nullable=False)
    password2 = db.Column(db.String(200), nullable=False)
    date_signup = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return 'User ' + str(self.id) + " " + self.username


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=False)
    email = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return 'Contact ' + str(self.sno) + " " + self.name


# base function which render the user to the landing page
@app.route('/')
def base():
    return render_template('base.html')


@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    return render_template('welcome.html')


@app.route('/webdev', methods=['GET', 'POST'])
def webdev():
    return render_template('webd.html')


@app.route('/payment', methods=['GET'])
def payment():
    return render_template('paymentHistory.html')

@app.route('/edit', methods=['GET'])
def edit():
    return render_template('editProfile.html')


# valid_login function checks whether the user is authenticate or not
def valid_login(username, password):
    exist_user = Users.query.filter_by(username=username, password1=password).all()
    if len(exist_user) != 0:
        return True
    else:
        return False


@app.route("/contact", methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        name = request.form['name1']
        email = request.form['email1']
        phone = request.form['phone1']
        message = request.form['message1']
        gmail = 'shrutiyadav26072002@gmail.com'
        entry = Contacts(name=name, phone_num=phone, msg=message, email=email)
        db.session.add(entry)
        db.session.commit()
        print("successful")
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=[gmail],
                          body=message + "\n" + phone
                          )
        return render_template('base.html', greet="We will reach to you soon")
    return render_template('base.html')


# login function let the authenticate user to successfully logged in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password1']):
            print(request.form['username'])
            return render_template('welcome.html', user=request.form['username'])
        else:
            error = 'Invalid username/password'
            return render_template('login.html', errors=error)
    else:
        return render_template('login.html')


# signup function let the new user to add the new user into the database
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_email = request.form['email']
        user_name = request.form['username']
        user_password1 = request.form['password1']
        user_password2 = request.form['password2']
        if user_password1 == user_password2:
            new_user = Users(email=user_email, username=user_name, password1=user_password1, password2=user_password2)
            db.session.add(new_user)
            db.session.commit()
            print(user_password1)
            print(user_password2)
            return redirect('/login')
        else:
            return redirect('/')
    else:
        return render_template('Signup.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/pay',methods=['POST','GET'])
def pay():
    if request.method == 'POST':
        name = request.form.get('name')
        purpose = request.form.get('purpose')
        email = request.form.get('email')
        amount = request.form.get('amount')
        
        response = api.payment_request_create(
        amount=amount,
        purpose=purpose,
        buyer_name=name,
        send_email=True,
        email=email,
        redirect_url="http://localhost:5000/success"
        )
        
        return redirect(response['payment_request']['longurl'])
    else:
        
        return redirect('/webdev')


if __name__ == "__main__":
    app.run(debug=True)
