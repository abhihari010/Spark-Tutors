from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import pyrebase
import os

dotenv_path = 'c:/Users/abhih/project1/secret.env'
if not os.path.exists(dotenv_path):
    raise FileNotFoundError(f"{dotenv_path} file not found")
load_dotenv(dotenv_path)

config = {
    "apiKey": os.getenv('API_KEY'),
    "authDomain": os.getenv('AUTH_DOMAIN'),
    "databaseURL": os.getenv('DATABASE_URL'),
    "projectId": os.getenv('PROJECT_ID'),
    "storageBucket": os.getenv('STORAGE_BUCKET'),
    "messagingSenderId": os.getenv('MESSAGING_SENDER_ID'),
    "appId": os.getenv('APP_ID'),
    "measurementId": os.getenv('MEASUREMENT_ID')
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

app = Flask(__name__, template_folder='firstwebsite/templates', static_folder="firstwebsite/static")
app.secret_key = "sachu"
app.permanent_session_lifetime = timedelta(minutes=10)

def get_user_id_token():
    if "user" in session:
        return session["user"]["idToken"]
    return None

def is_email_verified():
    if "user" in session:
        user = auth.refresh(session["user"]["refreshToken"])
        session["user"] = user
        return user['user']['emailVerified']
    return False

@app.route('/')
def homepage():
    return render_template("home.html")

@app.route('/offer')
def offer():
    return render_template("offer.html")

@app.route("/appointment", methods=['GET', 'POST'])
def appointment():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to be logged in to schedule an appointment.", category="error")
        return redirect("/login")

    if not is_email_verified():
        flash("Please verify your email to schedule an appointment.", category="error")
        return redirect("/")

    id_token = get_user_id_token()
    if not id_token:
        flash("You are not authenticated", category="error")
        return redirect("/login")

    if request.method == "POST":
        username = request.form.get("username")
        date = request.form.get("date")
        time = request.form.get("time")

        user = db.child("users").child(user_id).get(token=id_token).val()

        if not user:
            flash("User not found", category="error")
            return render_template("appointment.html")

        if username != user["username"]:
            flash("Username does not match", category="error")
            return render_template("appointment.html")

        try:
            valid_date = datetime.strptime(date, '%Y-%m-%d').date()
            valid_time = datetime.strptime(time, '%I:%M %p').time()
            valid_datetime = datetime.combine(valid_date, valid_time)
            current_datetime = datetime.now()

            if valid_datetime <= current_datetime:
                flash("You cannot schedule an appointment in the past", category="error")
                return render_template("appointment.html")

        except ValueError:
            flash("Invalid date or time format", category="error")
            return redirect("/")

        appt = db.child("appointments").order_by_child("datetime").equal_to(valid_datetime.isoformat()).get(token=id_token)
        if appt.each():
            flash("An appointment already exists at this time. Please choose another time.", category="error")
            return render_template("appointment.html")

        new_appt = {
            "user_id": user_id,
            "username": username,
            "datetime": valid_datetime.isoformat()
        }
        db.child("appointments").push(new_appt, token=id_token)
        flash("Your appointment was successfully scheduled. Check your schedule to confirm!", category="success")
        return redirect("/")
    else:
        return render_template("appointment.html")

@app.route('/appointments', methods=['GET'])
def get_appointments():
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'booked_times': []})

    try:
        appt_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'booked_times': []})

    id_token = get_user_id_token()
    appointments = db.child("appointments").order_by_child("datetime").start_at(appt_date.isoformat()).end_at(appt_date.isoformat() + "\uf8ff").get(token=id_token)
    booked_times = [datetime.fromisoformat(appt.val()["datetime"]).strftime('%I:%M %p') for appt in appointments.each()]
    return jsonify({'booked_times': booked_times})

@app.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        if "user_id" in session:
            user_id = session["user_id"]
            id_token = get_user_id_token()
            user = db.child("users").child(user_id).get(token=id_token).val()
            email = user["email"]
            message = request.form.get("message")

            if not message:
                flash("Please provide a valid message.", category="error")
                return render_template("contact.html")
            elif len(message) < 4:
                flash("Not enough content.", category="error")
                return render_template("contact.html")
            else:
                new_message = {
                    "email": email,
                    "content": message,
                    "date": datetime.now(timezone.utc).isoformat()
                }
                db.child("messages").push(new_message, token=id_token)
                flash("Message sent.", category="success")
                return redirect("/")
        else:
            email = request.form.get("email")
            name = request.form.get("name")
            message = request.form.get("message")

            if len(email) < 3:
                flash("Please enter a valid email.", category="error")
                return render_template("contact.html")
            elif not name:
                flash("Please enter a valid name.", category="error")
                return render_template("contact.html")
            elif not message or len(message) < 4:
                flash("Please provide a valid message.", category="error")
                return render_template("contact.html")
            else:
                new_message = {
                    "email": email,
                    "name": name,
                    "content": message,
                    "date": datetime.now(timezone.utc).isoformat()
                }
                db.child("messages").push(new_message)
                flash("Message sent. Check your email within 1-3 business days for a reply!", category="success")
                return redirect("/")

    return render_template("contact.html")

@app.route('/plans')
def plans():
    return render_template("plans.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    # Retrieve registration message from session
    if 'message' in session and 'category' in session:
        flash(session['message'], category=session['category'])
        session.pop('message', None)
        session.pop('category', None)

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = request.form.get("remember")

        if not email or not password:
            flash("Please enter a valid email and password", category="error")
            return render_template("login.html")

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            user_info = auth.get_account_info(user['idToken'])
            if not user_info['users'][0]['emailVerified']:
                flash("Please verify your email before logging in.", category="error")
                return render_template("login.html")

            session["user_id"] = user["localId"]
            session["user"] = user  # Save the whole user object
            flash("Logged In!", category="success")
            return redirect("/")
        except Exception as e:
            error_message = str(e)
            if "EMAIL_NOT_FOUND" in error_message or "INVALID_PASSWORD" in error_message:
                flash("Invalid email or password", category="error")
            else:
                flash(f"Error: {error_message}", category="error")
            return render_template("login.html")

    return render_template("login.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        name = request.form.get("name")
        grade = request.form.get("grade")
        username = request.form.get("username")

        if len(email) < 3:
            flash("Please enter a valid email.", category="error")
            return render_template("register.html")
        elif len(username) < 5:
            flash("Username must be longer than 5 characters.", category="error")
            return render_template("register.html")
        elif len(password) < 8:
            flash("Password is not long enough.", category="error")
            return render_template("register.html")
        elif password != confirmation:
            flash("Passwords must match.", category="error")
            return render_template("register.html")
        elif not name:
            flash("Please enter a valid name", category="error")
            return render_template("register.html")
        elif not grade or not grade.isdigit() or int(grade) < 8 or int(grade) > 12:
            flash("Please enter a valid grade", category="error")
            return render_template("register.html")

        try:
            user = auth.create_user_with_email_and_password(email, password)
            auth.send_email_verification(user['idToken']) 

            user_data = {
                "email": email,
                "username": username,
                "name": name,
                "grade": grade
            }
            db.child("users").child(user["localId"]).set(user_data, token=user["idToken"])
            session['message'] = "Account successfully created! Please verify your email before logging in."
            session['category'] = "success"
            return redirect("/login")
        except Exception as e:
            error_message = str(e)
            print(f"Error creating account: {error_message}")
            flash(f"Error creating account: {error_message}", category="error")
            return render_template("register.html")

    return render_template("register.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "success")
    return redirect("/login")

@app.route('/account', methods=["GET", "POST"])
def account():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    id_token = get_user_id_token()
    if not id_token:
        flash("You are not authenticated", category="error")
        return redirect("/login")

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        name = request.form.get("name")
        grade = request.form.get("grade")

        if not username or not email or not name or not grade:
            flash("Please provide valid details.", category="error")
            return render_template("account.html")

        user_updates = {
            "username": username,
            "email": email,
            "name": name,
            "grade": grade
        }
        db.child("users").child(user_id).update(user_updates, token=id_token)
        flash("Account details updated successfully!", category="success")
        return redirect("/")

    user = db.child("users").child(user_id).get(token=id_token).val()
    return render_template("account.html", user=user)

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to be logged in to view your schedule.", category="error")
        return redirect("/login")

    id_token = get_user_id_token()
    if not id_token:
        flash("You are not authenticated", category="error")
        return redirect("/login")

    if request.method == "POST":
        appointment_id = request.form.get('appointment_id')
        if not appointment_id:
            flash("Invalid appointment ID.", category="error")
            return redirect("/schedule")

        appointment = db.child("appointments").child(appointment_id).get(token=id_token).val()
        if appointment and appointment["user_id"] == user_id:
            db.child("appointments").child(appointment_id).remove(token=id_token)
            flash("Appointment successfully deleted.", category="success")
        else:
            flash("Appointment not found or you do not have permission to delete it.", category="error")

        return redirect("/schedule")

    appointments = db.child("appointments").order_by_child("user_id").equal_to(user_id).get(token=id_token)
    schedule = [{"id": appt.key(), "datetime": appt.val()["datetime"]} for appt in appointments.each()]
    return render_template("schedule.html", schedule=schedule)

@app.route('/crash')
def main():
    raise Exception()

if __name__ == '__main__':
    app.run(debug=True)
