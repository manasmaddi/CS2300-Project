from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Update with your correct database URL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.txngvsfxynpnqutzjove:dbproject1234@aws-0-us-east-1.pooler.supabase.com:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/')
def home():
    return "Welcome to the Fitness Tracker App!"

@app.route('/test-db')
def test_db():
    try:
        conn = db.engine.connect()
        result = conn.execute(text('SELECT 1'))
        conn.close()
        return "Database connected successfully!"
    except Exception as e:
        return f"Database connection failed: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
