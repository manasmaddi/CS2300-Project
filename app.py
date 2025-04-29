# app.py

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Authentication
import datetime
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres.txngvsfxynpnqutzjove:dbproject1234@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Test database connection
def test_database_conc():
    try:
        db.session.connection()
        print('Database connected successfully.')
    except Exception as e:
        print('Failed to connect to the database.', e)

@app.route('/')
def home():
    return render_template('welcome.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user:
            session['signup_error'] = 'Already signed up. Please login.'
            return redirect(url_for('login'))

        new_user = User(
            userid=random.randint(1, 1000000),
            name=name,
            email=email,
            password=0,
            height=0,
            startingweight=0.0,
            currentweight=0.0,
            goalweight=0.0
        )
        db.session.add(new_user)
        db.session.commit()

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_auth = Authentication(
            userid=new_user.userid,
            hashedpassword=hashed_password,
            last_login=None
        )
        db.session.add(new_auth)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    show_back_button = False
    show_forgot_button = False

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user:
            auth = Authentication.query.filter_by(userid=user.userid).first()
            if auth and check_password_hash(auth.hashedpassword, password):
                session['userid'] = user.userid
                session['name'] = user.name
                return redirect(url_for('dashboard'))
            else:
                error_message = "Incorrect password. Please try again."
                show_forgot_button = True
        else:
            error_message = "User not found. Please sign up."
            show_back_button = True

    return render_template('login.html', error_message=error_message, show_back_button=show_back_button, show_forgot_button=show_forgot_button)

    
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']

        user = User.query.filter_by(email=email).first()
        if user:
            auth = Authentication.query.filter_by(userid=user.userid).first()
            if auth:
                auth.hashedpassword = generate_password_hash(new_password, method='pbkdf2:sha256')
                db.session.commit()
                return redirect(url_for('login'))
            else:
                return "Authentication not found for user."
        else:
            return "User with this email does not exist."

    return render_template('forgot_password.html')


@app.route('/dashboard')
def dashboard():
    if 'userid' not in session:
        return redirect(url_for('login'))

    name = session.get('name')
    return render_template('dashboard.html', name=name)

if __name__ == '__main__':
    with app.app_context():
        test_database_conc()
    app.run(debug=True)