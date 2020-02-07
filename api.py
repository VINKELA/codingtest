from flask import Flask,session
from functions import generate_confirmation_token
from model import app, db, Users, Projects, Actions, Users_schema, Projects_schema, Actions_schema
from sqlalchemy import and_
from flask import jsonify
from flask import Flask, flash, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash


from flask_restful import reqparse, abort, Api, Resource
from flask_restful import fields, marshal_with


api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('username')
parser.add_argument('password')

class Create_user(Resource):
    def post(self):
        args = parser.parse_args()
        username = args['username']
        password = args['password']
        if username == "":
            abort(404, message="please choose a username")
        new_user = username.lower()
        current = Users.query.filter_by(name=new_user).first()
        if current:
            abort(404, message="{} already exist. please choose another username".format(new_user))
        if password == "":
            abort(404, message = "please choose a password")
        if len(password) < 6:
            abort(404, message = "please choose a password that has up to 5 or more letters")    
        user = Users(name=new_user, password = generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return jsonify({'Success':"{} registered successfully".format(new_user)})

class Auth(Resource):
    def post(self):
        args = parser.parse_args()
        username = args['username']
        password = args['password']
        if username == "":
            abort(404, message="please provide your username")
        username = username.lower()
        if password == "":
            abort(404, message = "please provide your password")
        user = Users.query.filter_by(name=username).first()
        if not user:
            abort(404, message = "username or password incorrect")
        if not check_password_hash(user.password, password):
            abort(404, message ="username or password incorrect")
        token = generate_confirmation_token(user.name)
        return jsonify({'token':"{}".format(token)})

api.add_resource(Create_user,'/users/register')
api.add_resource(Auth,'/users/auth')


if __name__ == '__main__':
    app.run(debug=True)

