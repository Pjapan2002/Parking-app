# Parking Management System

A Parking-app for managing four-vehicle parking, built with features like:
- Secure Login System
- Admin & User Dashboards
- Parking Spot Management
- Real-time Booking & History Tracking

## Features:
- User authentication
- Create & manage parking lots and spots
- Reserve & release parking spots
- Auto-calculated cost based on duration
- View reservation history
- Admin user management

---

## Tech Stack:
- **Backend**: Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Frontend**: HTML, Jinja2, Bootstrap 5
- **Database**: SQLite

---

## Project Structure:
```bash
parking-app/
├── app/
│   ├── templates/
│   ├── static/
│   ├── routes/
│   ├── models/
│   └── __init__.py
├── .env
├── requirements.txt
├── run.py
└── README.md
```
---
## Project setup:
```bash
1. Clone the Repository
- git clone https://github.com/your-username/parking-app.git
- cd parking-app

2. Create Virtual Environment
- python -m venv venv
- venv\Scripts\activate ( for Windows )
- source venv/bin/activate ( for Mac/Linux )

3. Install Requirements.txt
- pip install -r requirements.txt

4. Create '.env' file
- SECRET_KEY=your-secret-key
- DATABASE_URL=sqlite:///parking_app.db

5. Initialize the Database
- py db_setup.py

6. Run Application
- py run.py
```
---
