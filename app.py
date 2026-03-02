from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE = 'database.db'

# helper to get database connection

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# initialize database with required tables

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # users table for admin
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    # contacts
    cur.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    # reviews
    cur.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    # orders (for trust page counter)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detail TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()

    # seed admin user if not exists
    cur.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if cur.fetchone() is None:
        print('Seeding admin user with default password "admin"')
        pw = generate_password_hash('admin')
        cur.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', ('admin', pw))
        conn.commit()
    conn.close()

# run once at startup
init_db()

# seed the database with realistic sample reviews if it's empty
# using the provided list of common names.  This helps the reviews page look
# populated during development without fake "playerXX" usernames.

def seed_reviews_if_empty():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) as count FROM reviews')
    if cur.fetchone()['count'] < 50:
        names = [
            'Ahsan', 'Hamad', 'Ali', 'Bilal', 'Umar', 'Fahad', 'Hassan', 'Zain',
            'Daniyal', 'Saad', 'Ahmed', 'Salman', 'Rehan', 'Kamran', 'Usman',
            'Imran', 'Asim', 'Noman', 'Shahzaib', 'Farhan', 'Rizwan', 'Aqib',
            'Junaid', 'Adnan', 'Kashif',
            # optional female names for variety
            'Ayesha', 'Fatima', 'Hina', 'Sana', 'Mehwish', 'Iqra', 'Areeba',
            'Hira', 'Zoya', 'Saba', 'Mahnoor', 'Rabia', 'Noor', 'Sidra', 'Amna',
            'Laiba', 'Sarah', 'Bushra', 'Kinza', 'Samina',
            # extra to reach 50
            'Iman', 'Rida', 'Saima', 'Shiza', 'Mehreen'
        ]
        import random
        for i in range(50):
            name = random.choice(names)
            rating = random.randint(3, 5)
            message = f"Great service! Rating {rating}."
            created_at = datetime.now().isoformat()
            cur.execute(
                'INSERT INTO reviews (name,rating,message,created_at) VALUES (?,?,?,?)',
                (name, rating, message, created_at)
            )
        conn.commit()
    conn.close()

# call seeder
seed_reviews_if_empty()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        message = request.form.get('message', '').strip()
        if not name or not message:
            flash('Name and message are required', 'danger')
            return redirect(url_for('contact'))
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO contacts (name,message,created_at) VALUES (?,?,?)',
                    (name, message, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        flash('Your message has been sent!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        rating = request.form.get('rating', '').strip()
        message = request.form.get('message', '').strip()
        try:
            rating = int(rating)
        except ValueError:
            rating = 0
        if not name or not message or rating < 1 or rating > 5:
            flash('Please provide valid name, rating (1-5) and message', 'danger')
        else:
            cur.execute('INSERT INTO reviews (name,rating,message,created_at) VALUES (?,?,?,?)',
                        (name, rating, message, datetime.now().isoformat()))
            conn.commit()
            flash('Review submitted!', 'success')
        return redirect(url_for('reviews'))
    cur.execute('SELECT * FROM reviews ORDER BY created_at DESC')
    all_reviews = cur.fetchall()
    conn.close()
    return render_template('reviews.html', reviews=all_reviews)

@app.route('/trust')
def trust():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) as count FROM orders')
    total_orders = cur.fetchone()['count']
    conn.close()
    return render_template('trust.html', total_orders=total_orders)

# admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cur.fetchone()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session['admin'] = username
            flash('Logged in successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash('Logged out', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM reviews ORDER BY created_at DESC')
    reviews_list = cur.fetchall()
    cur.execute('SELECT * FROM contacts ORDER BY created_at DESC')
    contacts_list = cur.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', reviews=reviews_list, contacts=contacts_list)

@app.route('/admin/review/delete/<int:rid>')
def admin_delete_review(rid):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM reviews WHERE id = ?', (rid,))
    conn.commit()
    conn.close()
    flash('Review deleted', 'info')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
