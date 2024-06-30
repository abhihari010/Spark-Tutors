from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime, timezone




app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db=SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50),nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.Integer, nullable=False)


class Message(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date=db.Column(db.DateTime, default=datetime.now(timezone.utc))
    content=db.Column(db.String(100000), nullable=False)
    
class UnknownMessage(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), nullable=False)
    unkowncontent=db.Column(db.String(100000), nullable=False)
    date=db.Column(db.DateTime, default=datetime.now(timezone.utc))




@app.route('/')
def homepage():
    return render_template("home.html")

@app.route('/offer')
def offer():
    return render_template("offer.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    return render_template("register.html")

@app.route('/logout')
def logout():
    return

@app.route('/crash')
def main():
    raise Exception()

if __name__== '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
