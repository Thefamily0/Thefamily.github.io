from flask import Flask, render_template, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
import smtplib
import random
import json
from datetime import datetime

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True

app = Flask(__name__)

if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

app.secret_key = b'\n\x8d\xe7\x05/\x96\x8d\xdb\x8d\xdd\xe7\xb4\xfa@\x94\xd6\xf8\xfa\x19\xc3xb14'

db = SQLAlchemy(app)


class Userinfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(12), nullable=True)


@app.route("/", methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route("/login_validation", methods=['GET', 'POST'])
def login_validation():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        result = db.session.execute("SELECT email, password from userinfo WHERE email = '{}' AND password = '{}'".format(email, password))

        reslist = result.all()

        if len(reslist) == 1:
            return redirect('/home')
        else:
            flash('Invalid Credentials!')
            return render_template('login.html')


@app.route("/forget")
def forget():
    return render_template('forget_password.html')


@app.route("/password", methods=['GET', 'POST'])
def passwd():
    if request.method == 'POST':
        uname = request.form['username']
        email = request.form['email']
        try:
            result = db.session.execute("SELECT username, email FROM userinfo WHERE username = '{}' AND email = '{}'".format(uname, email))
            reslist = result.all()
            if len(reslist) == 1:
                result1 = db.session.execute("SELECT password FROM userinfo WHERE username = '{}' AND email = '{}'".format(uname, email))
                reslist1 = result1.all()

                message = "Your Password is " + str(reslist1[0])

                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(params['gmail-user'], params['gmail-password'])
                server.sendmail(params['gmail-user'], email, message)
            else:
                flash('Invalid Inputs!')
        except() as e:
            return render_template('forget_password.html', error=e)
    return render_template('login.html')


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        message = "Your One Time Password is " + str(random.randint(1000, 9999))

        entry = Userinfo(username=username, email=email, password=password, date=datetime.now())
        db.session.add(entry)
        db.session.commit()

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(params['gmail-user'], params['gmail-password'])
        server.sendmail(params['gmail-user'], email, message)

    return render_template('registration.html', params=params)


@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


app.run(debug=True)
