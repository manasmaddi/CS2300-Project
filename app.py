from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
#from models import db, User, Authentication, WeightLog, FoodLog, FoodEntry, CaloricPlan
from models import db, User, Authentication, WeightLog, FoodLog, FoodEntry, CaloricPlan
from sqlalchemy import text

from datetime import datetime
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
                # Update last_login time
                auth.last_login = datetime.now()
                db.session.commit()

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

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'userid' not in session:
        return redirect(url_for('login'))

    uid = session['userid']

    if request.method == 'POST':
        try:
            db.session.execute(
                text("""
                    UPDATE "User"
                    SET name = :name,
                        email = :email,
                        height = :height,
                        startingWeight = :startingWeight,
                        currentWeight = :currentWeight,
                        goalWeight = :goalWeight
                    WHERE userID = :uid
                """),
                {
                    "name": request.form['name'],
                    "email": request.form['email'],
                    "height": int(request.form['height']),
                    "startingWeight": float(request.form['startingWeight']),
                    "currentWeight": float(request.form['currentWeight']),
                    "goalWeight": float(request.form['goalWeight']),
                    "uid": uid
                }
            )
            db.session.commit()

            user = db.session.execute(
                text('SELECT * FROM "User" WHERE userID = :uid'),
                {"uid": uid}
            ).fetchone()

            return render_template('settings.html', user=user, success=True)

        except Exception as e:
            return f"Error updating settings: {str(e)}"

    # GET: fetch user data
    user = db.session.execute(
        text('SELECT * FROM "User" WHERE userID = :uid'),
        {"uid": uid}
    ).fetchone()

    return render_template('settings.html', user=user)



@app.route('/add-weight-log', methods=['GET', 'POST'])
def add_weight_log():

    if 'userid' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            new_log = WeightLog(
                logid=random.randint(1, 1000000),  
                userid=session['userid'],
                weight=float(request.form['weight']),
                date=request.form['date']
            )
            db.session.add(new_log)
            db.session.commit()
            #return redirect(url_for('dashboard'))
            #return redirect(url_for('dashboard'))
            return render_template('weightEntry.html', success = True)
        except Exception as e:
            return f"Error adding weight log: {str(e)}"

    return render_template('weightEntry.html')

from datetime import date
from sqlalchemy import text

@app.route('/add-food-entry', methods=['GET', 'POST'])
def add_food_entry():
    if 'userid' not in session:
        return redirect(url_for('login'))

    uid = session['userid']
    today = date.today()

    if request.method == 'POST':
        # 1. Get form values
        foodname = request.form['foodname']
        calories = int(request.form['calories'])
        fats = int(request.form['fats'])
        carbs = int(request.form['carbs'])
        proteins = int(request.form['proteins'])

        # 2. Check if FoodLog exists
        result = db.session.execute(
            text("""
                SELECT entryid FROM "foodlog"
                WHERE userid = :uid AND date = :today
            """),
            {"uid": uid, "today": today}
        ).fetchone()

        if result:
            entryid = result.entryid
        else:
            # 3. Insert new FoodLog for today
            new_log = db.session.execute(
                text("""
                    INSERT INTO "foodlog"(userid, date)
                    VALUES (:uid, :today)
                    RETURNING entryid
                """),
                {"uid": uid, "today": today}
            )
            entryid = new_log.fetchone().entryid

        # 4. Insert food into FoodEntry
        db.session.execute(
            text("""
                INSERT INTO "foodentry"(entryid, foodname, date, calories, fats, carbs, proteins)
                VALUES (:eid, :name, :date, :cal, :fat, :carb, :pro)
            """),
            {
                "eid": entryid,
                "name": foodname,
                "date": today,
                "cal": calories,
                "fat": fats,
                "carb": carbs,
                "pro": proteins
            }
        )

        db.session.commit()
        return render_template("foodEntry.html", success=True)

    return render_template("foodEntry.html")




if __name__ == '__main__':
    with app.app_context():
        test_database_conc()
    app.run(debug=True)


