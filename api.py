from flask import Flask,session
from functions import generate_confirmation_token, abort_if_project_doesnt_exist, abort_if_action_doesnt_exist
from model import app, db, Users, Projects, Actions, Users_schema, Projects_schema, Actions_schema
from flask import jsonify
from flask import Flask, flash, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_restful import reqparse, abort, Api, Resource
from flask_restful import fields, marshal_with
from sqlalchemy import and_


api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('username')
parser.add_argument('password')
parser.add_argument('project_name')
parser.add_argument('project_description')
parser.add_argument('project_id')
parser.add_argument('user_story')
parser.add_argument('description')
parser.add_argument('note')

# welcome
class Welcome(Resource):
    def get(self):
        return jsonify({"greetings": "Welcome", "status_code": 200})

# create new user
class Create_user(Resource):
    def post(self):
        args = parser.parse_args()
        username = args['username']
        password = args['password']
        if not  username:
            abort(404, message="please choose a username")
        new_user = username.lower()
        current = Users.query.filter_by(name=new_user).first()
        if current:
            abort(404, message="{} already exist. please choose another username".format(new_user))
        if not password:
            abort(404, message = "please choose a password")
        if len(password) < 6:
            abort(404, message = "please choose a password that has up to 5 or more letters")    
        user = Users(name=new_user, password = generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "{} registered successfully".format(new_user), 'status_code': "200"})
''' 
validates user's name and password
if successful returns a token
else return error
'''
class Auth(Resource):
    def post(self):
        args = parser.parse_args()
        username = args['username']
        password = args['password']
        if not username:
            abort(404, message="please provide your username")
        username = username.lower()
        if not password:
            abort(404, message = "please provide your password")
        user = Users.query.filter_by(name=username).first()
        if not user:
            abort(404, message = "username or password incorrect")
        if not check_password_hash(user.password, password):
            abort(404, message ="username or password incorrect")
        token = generate_confirmation_token(user.name)
        return jsonify({'token':"{}".format(token), 'status_code': 200})

# class for projects
class Project(Resource):
    # create a new project
    def post(self):
        args = parser.parse_args()
        project_name = args['project_name']
        project_description = args['project_description']
        if not project_name:
            abort(404, message="please choose a name for your project")
        project_name = project_name.lower()
        project = Projects.query.filter_by(name=project_name).first()
        if project:
            abort(404, message="{} already exist. please choose another name for your project".format(project_name))
        if not project_description:
            abort(404, message = "please describe your project")
        if len(project_description) < 10:
            abort(404, message = "please describe your project with more words")    
        project = Projects(name=project_name, description= project_description)
        db.session.add(project)
        db.session.commit()
        return jsonify({'message':"{} added successfully".format(project_name), 'status_code': '201'})
    
    # Retrieve all projects
    def get(self):
        args = parser.parse_args()
        search_word = args['search']
        # if search word is provided
        if search_word:
            search = "%{}%".format(search_word)
            project = Projects.query.filter(Post.name.like(search)).all()
        else:
            project = Projects.query.all()
        ProjectSchema= Projects_schema(many=True)
        output = ProjectSchema.dump(project)  
        return jsonify({'Projects': output, 'status_code':'200'})


# perform create, read, update and delete on existing projects
class Project_crud(Resource):
    # Retrieve a single project by id
    def get(self, project_id):
        abort_if_project_doesnt_exist(project_id)
        project = Projects.query.filter_by(id=project_id).first()
        ProjectSchema= Projects_schema()
        output = ProjectSchema.dump(project)  
        return jsonify({'Project':output, 'status_code': 200})

    # update an existing project
    def put(self, project_id):
        abort_if_project_doesnt_exist(project_id)
        args = parser.parse_args()
        project_name = args['project_name']
        project_description = args['project_description']
        if not project_name and not project_description: 
            abort(404, message="No changes specified")
        project = Projects.query.filter_by(id=project_id).first()
        if project_name:
            if project.name != project_name:
                project.name = project_name
        if project_description:
            if project.description != project_description:
                project.description = project_description
        db.session.add(project)
        db.session.commit()
        return  jsonify({'message':'changes made successfully', 'status_code': '201'})


    #update the completed property of project with given project_id
    def patch(self, project_id):
        abort_if_project_doesnt_exist(project_id)
        args = parser.parse_args()
        user_story = args['user_story']
        if not user_story:
            abort(404, message="No changes made")
        project = Projects.query.filter_by(id=project_id).first()

        if user_story != project.user_stories:
            project.user_stories = user_story
        db.session.add(project)
        db.session.commit()
        return jsonify({'message': 'changes made successfully', 'status_code':'201'})




    def delete(self, project_id):
        abort_if_project_doesnt_exist(project_id)
        Projects.query.filter_by(id=project_id).delete()
        db.session.commit()
        return jsonify({'message': 'project deleted successfully', 'status_code': '201'})


# Create a new action under an existing project
class Action(Resource):
    def post(self, project_id):
        args = parser.parse_args()
        action_description = args['description']
        action_note = args['note']
        if not action_description:
            abort(404, message = "please describe your action")
        if not action_note:
            abort(404, message = "please describe your action")

        if len(action_description) < 10:
            abort(404, message = "please describe your action with more words")    
        action = Actions(projects_id = project_id, description=action_description, note = action_note)
        db.session.add(action)
        db.session.commit()
        return jsonify({'message':" Action added successfully", 'status_code':'201'}) 
    
    def get(self, project_id):
        action = Actions.query.filter_by(projects_id=project_id)
        ActionSchema= Actions_schema(many=True)
        output = ActionSchema.dump(action)  
        return jsonify({'Actions':output, 'status_code': '200'})


# Retrieve all the actions
class All_actions(Resource):
    def get(self):
        all_actions = Actions.query.all()
        ActionSchema= Actions_schema(many=True)
        output = ActionSchema.dump(all_actions)  
        return jsonify({'Actions':output, 'status_code': '200'})

# Retrieves a single action by id
class Single_action(Resource):
    def get(self, action_id):
        actions = Projects.query.filter_by(id=action_id).first()
        if  not actions:
            abort(404, message="Action {} doesn't exist".format(action_id))
        ActionSchema= Actions_schema()
        output = ActionSchema.dump(actions)  
        return jsonify({'Actions':output, 'status_code': '200'})

#Perform CRUD  on Actions given project_id and action_id
class Action_crud(Resource):
    # Retrieve a single action by id
    def get(self, project_id, action_id):
        abort_if_project_doesnt_exist(project_id)
        abort_if_action_doesnt_exist
        action = Actions.query.filter_by(projects_id=project_id)
        ActionSchema= Actions_schema(many=True)
        output = ActionSchema.dump(action)  
        return jsonify({'Actions':output, 'status_code': '200'})

    # update a given action for a particular project
    def put(self, project_id, action_id):
        abort_if_project_doesnt_exist(project_id)
        abort_if_action_doesnt_exist(action_id)
        args = parser.parse_args()
        action_description = args['description']
        action_note = args['note']
        if not action_note and not action_description:
            abort(404, message="No changes made")
        action = Actions.query.filter_by(id=action_id).first()
        if action_description:
            if action.description != action_description:
                action.description = action_description
        if action_note:
            if action.note != action_note:
                action.note = action_note
        db.session.add(action)
        db.session.commit()
        return jsonify({'message': 'changes made successfully', 'status_code': '201'})

    def delete(self, project_id, action_id):
        abort_if_project_doesnt_exist(project_id)
        abort_if_action_doesnt_exist(action_id)
        action = Actions.query.filter_by(id = action_id).delete()
        db.session.commit()
        return jsonify({'message': 'Action deleted successfully', 'status_code':'201'})

api.add_resource(Welcome,'/')
api.add_resource(Create_user,'/users/register')
api.add_resource(Auth,'/users/auth')
api.add_resource(Project_crud, '/projects/<project_id>')
api.add_resource(Project, '/projects')
api.add_resource(All_actions, '/actions')
api.add_resource(Single_action, '/actions/<action_id>')
api.add_resource(Action, '/projects/<project_id>/actions')
api.add_resource(Action_crud, '/projects/<project_id>/actions/<action_id>')


if __name__ == '__main__':
    app.run(debug=True)

