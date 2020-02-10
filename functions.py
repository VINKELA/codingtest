from model import app, Projects, Actions
from itsdangerous import URLSafeTimedSerializer
from flask_restful import abort

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


# generate confirmation token given user
def generate_confirmation_token(user):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(user, salt=app.config['SECURITY_PASSWORD_SALT'])

def abort_if_project_doesnt_exist(project_id):
    project = Projects.query.filter_by(id=project_id).first()
    if  not project:
        abort(404, message="Project with id = {} doesn't exist".format(project_id))

def abort_if_action_doesnt_exist(action_id):
    actions = Actions.query.filter_by(id=action_id).first()
    if  not actions:
        abort(404, message="Action with id {} doesn't exist".format(action_id))

# allowed files
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
