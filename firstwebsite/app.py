from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "sachu"
db = SQLAlchemy(app)
app.permanent_session_lifetime = timedelta(minutes=10)

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False) 
    name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Integer, nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    content = db.Column(db.String(100000), nullable=False)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)



@app.route('/')
def homepage():
    return render_template("home.html")

@app.route('/offer')
def offer():
    return render_template("offer.html")


@app.route("/appointment", methods=['GET', 'POST'])
def appointment():
    if request.method == "POST":
        username=request.form.get("username")
        date=request.form.get("date")
        time=request.form.get("time")

        user = User.query.filter_by(id=session["user_id"]).first()
        
        if not user:
            flash("You are not logged in", category="error")
            return("appointment.html")
        
        if not username:
            flash("Please enter your username", category="error")
            return render_template("appointment.html")
        
        if not date:
            flash("Please enter a date", category="error")
            return render_template("appointment.html")
        
        if not time:
            flash("Please enter a time", category="error")
            return render_template("appointment.html")
        
        if username != user.username:
            flash("Not your username", category="error")
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
        
        appt = Schedule.query.filter_by(date=valid_datetime).first()

        if appt:
            flash("An appointment already exists at this time. Please choose another time.", category="error")
            return render_template("appointment.html")
        
        new_appt = Schedule(email=user.email, date=valid_datetime)
        db.session.add(new_appt)
        db.session.commit()
        flash("Your appointment was succesfully scheduled. Check your schedule to confirm!", category="success")
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

    appointments = Schedule.query.filter(Schedule.date.between(
        datetime.combine(appt_date, datetime.min.time()),
        datetime.combine(appt_date, datetime.max.time())
    )).all()
    
    booked_times = [appt.date.strftime('%I:%M %p') for appt in appointments]
    return jsonify({'booked_times': booked_times})

@app.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        if "user_id" in session:
            user = User.query.filter_by(id=session["user_id"]).first()
            email = user.email
            message = request.form.get("message")
            if not user:
                flash("No user with this id.", category="error")
                return render_template("contact.html")
            elif not message:
                flash("Please provide a valid message.", category="error")
                return render_template("contact.html")
            elif len(message) < 4:
                flash("Not enough content.", category="error")
                return render_template("contact.html")
            else:
                new_message = Message(email=email, content=message)
                db.session.add(new_message)
                db.session.commit()
                flash("Message sent.", category="success")
                return redirect("/")
        else:
            email=request.form.get("email")
            name=request.form.get("name")
            message=request.form.get("message")
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
                new_message = Message(email=email, content=message)
                db.session.add(new_message)
                db.session.commit()
                flash("Message sent. Check your email within 1-3 business days for a reply!", category="success")
                return redirect("/")

    return render_template("contact.html")

@app.route('/plans')
def plans():
    return render_template("plans.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember=request.form.get("remember")

        if not email:
            flash("Please enter a valid email", category="error")
            return render_template("login.html")
        elif not password:
            flash("Please enter a valid password", category="error")
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()
        if user is None:
            flash("Email does not exist", category="error")
            return render_template("login.html")

        if not check_password_hash(user.password, password):
            flash("Password is incorrect", category="error")
            return render_template("login.html")
        
        session.permanent = True
        if remember:
            app.permanent_session_lifetime = timedelta(days=100)
        else:
            app.permanent_session_lifetime = timedelta(minutes=10)

        session["user_id"] = user.id
        flash("Logged In!", category="success")
        return redirect("/")

    return render_template("login.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        name = request.form.get("name")
        grade = int(request.form.get("grade"))
        username=request.form.get("username")


        if len(email) < 3:
            flash("Please enter a valid email.", category="error")
            return render_template("register.html")
        
        elif len(username) < 5:
            flash("Username must be longer than 5 characters.", category="error")
            return render_template("register.html")
        
        elif not password:
            flash("Please enter a valid password.", category="error")
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
        
        elif not grade or grade < 8 or grade > 12:
            flash("Please enter a valid grade", category="error")
            return render_template("register.html")
        
        check_email = User.query.filter_by(email=email).first()
        if check_email:
            flash("Email already exists.", category="error")
            return render_template("register.html")
        
        check_username = User.query.filter_by(username=username).first()
        if check_username:
            flash("Username already exists.", category="error")
            return render_template("register.html")


        hash = generate_password_hash(password)
        new_user = User(email=email, username=username, password=hash, name=name, grade=grade)
        db.session.add(new_user)
        db.session.commit()

        session.permanent = True
        session["user_id"] = new_user.id
        flash("Account Successfully Created!", category="success")
        return redirect("/")

    return render_template("register.html")

@app.route('/logout')
def logout():
    if "user_id" in session:
        user_id = session["user_id"]
        flash("You have been logged out", "success")
    session.clear()
    return redirect("/login")

@app.route('/account', methods=["GET", "POST"])
def account():
    if request.method == "POST":
        username=request.form.get("username")
        email=request.form.get("email")
        name=request.form.get("name")
        grade=request.form.get("grade")

        if not username:
            flash("Please enter a valid username", category="error")
            return("account.html")
        
        if not email:
            flash("Please enter your email", category="error")
            return render_template("account.html")
        
        if not name:
            flash("Please enter your name", category="error")
            return render_template("account.html")
        
        if not grade:
            flash("Please enter your grade", category="error")
            return render_template("account.html")
        
        check_email = User.query.filter_by(email=email).first()
        if check_email:
            flash("Email already exists.", category="error")
            return render_template("register.html")
        
        check_username = User.query.filter_by(username=username).first()
        if check_username:
            flash("Username already exists.", category="error")
            return render_template("register.html")

        
        user = User.query.filter_by(id=session["user_id"]).first()
        user.username = username
        user.email = email
        user.name = name
        user.grade = grade
        db.session.commit()

        flash("Account details updated successfully!", category="success")
        return redirect("/")


    else:
        user = User.query.filter_by(id=session["user_id"]).first()
        return render_template("account.html", user=user)


@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if request.method == "POST":
        if "user_id" not in session:
            flash("You need to be logged in to delete an appointment.", category="error")
            return redirect("/login")
        
        appointment_id = request.form.get('appointment_id')
        if not appointment_id:
            flash("Invalid appointment ID.", category="error")
            return redirect("/schedule")
        
        user = User.query.filter_by(id=session["user_id"]).first()
        if not user:
            flash("User not found", category="error")
            return redirect("/")
        
        appointment = Schedule.query.filter_by(id=appointment_id, email=user.email).first()
        if appointment:
            db.session.delete(appointment)
            db.session.commit()
            flash("Appointment successfully deleted.", category="success")
        else:
            flash("Appointment not found or you do not have permission to delete it.", category="error")
            
        return redirect("/appointment")


    else:
        user = User.query.filter_by(id=session["user_id"]).first()
        if user:
            schedule = Schedule.query.filter_by(email=user.email).all() 
            return render_template("schedule.html", schedule=schedule)
        else:
            flash("User not found", category="error")
            return redirect("/")

@app.route('/crash')
def main():
    raise Exception()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)