import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from models import db, User, Person, Planet, Vehicle, FavPerson, FavPlanet, FavVehicle

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'lux'

    admin = Admin(app, name='StarWars API', template_mode='bootstrap4')

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Person, db.session))
    admin.add_view(ModelView(Planet, db.session))
    admin.add_view(ModelView(Vehicle, db.session))
    admin.add_view(ModelView(FavPerson, db.session))
    admin.add_view(ModelView(FavPlanet, db.session))
    admin.add_view(ModelView(FavVehicle, db.session))