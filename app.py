from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import pyrebase
import os

dotenv_path = 'c:/Users/abhih/project1/secret.env'
if not os.path.exists(dotenv_path):
    raise FileNotFoundError(f"{dotenv_path} file not found")
load_dotenv(dotenv_path)

api_key = os.getenv('API_KEY')
auth_domain = os.getenv('AUTH_DOMAIN')
database_url = os.getenv('DATABASE_URL')
project_id = os.getenv('PROJECT_ID')
storage_bucket = os.getenv('STORAGE_BUCKET')
messaging_sender_id = os.getenv('MESSAGING_SENDER_ID')
app_id = os.getenv('APP_ID')
measurement_id = os.getenv('MEASUREMENT_ID')


config = {
    "apiKey": api_key,
    "authDomain": auth_domain,
    "databaseURL": database_url,
    "projectId": project_id,
    "storageBucket": storage_bucket,
    "messagingSenderId": messaging_sender_id,
    "appId": app_id,
    "measurementId": measurement_id
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

app = Flask(__name__, template_folder='firstwebsite/templates', static_folder='firstwebsite/static')
app.secret_key = "sachu"
app.permanent_session_lifetime = timedelta(minutes=10)

def get_user_id_token():
    if "user" in session:
        return session["user"]["idToken"]
    return None

def is_email_verified():
    if "user" in session:
        user_info = auth.get_account_info(session["user"]["idToken"])
        return user_info['users'][0]['emailVerified']
    return False

# Routes
@app.route('/')
def homepage():
    return render_template("home.html")

@app.route('/offer')
def offer():
    return render_template("offer.html")

@app.route("/appointment", methods=['GET', 'POST'])
def appointment():
    if request.method == "POST":
        username = request.form.get("username")
        date = request.form.get("date")
        time = request.form.get("time")
        reschedule_id = request.form.get("reschedule_id")

        if "user" not in session:
            flash("You are not logged in", category="error")
            return render_template("appointment.html")

        user = db.child("users").child(session["user"]["localId"]).get().val()
        if not user:
            flash("User not found", category="error")
            return render_template("appointment.html")

        if not username or not date or not time:
            flash("Please fill out all fields", category="error")
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
            return render_template("appointment.html")

        appointments = db.child("appointments").order_by_child("date").equal_to(valid_datetime.isoformat()).get().val()
        if appointments:
            flash("An appointment already exists at this time. Please choose another time.", category="error")
            return render_template("appointment.html")

        new_appt = {
            "user_id": session["user"]["localId"],
            "username": username,
            "date": valid_datetime.isoformat(),
            "zoom_meeting_id": "452 899 0105",
            "tutor" : "Pranav Jithesh"
        }
        db.child("appointments").push(new_appt)

        if reschedule_id:
            db.child("appointments").child(reschedule_id).remove()

        flash("Your appointment was successfully scheduled. Check your schedule to confirm!", category="success")
        return redirect("/")

    reschedule_id = request.args.get("reschedule_id")
    return render_template("appointment.html", reschedule_id=reschedule_id)


@app.route('/appointments', methods=['GET'])
def get_appointments():
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'booked_times': []})

    try:
        appt_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'booked_times': []})

    try:
        appointments = db.child("appointments").order_by_child("date").start_at(appt_date.isoformat()).end_at(appt_date.isoformat() + "\uf8ff").get().val()
        if appointments:
            booked_times = [datetime.fromisoformat(appt["date"]).strftime('%I:%M %p') for appt in appointments.values()]
        else:
            booked_times = []
        return jsonify({'booked_times': booked_times})
    except Exception as e:
        print(f"Error fetching appointments: {str(e)}")
        return jsonify({'booked_times': []})



@app.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        if "user" in session:
            user = db.child("users").child(session["user"]["localId"]).get().val()
            email = user["email"]
            message = request.form.get("message")
            if not user:
                flash("No user with this ID.", category="error")
                return render_template("contact.html")
            elif not message or len(message) < 4:
                flash("Please provide a valid message.", category="error")
                return render_template("contact.html")
            else:
                new_message = {
                    "email": email,
                    "content": message,
                    "date": datetime.now(timezone.utc).isoformat()
                }
                db.child("messages").push(new_message)
                flash("Message sent.", category="success")
                return redirect("/")
        else:
            email = request.form.get("email")
            name = request.form.get("name")
            message = request.form.get("message")
            if not email or len(email) < 3 or not name or not message or len(message) < 4:
                flash("Please fill out all fields with valid information.", category="error")
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

    if 'message' in session and 'category' in session:
        flash(session['message'], category=session['category'])
        session.pop('message', None)
        session.pop('category', None)

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = request.form.get("remember")

        if not email or not password:
            flash("Please fill out all fields", category="error")
            return render_template("login.html")

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            if not auth.get_account_info(user['idToken'])['users'][0]['emailVerified']:
                flash("Please verify your email before logging in", category="error")
                return render_template("login.html")

            session.permanent = True
            if remember:
                app.permanent_session_lifetime = timedelta(days=100)
            else:
                app.permanent_session_lifetime = timedelta(minutes=10)

            session["user"] = user
            session["idToken"] = user['idToken']
            flash("Logged In!", category="success")
            return redirect("/")
        except Exception as e:
            flash("Invalid Username or Password", category="error")
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

        if not email or not username or not password or not name or not grade:
            flash("Please fill out all fields with valid information.", category="error")
            return render_template("register.html")
        if not grade.isdigit():
            flash("Grade must be a number", category="error")
            return render_template("register.html")
        if int(grade) < 8 or int(grade) > 12:
            flash("Sorry, we only take grades 8-12", category="error")
            return render_template("register.html")            
        if len(password) < 8:
            flash("Password too short", category="error")
            return render_template("register.html")             
        if len(email) < 3:
            flash("Invalid Email", category="error")
            return render_template("register.html") 
        if len(username) < 5:
            flash("Username is too short.", category="error")
            return render_template("register.html")           
        if password != confirmation:
            flash("Passwords do not match.", category="error")
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
            db.child("users").child(user["localId"]).set(user_data)
            session['message'] = "Account successfully created! Please verify your email before logging in."
            session['category'] = "success"
            return redirect("/login")
        except Exception as e:
            error_message = str(e)
            if "EMAIL_EXISTS" in error_message:
                flash("This email is already registered. Please log in or use a different email.", category="error")
            else:
                flash(f"Error creating account: {error_message}", category="error")
            return render_template("register.html")

    return render_template("register.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", category="success")
    return redirect("/")


@app.route('/account', methods=["GET", "POST"])
def account():
    if "user" not in session:
        flash("You need to log in first.", category="error")
        return redirect("/login")

    user_id = session["user"]["localId"]
    idToken = session["user"].get("idToken")  

    try:
        user_info = db.child("users").child(user_id).get(idToken).val()
    except Exception as e:
        flash(f"Error fetching user info: {str(e)}", category="error")
        return render_template("account.html")

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        name = request.form.get("name")
        grade = request.form.get("grade")

        if not username or not email or not name or not grade:
            flash("All fields are required.", category="error")
        else:
            try:
                db.child("users").child(user_id).update({
                    "username": username,
                    "email": email,
                    "name": name,
                    "grade": grade
                }, idToken)
                flash("Account details updated successfully!", category="success")
                return redirect("/")
            except Exception as e:
                flash(f"Error updating account details: {str(e)}", category="error")

    return render_template("account.html", user_info=user_info)



@app.route('/schedule', methods=["GET", "POST"])
def schedule():
    if "user" in session:
        user_id = session["user"]["localId"]
        user_info = db.child("users").child(user_id).get().val()
        if not user_info:
            flash("User not found", category="error")
            return redirect("/")

        if request.method == "POST":
            appointment_id = request.form.get("appointment_id")
            if appointment_id:
                db.child("appointments").child(appointment_id).remove()
                flash("Appointment rescheduled. Please choose a new time.", category="success")
                return redirect("/appointment")

        schedule = db.child("appointments").order_by_child("user_id").equal_to(user_id).get().val()
        
        # Format the date for each appointment
        if schedule:
            for key, appointment in schedule.items():
                appointment["formatted_date"] = datetime.fromisoformat(appointment["date"]).strftime('%A, %B %d, %Y at %I:%M %p')
        
        return render_template("schedule.html", schedule=schedule if schedule else {})
    flash("You are not logged in", category="error")
    return redirect("/login")



if __name__ == '__main__':
    app.run(debug=True)
