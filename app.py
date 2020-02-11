import os
from flask import Flask,session
from functions import generate_confirmation_token, abort_if_project_doesnt_exist, abort_if_action_doesnt_exist, allowed_file
from model import app, db, Users, Projects, Actions, Users_schema, Projects_schema, Actions_schema, pagination
from flask import jsonify
from flask import Flask, flash, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_restful import reqparse, abort, Api, Resource
from flask_restful import fields, marshal_with
from sqlalchemy import and_
from werkzeug.utils import secure_filename


api = Api(app)
# file folder
UPLOAD_FOLDER = 'upload'
# configure upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# maximum file size
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# for selecting arguments
parser = reqparse.RequestParser()
parser.add_argument('password')
parser.add_argument('name')
parser.add_argument('description')
parser.add_argument('id')
parser.add_argument('completed')
parser.add_argument('user_stories')
parser.add_argument('note')
parser.add_argument('search')
parser.add_argument('limit')
parser.add_argument('offset')

#fields
project_fields = {
    'name': fields.String,
    'description': fields.String,
    'id': fields.Integer,
    'completed': fields.Boolean,
    'user_stories': fields.String
}

# welcome page
class Welcome(Resource):
    def get(self):
        return jsonify({"greetings": "Welcome","program":"VGGvirtualinternship", "project":"coding test", "submitted_by":"kelvin orji", "full_name":"orji kalu kelvin", "email":"orjikalukelvin@gmail.com","track":"python", "status_code": 200})

# create new user
class Create_user(Resource):
    def post(self):
        args = parser.parse_args()
        username = args['name']
        password = args['password']
        if not  username:
            abort(404, message="please choose a name")
        new_user = username.lower()
        current = Users.query.filter_by(name=new_user).first()
        if current:
            abort(404, message="{} already exist. please choose another name".format(new_user))
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
        username = args['name']
        password = args['password']
        if not username:
            abort(404, message="please provide your username")
        username = username.lower()
        if not password:
            abort(404, message = "please provide your password")
        user = Users.query.filter_by(name=username).first()
        if not user:
            abort(404, message = "name or password incorrect")
        if not check_password_hash(user.password, password):
            abort(404, message ="name or password incorrect")
        token = generate_confirmation_token(user.name)
        return jsonify({'token':"{}".format(token), 'status_code': 200})

# class for projects
class Project(Resource):
    # create a new project
    def post(self):
        args = parser.parse_args()
        project_name = args['name']
        project_description = args['description']
        if not project_name:
            abort(404, message="please choose a name for your project")
        project_name = project_name.lower()
        project = Projects.query.filter_by(name=project_name).first()
        if project:
            abort(404, message="{} already exist. please choose another name for your project".format(project_name))
        if not project_description:
            abort(404, message = "please describe your project")
        project = Projects(name=project_name, description= project_description)
        db.session.add(project)
        db.session.commit()
        return jsonify({'message':"{} added successfully".format(project_name), 'status_code': '201'})
    
    # Retrieve all projects
    def get(self):
        args = parser.parse_args()
        search_word = args['search']
        offset = args['offset']
        limit = args['limit']
        # if search word is provided
        if search_word:
            search = "%{}%".format(search_word)
            project = Projects.query.filter(Projects.name.like(search)).all()
        # set pagination 
        elif limit and offset:
            app.config['PAGINATE_PAGE_SIZE'] = limit
            app.config['PAGINATE_PAGE_PARAM'] = offset
            return pagination.paginate(Projects, project_fields)
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
        project_name = args['name']
        project_description = args['description']
        if not project_name and not project_description: 
            abort(404, message="No changes specified")
        project = Projects.query.filter_by(id=project_id).first()
        if project_name:
            name_check = Projects.query.filter_by(name=project_name).first()
            if name_check:
                abort(404, message="name {} already exist".format(project_name))
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
        project = Projects.query.filter_by(id=project_id).first()
        if project.completed:
            abort(404, message = "completed already updated")
        project.completed = True
        db.session.add(project)
        db.session.commit()
        return jsonify({'message': 'changes made successfully', 'status_code':'201'})
    # delete project with given id 
    def delete(self, project_id):
        abort_if_project_doesnt_exist(project_id)
        Projects.query.filter_by(id=project_id).delete()
        db.session.commit()
        return jsonify({'message': 'project deleted successfully', 'status_code': '201'})


# Create a new action under an existing project
class Action(Resource):
    # create new action with project id
    def post(self, project_id):
        abort_if_project_doesnt_exist(project_id)
        args = parser.parse_args()
        action_description = args['description']
        action_note = args['note']
        if not action_description:
            abort(404, message = "please describe your action")
        if not action_note:
            abort(404, message = "please give some notes on action")
        action = Actions(projects_id = project_id, description=action_description, note = action_note)
        db.session.add(action)
        db.session.commit()
        return jsonify({'message':" Action added successfully", 'status_code':'201'}) 
    # get all actions with given project id
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
        actions = Actions.query.filter_by(id=action_id).first()
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
        abort_if_action_doesnt_exist(action_id)
        action = Actions.query.filter(and_(Actions.projects_id==project_id, Actions.id == action_id))
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
        action = Actions.query.filter(and_(Actions.projects_id==project_id, Actions.id == action_id)).first()
        if action_description:
            if action.description != action_description:
                action.description = action_description
        if action_note:
            if action_note != action.note:
                action.note = action_note
        db.session.add(action)
        db.session.commit()
        return jsonify({'message': 'changes made successfully', 'status_code': '201'})
    
    # Delete action with project id and action id
    def delete(self, project_id, action_id):
        abort_if_project_doesnt_exist(project_id)
        abort_if_action_doesnt_exist(action_id)
        action = Actions.query.filter(and_(Actions.projects_id==project_id, Actions.id == action_id)).delete()
        db.session.commit()
        return jsonify({'message': 'Action deleted successfully', 'status_code':'201'})


        
#upload user stories files to server and save location to string to database
class Upload_files(Resource):
    def put(self, project_id):
        if 'file' not in request.files:
            abort(404, message="No file part in the request")
        file = request.files['file']
        if file.filename == '':
            abort(404, message="No file selected for uploading")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #path to file
            path = app.config['UPLOAD_FOLDER'] +'/' + filename
            file.save(path)
            project = Projects.query.filter_by(id=project_id).first()
            project.user_stories = path
            db.session.add(project)
            db.session.commit()
            return jsonify({'message':'file successfully uploaded!', 'status_code':'201'})
        else:
            abort(400, message="file type not allowed")

# Endpoints
api.add_resource(Welcome,'/')
api.add_resource(Create_user,'/users/register')
api.add_resource(Auth,'/users/auth')
api.add_resource(Project_crud, '/projects/<project_id>')
api.add_resource(Project, '/projects')
api.add_resource(All_actions, '/actions')
api.add_resource(Single_action, '/actions/<action_id>')
api.add_resource(Action, '/projects/<project_id>/actions')
api.add_resource(Action_crud, '/projects/<project_id>/actions/<action_id>')
api.add_resource(Upload_files, '/projects/<project_id>/upload')

if __name__ == '__main__':
    app.run(debug=True)

