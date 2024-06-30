from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_cors import CORS
from flask_migrate import Migrate





db=SQLAlchemy()

def create_app():
    app=Flask(__name__, template_folder='templates')
    app.secret_key="dont share"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./database.db'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from routes import create_routes
    create_routes(app,db)

    migrate=Migrate(app,db)
    return app



