from app import db

class User(db.Model):
    __tablename__ = 'User'

    userID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255),nullable=False)
    height = db.Column(db.Integer)
    startingWeight = db.Column(db.Float)
    currentWeight = db.Column(db.Float)
    goalWeight = db.Column(db.Float)

class Authentication(db.Model):
    __tablename__ = 'Authentication'

    authID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('User.userID', ondelete='CASCADE'))
    hashedPassword = db.Column(db.Text, nullable=False)
    last_login = db.Column(db.DateTime)

class WeightLog(db.Model):
    __tablename__ = 'WeightLog'

    logID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('User.userID', ondelete='CASCADE'))
    weight = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)

class FoodLog(db.Model):
    __tablename__ = 'FoodLog'

    entryID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('User.userID', ondelete='CASCADE'))
    date = db.Column(db.Date, nullable=False)
    totalCalories = db.Column(db.Integer, default=0)
    totalFats = db.Column(db.Integer, default=0)
    totalCarbs = db.Column(db.Integer, default=0)
    totalProteins = db.Column(db.Integer, default=0)
