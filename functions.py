from model import app
from itsdangerous import URLSafeTimedSerializer

# generate confirmation token given user
def generate_confirmation_token(user):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(user, salt=app.config['SECURITY_PASSWORD_SALT'])
