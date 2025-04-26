from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # For session management

# Connect to Supabase PostgreSQL using SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.txngvsfxynpnqutzjove:dbproject1234@aws-0-us-east-1.pooler.supabase.com:6543/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Import models after db is initialized
#from models import User

@app.route('/')
def home():
    return "Welcome to the Fitness Tracker App (SQLAlchemy version)!"

if __name__ == '__main__':
    app.run(debug=True)
