import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from models import configure as config_db, User
from serializer import configure as config_ma

from utils import APIException, generate_sitemap
from admin import setup_admin


app = Flask(__name__)

app.url_map.strict_slashes = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secret'

CORS(app) 

config_db(app) # Database
config_ma(app) # Marshmallow 

MIGRATE = Migrate(app, app.db)

jwt = JWTManager(app)

@jwt.user_identity_loader
def user_identity_lookup(user): return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


setup_admin(app)

# Error Handling
@app.errorhandler(APIException)
def handle_invalid_usage(error): return jsonify(error.to_dict()), error.status_code

# Generate Sitemap
@app.route('/')
def sitemap(): return generate_sitemap(app)


from users import users_bp
app.register_blueprint(users_bp)


from people import people_bp
app.register_blueprint(people_bp)

from planets import planets_bp
app.register_blueprint(planets_bp)

from vehicles import vehicles_bp
app.register_blueprint(vehicles_bp)


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)