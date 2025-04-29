from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'User'   # IMPORTANT: capital 'U' matches your database table

    userid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    password = db.Column(db.Integer, nullable=False)  # (Not actually used — you store password in Authentication)
    height = db.Column(db.Integer, nullable=False)
    startingweight = db.Column(db.Float, nullable=False)
    currentweight = db.Column(db.Float, nullable=False)
    goalweight = db.Column(db.Float, nullable=False)

class Authentication(db.Model):
    __tablename__ = 'Authentication'

    authid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('User.userid', ondelete='CASCADE'))
    hashedpassword = db.Column(db.String, nullable=False)   # Correct: must be String
    last_login = db.Column(db.DateTime)   # Correct: underscore!

class WeightLog(db.Model):
    __tablename__ = 'weightLog'

    logid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('User.userid', ondelete='CASCADE'))
    weight = db.Column(db.Float)
    date = db.Column(db.Date)

class FoodLog(db.Model):
    __tablename__ = 'foodLog'

    entryid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('User.userid', ondelete='CASCADE'))
    date = db.Column(db.Date)
    totalcalories = db.Column(db.Integer)
    totalfats = db.Column(db.Integer)
    totalcarbs = db.Column(db.Integer)
    totalproteins = db.Column(db.Integer)

class FoodEntry(db.Model):
    __tablename__ = 'foodEntry'

    entryid = db.Column(db.Integer, db.ForeignKey('foodLog.entryid', ondelete='CASCADE'), primary_key=True)
    foodname = db.Column(db.String(40))
    date = db.Column(db.Date)
    calories = db.Column(db.Integer)
    fats = db.Column(db.Integer)
    carbs = db.Column(db.Integer)
    proteins = db.Column(db.Integer)

class CaloricPlan(db.Model):
    __tablename__ = 'caloricPlan'

    planid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('User.userid', ondelete='CASCADE'))
    reccalories = db.Column(db.Integer)
    recprotein = db.Column(db.Integer)
    reccarbs = db.Column(db.Integer)
    recfats = db.Column(db.Integer)
    goaltype = db.Column(db.Integer)
