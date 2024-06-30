from flask import render_template, request
from models import Users


def create_routes(app,db):
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

