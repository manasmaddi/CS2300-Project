from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Authentication, WeightLog, FoodLog, FoodEntry, CaloricPlan
from sqlalchemy import text
from datetime import date
from sqlalchemy import text

import matplotlib
matplotlib.use('Agg')  # <-- Add this line
import matplotlib.pyplot as plt
from flask import send_file
from chart_cache import generate_cache_key, is_cache_valid, update_cache_file
import matplotlib.dates as mdates
import io
import os

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
        age = request.form['age']
        gender = request.form['gender']

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
            goalweight=0.0,
            age = age,
            gender = gender,
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
                        age = :age,
                        gender = :gender,
                        startingWeight = :startingWeight,
                        currentWeight = :currentWeight,
                        goalWeight = :goalWeight
                    WHERE userID = :uid
                """),
                {
                    "name": request.form['name'],
                    "email": request.form['email'],
                    "height": int(request.form['height']),
                    "age": int(request.form['age']),
                    "gender": request.form['gender'],
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

    # fetch user data from the query
    user = db.session.execute(
        text('SELECT * FROM "User" WHERE userID = :uid'),
        {"uid": uid}
    ).fetchone()

    return render_template('settings.html', user=user)



@app.route('/add-weight-entry', methods=['GET', 'POST'])
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
            return render_template('weightEntry.html', success = True)
        except Exception as e:
            return f"Error adding weight log: {str(e)}"
        
    return render_template('weightEntry.html')

@app.route('/weightlog', methods=['GET', 'POST'])
def weightlog():
    if 'userid' not in session:
        return redirect(url_for('login'))

    uid = session['userid']

    entries = db.session.execute(
        text('SELECT * FROM "weightlog" WHERE userID = :uid ORDER BY date DESC'),
        {"uid": uid}
    ).fetchall()

    return render_template('weightlog.html', entries=entries)

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
        #  Update FoodLog totals
        db.session.execute(
            text("""
                UPDATE "foodlog"
                SET totalCalories = totalCalories + :cal,
                    totalFats = totalFats + :fat,
                    totalCarbs = totalCarbs + :carb,
                    totalProteins = totalProteins + :pro
                WHERE entryid = :eid
            """),
            {
                "cal": calories,
                "fat": fats,
                "carb": carbs,
                "pro": proteins,
                "eid": entryid
            }
        )

        db.session.commit()
        return render_template("foodEntry.html", success=True)

    return render_template("foodEntry.html")


@app.route('/foodlog', methods=['GET', 'POST'])
def foodlog():
    if 'userid' not in session:
        return redirect(url_for('login'))

    uid = session['userid']
    today = date.today()

    # Get today's food entries for the user
    entries = db.session.execute(
        text("""
            SELECT fe.*
            FROM "foodentry" fe
            JOIN "foodlog" fl ON fe.entryid = fl.entryid
            WHERE fl.userid = :uid AND fl.date = :today
        """),
        {"uid": uid, "today": today}
    ).fetchall()

    # Get like total macros and calories for day 
    totals = db.session.execute(
        text("""
            SELECT 
                SUM(calories) AS total_calories,
                SUM(proteins) AS total_proteins,
                SUM(fats) AS total_fats,
                SUM(carbs) AS total_carbs
            FROM "foodentry" fe
            JOIN "foodlog" fl ON fe.entryid = fl.entryid
            WHERE fl.userid = :uid AND fl.date = :today
        """),
        {"uid": uid, "today": today}
    ).fetchone()
    
    return render_template("foodLog.html", food_entries=entries, totals=totals)

@app.route('/caloricPlan', methods=['GET', 'POST'])
def caloric_plan():
    if 'userid' not in session:
        return redirect(url_for('login'))

    uid = session['userid']

    if request.method == 'POST':
        goal = request.form['goal']
        weekly_diff = float(request.form['weekly_diff'])

        # Step 1: Fetch user details
        user = db.session.execute(
            text("""
                SELECT height, currentWeight, gender, age
                FROM "User"
                WHERE userID = :uid
            """),
            {"uid": uid}
        ).fetchone()

        height = user.height
        weight = user.currentweight
        gender = user.gender
        age = user.age

        #  Calculate BMR (got from web)
        if gender == "Male":
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

        #alories based on goal
        calorie_adjustment = (weekly_diff * 3500) / 7

        if goal == "Lose":
            recommended = int(bmr - calorie_adjustment)
        elif goal == "Gain":
            recommended = int(bmr + calorie_adjustment)
        else:
            recommended = int(bmr)

        # Step 4: Calculate recommended macros
        rec_protein = int((recommended * 0.25) / 4)   # 4 kcal/g
        rec_carbs = int((recommended * 0.50) / 4)     # 4 kcal/g
        rec_fats = int((recommended * 0.25) / 9)      # 9 kcal/g

        # Step 5: Check if CaloricPlan exists
        plan = db.session.execute(
            text("SELECT * FROM \"caloricplan\" WHERE userID = :uid"),
            {"uid": uid}
        ).fetchone()

        if plan:
            # Update existing plan
            db.session.execute(
                text("""
                    UPDATE "caloricplan"
                    SET recCalories = :cal,
                        recProtein = :pro,
                        recCarbs = :carb,
                        recFats = :fat,
                        goalType = :goal
                    WHERE userID = :uid
                """),
                {
                    "cal": recommended,
                    "pro": rec_protein,
                    "carb": rec_carbs,
                    "fat": rec_fats,
                    "goal": goal,
                    "uid": uid
                }
            )
        else:
            # Insert new plan
            db.session.execute(
                text("""
                    INSERT INTO "caloricplan"(userID, recCalories, recProtein, recCarbs, recFats, goalType)
                    VALUES (:uid, :cal, :pro, :carb, :fat, :goal)
                """),
                {
                "uid": uid,
                "cal": recommended,
                "pro": rec_protein,
                "carb": rec_carbs,
                "fat": rec_fats,
                "goal": goal
                }
            )

        db.session.commit()

        return render_template(
    'caloricPlan.html',
    success=True,
    recommended=recommended,
    carbs=rec_carbs,
    protein=rec_protein,
    fats=rec_fats
)

    return render_template('caloricPlan.html')


@app.route('/statistics')
def statistics():
    if 'userid' not in session:
        return redirect(url_for('login'))

    uid = session['userid']

    # 1. Get weight logs
    weights = db.session.execute(
        text('SELECT weight, date FROM weightlog WHERE userID = :uid ORDER BY date ASC'),
        {"uid": uid}
    ).fetchall()

    if len(weights) >= 2:
        total_weight_change = round(weights[-1].weight - weights[0].weight, 2)
        days = (weights[-1].date - weights[0].date).days
        weight_change_per_week = round(total_weight_change / (days / 7), 2) if days > 0 else "N/A"
    else:
        total_weight_change = "N/A"
        weight_change_per_week = "N/A"

    # 2. Get caloric average
    food_logs = db.session.execute(
        text('SELECT totalcalories FROM foodlog WHERE userID = :uid AND totalcalories IS NOT NULL'),
        {"uid": uid}
    ).fetchall()

    if food_logs:
        total_calories = sum(log.totalcalories for log in food_logs)
        caloric_average = round(total_calories / len(food_logs), 2)
    else:
        caloric_average = "N/A"

    # 3. Get recommended calories from caloricPlan
    plan = db.session.execute(
        text('SELECT recCalories FROM caloricplan WHERE userID = :uid'),
        {"uid": uid}
    ).fetchone()

    new_recommended_calories = plan.reccalories if plan else "N/A"

    return render_template(
        'statistics.html',
        total_weight_change=total_weight_change,
        caloric_average=caloric_average,
        weight_change_per_week=weight_change_per_week,
        new_recommended_calories=new_recommended_calories
    )
    
@app.route('/weight_chart.png')
def weight_chart():
    uid = session.get('userid')
    weights = WeightLog.query.filter_by(userid=uid).order_by(WeightLog.date).all()

    dates = [log.date for log in weights]
    values = [log.weight for log in weights]

    key = generate_cache_key(dates + values)
    img_path = f"static/weight_chart_{uid}.png"
    cache_path = f"static/weight_chart_{uid}.key"

    if not is_cache_valid(cache_path, key):
        # Generate chart
        plt.figure(figsize=(8, 5))
        plt.plot(dates, values, marker='o', linestyle='-', color='blue')
        plt.title("Weight Tracking Over Time")
        plt.xlabel("Date")
        plt.ylabel("Weight (kg)")
        plt.xticks(rotation=45)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.tight_layout()
        plt.savefig(img_path)
        plt.close()
        update_cache_file(cache_path, key)

    return send_file(img_path, mimetype='image/png')

@app.route('/caloric_chart.png')
def caloric_chart():
    uid = session.get('userid')

    # Group total calories by date
    result = db.session.execute(
        text("""
            SELECT fl.date, SUM(fe.calories) AS total
            FROM foodentry fe
            JOIN foodlog fl ON fe.entryid = fl.entryid
            WHERE fl.userid = :uid
            GROUP BY fl.date
            ORDER BY fl.date
        """), {"uid": uid}
    ).fetchall()

    if not result or len(result) == 0:
        # Return a default blank chart or image saying "No data yet"
        plt.figure(figsize=(8, 4))
        plt.text(0.5, 0.5, 'No calorie data yet', fontsize=14, ha='center')
        plt.axis('off')
        img_path = f"static/caloric_chart_{uid}_blank.png"
        plt.savefig(img_path)
        plt.close()
        return send_file(img_path, mimetype='image/png')

    dates = [row.date.strftime('%Y-%m-%d') for row in result]
    totals = [row.total for row in result]

    key = generate_cache_key(totals)
    img_path = f"static/caloric_chart_{uid}.png"
    cache_path = f"static/caloric_chart_{uid}.key"

    if not is_cache_valid(cache_path, key):
        plt.figure(figsize=(9, 5))
        plt.plot(dates, totals, marker='o', linestyle='-', color='orange')
        plt.title("Daily Total Caloric Intake")
        plt.xlabel("Date")
        plt.ylabel("Calories")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(img_path)
        plt.close()
        update_cache_file(cache_path, key)

    return send_file(img_path, mimetype='image/png')


if __name__ == '__main__':
    with app.app_context():
        test_database_conc()
    app.run(port = 5001,debug=True)

