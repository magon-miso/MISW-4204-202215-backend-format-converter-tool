from email.policy import default
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
#from marshmallow import fields, Schema
#from enum import Enum

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128))
    newformat = db.Column(db.String(5))
    user = db.Column(db.Integer, db.ForeignKey("user.id"))
    status = db.Column(db.Enum("uploaded", "processed", name='statusEnum'))
    upload_date = db.Column(db.DateTime)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    email = db.Column(db.String(250))
    role = db.Column(db.Enum("ADMIN", "USER", name='RoleUser'))
    tasks = db.relationship('Task', cascade='all, delete, delete-orphan')


class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        include_relationships = True
        load_instance = True

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
