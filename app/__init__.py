from flask import Flask
from .routes.home_routes import home
from .routes.auth_routes import auth
from .routes.admin_routes import admin
from .routes.user_routes import user

from .db import db, login_manager
from .models import User, ParkingLot, ParkingSpot, Reservation

from dotenv import load_dotenv
import os

load_dotenv() 

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    app.register_blueprint(home)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(user)

    return app
