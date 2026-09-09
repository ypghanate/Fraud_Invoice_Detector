# # diff between MYSQL and SQLite

# CREATE TABLE products (
#     id INT AUTO_INCREMENT PRIMARY KEY, #AUTO_INCRMENT in between
#     product_name VARCHAR(100) NOT NULL,
#     category VARCHAR(50) DEFAULT 'General', # no var_char
#     price DECIMAL(10, 2) NOT NULL,
#     created_at DATETIME DEFAULT CURRENT_TIMESTAMP
# );

# CREATE TABLE products (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     product_name TEXT NOT NULL,
#     category TEXT DEFAULT 'General',
#     price REAL NOT NULL,
#     created_at TEXT DEFAULT CURRENT_TIMESTAMP
# );

# CREATE TABLE users (
#     id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
#     username VARCHAR(50) NOT NULL,
#     created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
# );


# SELECT CONCAT(product_name, ' (', category, ') - $', price) AS product_label FROM products;
# SELECT product_name || ' (' || category || ') - $' || price AS product_label FROM products;

# SELECT * FROM products WHERE created_at >= NOW() - INTERVAL 1 DAY;
# SELECT * FROM products WHERE created_at >= datetime('now', '-1 day');
# SELECT * FROM users WHERE created_at >= NOW() - INTERVAL '7 days'


# INSERT INTO products (id, product_name, price) 
# VALUES (1, 'Wireless Mouse', 29.99)
# ON DUPLICATE KEY UPDATE price = VALUES(price);

# INSERT INTO products (id, product_name, price) 
# VALUES (1, 'Wireless Mouse', 29.99)
# ON CONFLICT(id) DO UPDATE SET price = excluded.price;


# SELECT json_extract(metadata, '$.theme') FROM user_settings;

# SELECT metadata->>'theme' FROM user_settings;
# SELECT * FROM user_settings WHERE metadata @> '{"theme": "dark"}';






# import json
# import sqlite3

# conn = sqlite3.connect('cleaner.db')
# cursor = conn.cursor()

# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS clean (
#         id INTEGER PRIMARY KEY,
#         full_name TEXT,
#         email TEXT,
#         phone TEXT
#     )
# ''')

# with open('raw_data.json', 'r') as file:
#     data = json.load(file)

# cleaned_data = []

# for res in data:
#     raw_id = res.get('user_id')
#     if not raw_id:
#         continue
#     user_id = int(raw_id)

#     full_name = res.get('full_name', '').strip().title()

#     contact = res.get('contact_info', {})
#     email = contact.get('email', '').lower()
#     phone = contact.get('phone', 'N/A')

#     cleaned_data.append((user_id, full_name, email, phone))

# cursor.executemany('''
# INSERT INTO clean(id, full_name, email, phone) VALUES(?, ?, ?, ?)
# ''', cleaned_data)

# conn.commit()

# cursor.execute('SELECT * FROM clean')
# rows = cursor.fetchall()

# for row in rows:
#     print(row)

# conn.close()
    




# import json
# import mysql.connector as mysql
# import psycopg2
# from psycopg2.extras import Json

# # --- 1. MySQL Connection Setup ---
# mydb = mysql.connect(
#     host="localhost", port=3306, user="bob", password="123", database="mydb"
# )

# cur = mydb.cursor()

# # Create MySQL Users table
# cur.execute(
#     """
# CREATE TABLE IF NOT EXISTS users (
#     user_id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(100) NOT NULL,
#     email VARCHAR(100) UNIQUE NOT NULL,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
# """
# )

# # Create MySQL Orders table (Added missing user_id column definition)
# cur.execute(
#     """
# CREATE TABLE IF NOT EXISTS orders (
#     order_id INT AUTO_INCREMENT PRIMARY KEY,
#     user_id INT,
#     FOREIGN KEY (user_id) REFERENCES users(user_id),
#     amount DECIMAL(10,2),
#     order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
#     status VARCHAR(20) DEFAULT 'pending'
# );
# """
# )

# mydb.commit()  # Fixed variable name from conn.commit()


# # --- 2. PostgreSQL Connection Setup ---
# pg_conn = psycopg2.connect(
#     host="localhost",
#     port=5432,
#     user="postgres",
#     password="123",
#     dbname="analytics_db",
# )
# pg_cur = pg_conn.cursor()

# # Create Postgres Analytics table
# pg_cur.execute(
#     """
# CREATE TABLE IF NOT EXISTS order_analytics (
#     analytics_id SERIAL PRIMARY KEY,
#     order_id INT UNIQUE NOT NULL,
#     user_id INT NOT NULL,
#     metadata JSONB NOT NULL,
#     order_date TIMESTAMP NOT NULL
# );
# """
# )
# pg_conn.commit()


# # --- 3. MySQL Helper Functions ---
# def create_user(name, email):
#     query = """INSERT INTO users(name, email) VALUES(%s, %s)"""
#     cur.execute(query, (name, email))
#     mydb.commit()
#     return cur.lastrowid


# def create_order(user_id, amount, status="pending"):
#     query = """INSERT INTO orders(user_id, amount, status) VALUES(%s, %s, %s)"""
#     cur.execute(query, (user_id, amount, status))
#     mydb.commit()
#     return cur.lastrowid


# def fetch_mysql_orders():
#     query = """SELECT order_id, user_id, amount, status, order_date FROM orders"""
#     cur.execute(query)
#     orders = cur.fetchall()  # Fixed method name from cur.fetch_all
#     return orders


# # --- 4. PostgreSQL Data ETL Functions ---
# def insert_data(orders):
#     pg_query = """
#         INSERT INTO order_analytics (order_id, user_id, metadata, order_date)
#         VALUES (%s, %s, %s, %s)
#         ON CONFLICT (order_id) DO NOTHING
#     """

#     for row in orders:
#         order_id, user_id, amount, status, order_date = row

#         # Converted Decimal 'amount' to float so it can be JSON serialized safely
#         metadata = {"amount": float(amount), "status": status}

#         pg_cur.execute(
#             pg_query, (order_id, user_id, Json(metadata), order_date)
#         )

#     pg_conn.commit()


# def calculate():
#     query = (
#         """SELECT SUM((metadata->>'amount')::numeric) FROM order_analytics"""
#     )
#     pg_cur.execute(query)
#     result = pg_cur.fetchone()  # Fixed function call syntax
#     total = result[0] if result else 0
#     return total


# def window_func():
#     # Fixed SQL syntax: string extraction, comma, PARTITION BY, ORDER BY, and FROM clause
#     query = """
#         SELECT 
#             (metadata->>'amount')::numeric AS amount,
#             RANK() OVER (
#                 PARTITION BY user_id
#                 ORDER BY order_id
#             ) AS result_alias
#         FROM order_analytics;
#     """
#     pg_cur.execute(query)
#     return pg_cur.fetchall()



from pymongo import MongoClient
uri = "mongodb://localhost:27017/"
client = MongoClient(uri)

db = client['myDatabase']
logs = db['app_logs']

log = {
    "user_id": "usr_1024",
    "event_type": "LOGIN_FAILED",
    "timestamp": datetime.now(timezone.utc),
    "metadata": {
        "reason": "Invalid password",
        "attempt_count": 3,
        "device": "Android"
    }
}

result = logs.insert_one(log)

return list(logs_collection.find(query))

def find_docs(logs):
    for data in logs:
        res = data[event_type].get()
        if res == "LOGIN_FAILED":
            return data

def find_user_docs(logs):
    for data in logs:
        res = data[user_id].get()
        if res == "user_id":
            return data