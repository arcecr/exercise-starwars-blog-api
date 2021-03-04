from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError

from models import User, Person, Planet, Vehicle

ma = Marshmallow()

def configure(app):
    ma.init_app(app)


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True


class PersonSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Person
        include_fk = True
        load_instance = True
    
    url = ma.URLFor('people_bp.getPersonById', values=dict(id='<id>'))


class PlanetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Planet
        include_fk = True
        load_instance = True
    
    url = ma.URLFor('planets_bp.getPlanetById', values=dict(id='<id>'))


class VehicleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Vehicle
        include_fk = True
        load_instance = True

    url = ma.URLFor('vehicles_bp.getVehicleById', values=dict(id='<id>'))