from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    skills = db.Column(db.String(255), nullable=True)
    field_of_work = db.Column(db.String(50), nullable=True)
    avatar = db.Column(db.String(255), nullable=True, default='default_avatar.png')

    def __repr__(self):
        return f"<User {self.name}>"

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', backref='projects')
    image = db.Column(db.String(255), nullable=True)
    case_file = db.Column(db.String(255), nullable=True)
    project_details = db.Column(db.Text, nullable=True)
    def __repr__(self):
        return f"<Project {self.title}>"

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Связь с проектом
    project = db.relationship('Project', backref=db.backref('messages', lazy=True))
    # Связь с пользователем
    user = db.relationship('User', backref=db.backref('messages', lazy=True))

    def __repr__(self):
        return f"<Message {self.id}>"