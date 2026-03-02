Bali FF - Flask Website Project
===============================

Project Description:
-------------------
Bali FF ek Flask-based website hai jo Free Fire services, reviews, contact, trust pages aur admin panel provide karta hai.
Database: SQLite3

Project Structure:
-----------------
BALI FF/
├── app.py             <-- Flask app main file
├── database.db        <-- SQLite database
├── templates/         <-- HTML templates
│     ├── home.html
│     ├── reviews.html
│     ├── contact.html
│     ├── services.html
│     └── trust.html
└── static/            <-- CSS / JS / images
      └── style.css

Dependencies:
-------------
- Python 3.10+
- Flask
- Werkzeug

Create a `requirements.txt` file with:
Flask==2.3.3
Werkzeug==2.3.6

Setup & Run Locally:
--------------------
1. Install dependencies:
   pip install -r requirements.txt

2. Run the app:
   python app.py

3. Open in browser:
   http://127.0.0.1:5000

Free Hosting Deployment (Railway / Render):
------------------------------------------
1. Create a free account on Railway.app or Render.com
2. Push this project to GitHub
3. Connect the GitHub repo to Railway/Render
4. Make sure `requirements.txt` exists
5. Set the start command: python app.py
6. Deploy and access your live website via provided URL

Notes:
------
- If database.db already exists with fake reviews (player32 etc.), delete it before first deploy to seed realistic names.
- Admin login default:
  username: admin
  password: admin

Enjoy your Bali FF website! 🎮🔥
