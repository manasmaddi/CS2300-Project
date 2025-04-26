import psycopg2

conn = None
cur = None

try:
    conn = psycopg2.connect("postgresql://postgres.txngvsfxynpnqutzjove:dbproject1234@aws-0-us-east-1.pooler.supabase.com:6543/postgres")
    
    print("connected")
    cur = conn.cursor()

    cur.execute('''
        INSERT INTO "user" (userID, name, email, password, height, startingWeight, currentWeight, goalWeight)
        VALUES (1, 'John Doe', 'john@example.com', 123456, 180, 85.0, 80.5, 75.0)
    ''')
    conn.commit()
    print("All sample data inserted successfully!")

except Exception as e:
    print("Error:", e)

finally:
    if cur:
        cur.close()
    if conn:
        conn.close()
