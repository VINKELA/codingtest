from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_rest_paginate import Pagination


app = Flask(__name__)
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
app.config["SECRET_KEY"] = "precious_two"
app.config["SECURITY_PASSWORD_SALT"] = "precious"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine = create_engine('sqlite://', echo=False)
Base = declarative_base()

db = SQLAlchemy(app)
ma = Marshmallow(app)
pagination = Pagination(app, db)

# table for Users
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False, unique=True)
    def __repr__(self):
        return '<Users %r>' % self.name



# table for projects
class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.Text(80), nullable=False)
    completed = db.Column(db.Boolean(), nullable=True)
    user_stories = db.Column(db.Text(80), nullable=True)

    def __repr__(self):
        return '<Projects %r>' % self.name


# table for actions
class Actions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'),
        nullable=False)
    description = db.Column(db.Text(80), nullable=False)
    note = db.Column(db.Text(80), nullable=False)

    def __repr__(self):
        return '<Actions %r>' % self.key

        
#for formatting object as json
class Users_schema(ma.ModelSchema):
    class Meta:
        fields = ("id", "name","password")
        Model = Users 

class Projects_schema(ma.ModelSchema):
    class Meta:
        fields = ("id", "name", "description", "note", "user_stories")
        Model = Projects 

class Actions_schema(ma.ModelSchema):
    class Meta:
        fields = ("id", "project_id","description","note")
        Model = Actions 
