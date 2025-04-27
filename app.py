from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Authentication
from sqlalchemy import text
import datetime
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Correct database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres.txngvsfxynpnqutzjove:dbproject1234@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Test database connection
with app.app_context():
    try:
        db.session.execute(text('SELECT 1'))
        print('Database connected successfully.')
    except Exception as e:
        print('Failed to connect to the database.')
        print(str(e))

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('signup'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user:
            return "User already exists. Please try login."
        new_user = User(
            userid=random.randint(1, 1000000),  # generate random userid
            name=name,
            email=email,
            password=0,  # placeholder, no password column used here
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
        hashedpassword=hashed_password,  # this will now be long text
        lastlogin=None
        )
        
        db.session.add(new_auth)
        db.session.commit()

        return "Signup successful! "

    return render_template('signup.html')


if __name__ == '__main__':
    app.run(debug=True)
