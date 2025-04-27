from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    userid = db.Column(db.Integer, primary_key=True)  # ✅ lowercase
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    startingweight = db.Column(db.Float, nullable=False)
    currentweight = db.Column(db.Float, nullable=False)
    goalweight = db.Column(db.Float, nullable=False)

class Authentication(db.Model):
    __tablename__ = 'authentication'
    authid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    hashedpassword = db.Column(db.Integer, nullable=False)
    lastlogin = db.Column(db.DateTime)
