from app import db
from sqlalchemy.sql import func



class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text,nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    grade = db.Column(db.Text, nullable=False)
    messages=db.relationship('Message')

    def __repr__(self):
        return f'Hello {self.name} welcome to Spark Tutors'

class Message(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    content=db.Column(db.Text)
    date=db.Column(db.DateTime(timezone=True), default=func.now())
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'We hear you'