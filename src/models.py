from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def configure(app):
    db.init_app(app)
    app.db = db


class Person(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    birth_year = db.Column(db.String(25), nullable=False)
    gender = db.Column(db.String(25), nullable=False)
    height = db.Column(db.Integer, nullable=False)
    mass = db.Column(db.Integer, nullable=False)
    skin_color = db.Column(db.String(25), nullable=False)
    eye_color = db.Column(db.String(25), nullable=False)
    hair_color = db.Column(db.String(25), nullable=False)

    users_favorite = db.relationship("FavPerson", backref="person", cascade="all, delete")

    def __repr__(self):
        return "<Person(id='%s', name='%s')>" % (self.id, self.name)


class Planet(db.Model):
    __tablename__ = 'planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    diameter = db.Column(db.Integer, nullable=False)
    gravity = db.Column(db.String(25), nullable=False)
    terrain = db.Column(db.String(50), nullable=False)
    climate = db.Column(db.String(50), nullable=False)
    surface_water = db.Column(db.String(50), nullable=False)
    population = db.Column(db.Integer, nullable=False)
    rotation_period = db.Column(db.Integer, nullable=True)
    orbital_period = db.Column(db.Integer, nullable=True)

    users_favorite = db.relationship("FavPlanet", backref="planet", cascade="all, delete")

    def __repr__(self):
        return "<Planet(id='%s', name='%s')>" % (self.id, self.name)


class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    manufacturer = db.Column(db.String(80), nullable=False)
    vehicle_class = db.Column(db.String(50), nullable=False)
    passengers = db.Column(db.Integer, nullable=False)
    cost_in_credits = db.Column(db.Integer, nullable=False)
    max_atmosphering_speed = db.Column(db.Integer, nullable=False)
    length = db.Column(db.Float, nullable=False)
    crew = db.Column(db.Integer, nullable=False)
    cargo_capacity = db.Column(db.Integer, nullable=False)
    consumables = db.Column(db.String(50), nullable=False)

    users_favorite = db.relationship("FavVehicle", backref="vehicle", cascade="all, delete")

    def __repr__(self):
        return "<Vehicle(id='%s', name='%s')>" % (self.id, self.name)


#####################################


class FavPlanet(db.Model):
    __tablename__ = 'favplanets'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'))
    planetId = db.Column(db.Integer, db.ForeignKey('planets.id'))

    user = db.relationship("User")

    def __repr__(self):
        return "<FavPlanet(planet='%s')>" % self.planetId


class FavPerson(db.Model):
    __tablename__ = 'favpersons'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'))
    personId = db.Column(db.Integer, db.ForeignKey('people.id'))

    user = db.relationship("User")

    def __repr__(self):
        return "<FavPerson(person='%s')>" % self.personId


class FavVehicle(db.Model):
    __tablename__ = 'favvehicles'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'))
    vehicleId = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    
    user = db.relationship("User")

    def __repr__(self):
        return "<FavVehicle(vehicle='%s')>" % self.vehicleId


#####################################


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    favorite_persons = db.relationship("FavPerson")
    favorite_planets = db.relationship("FavPlanet")
    favorite_vehicles = db.relationship("FavVehicle")
    
    def __repr__(self):
        return "<User(name='%s')>" % self.name