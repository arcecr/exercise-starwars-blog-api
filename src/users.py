from flask import Blueprint, current_app, request, jsonify
from models import User, Person, Planet, Vehicle, FavPerson, FavPlanet, FavVehicle
from serializer import UserSchema, PlanetSchema, VehicleSchema, PersonSchema

from utils import APIException
from marshmallow import ValidationError

import datetime

from flask_jwt_extended import create_access_token, jwt_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

users_bp = Blueprint('users_bp', __name__)

@users_bp.route('/user/me', methods=['GET'])
@jwt_required()
def getProfile():
    userQuery = User.query.get(current_user.id)

    if userQuery is None: raise APIException("User not found", 400)
    
    userSchema = UserSchema(only=["name", "email", "username"])

    return jsonify({
        "info": userSchema.dump(userQuery)
    }), 200

@users_bp.route('/user/favorites', methods=['GET'])
@jwt_required()
def getFavoritesByUserId():
    userQuery = User.query.get(current_user.id)

    if userQuery is None: raise APIException("User not found", 400)

    personSchema = PersonSchema(only=["id", "name", "url"])
    planetSchema = PlanetSchema(only=["id", "name", "url"])
    vehicleSchema = VehicleSchema(only=["id", "name", "url"])

    favorite_persons = list(map(lambda x: personSchema.dump(x.person), userQuery.favorite_persons))
    favorite_planets = list(map(lambda x: planetSchema.dump(x.planet), userQuery.favorite_planets))
    favorite_vehicles = list(map(lambda x: vehicleSchema.dump(x.vehicle), userQuery.favorite_vehicles))

    return jsonify({
        "favorites": {
            "people": favorite_persons,
            "planets": favorite_planets,
            "vehicles": favorite_vehicles
        }
    }), 200


@users_bp.route('/user/favorites', methods=['POST'])
@jwt_required()
def addFavoriteByUserId():
    if not request.data or request.is_json is not True: raise APIException('Missing JSON object', status_code=405)

    person_id = request.json.get("person_id", None)
    planet_id = request.json.get("planet_id", None)
    vehicle_id = request.json.get("vehicle_id", None)

    if not person_id and not planet_id and not vehicle_id: raise APIException("person_id, planet_id or vehicle_is is required", status_code=401)

    person_query = Person.query.get(person_id)
    planet_query = Planet.query.get(planet_id)
    vehicle_query = Vehicle.query.get(vehicle_id)

    hasPersonFav = FavPerson.query.filter_by(userId=current_user.id, personId=person_id).one_or_none()
    hasPlanetFav = FavPlanet.query.filter_by(userId=current_user.id, planetId=planet_id).one_or_none()
    hasVehicleFav = FavVehicle.query.filter_by(userId=current_user.id, vehicleId=vehicle_id).one_or_none()

    ##################################################
    if person_id:
        if person_query is None: raise APIException("Doesn't exist this person", 400)
        
        if not hasPersonFav:
            person_favorite = FavPerson(userId=current_user.id, personId=person_id)
            current_app.db.session.add(person_favorite)

    ##################################################
    if planet_id:
        if not planet_query: raise APIException("Doesn't exist this planet", 400)
        
        if not hasPlanetFav:
            planet_favorite = FavPlanet(userId=current_user.id, planetId=planet_id)
            current_app.db.session.add(planet_favorite)

    ##################################################
    if vehicle_id:
        if not vehicle_query: raise APIException("Doesn't exist this vehicle", 400)
        
        if not hasVehicleFav:
            vehicle_favorite = FavVehicle(userId=current_user.id, vehicleId=vehicle_id)
            current_app.db.session.add(vehicle_favorite)
        
    ##################################################

    current_app.db.session.commit()

    return jsonify(), 201


@users_bp.route('/user/favorites', methods=['DELETE'])
@jwt_required()
def deleteUserFavoriteById():
    if not request.data or request.is_json is not True: raise APIException('Missing JSON object', status_code=405)

    person_id = request.json.get("person_id", None)
    planet_id = request.json.get("planet_id", None)
    vehicle_id = request.json.get("vehicle_id", None)

    if not person_id and not planet_id and not vehicle_id: raise APIException("person_id, planet_id or vehicle_is is required", status_code=401)

    hasPersonFav = FavPerson.query.filter_by(userId=current_user.id, personId=person_id).one_or_none()
    hasPlanetFav = FavPlanet.query.filter_by(userId=current_user.id, planetId=planet_id).one_or_none()
    hasVehicleFav = FavVehicle.query.filter_by(userId=current_user.id, vehicleId=vehicle_id).one_or_none()

    ##################################################
    if person_id:
        if not hasPersonFav: raise APIException("Does not exist this favorite in your list", 400)
        current_app.db.session.delete(hasPersonFav)
    
    ##################################################
    if planet_id:
        if not hasPlanetFav: raise APIException("Does not exist this favorite in your list", 400)
        current_app.db.session.delete(hasPlanetFav)

    ##################################################
    if vehicle_id:
        if not hasVehicleFav: raise APIException("Does not exist this favorite in your list", 400)
        current_app.db.session.delete(hasVehicleFav)
    
    ##################################################

    current_app.db.session.commit()

    return jsonify(), 204


@users_bp.route('/users/register', methods=['POST'])
def registerUser():
    if not request.data or request.is_json is not True: raise APIException('Missing JSON object', status_code=405)

    data = request.json
    userSchema = UserSchema()

    try: user = userSchema.load(data)
    except ValidationError as err: raise APIException(err.messages, status_code=400)

    existUsername = User.query.filter_by(username=data.get("username")).first()
    existEmail = User.query.filter_by(email=data.get("email")).first()

    if existUsername: raise APIException("Already exist other user with same username", status_code=409)
    if existEmail: raise APIException("Already exist other user with same email", status_code=409)

    newUser = User()
    newUser.name = data.get("name")
    newUser.email = data.get("email")
    newUser.username = data.get("username")
    newUser.password = generate_password_hash(data.get("password"))

    current_app.db.session.add(newUser)
    current_app.db.session.commit()

    return jsonify(), 201


@users_bp.route('/users/login', methods=['POST'])
def loginUser():
    if not request.data or request.is_json is not True: raise APIException('Missing JSON object', status_code=405)

    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username: raise APIException("Username is required", status_code=401)
    if not password: raise APIException("Password is required", status_code=401)

    user = User.query.filter_by(username=username).one_or_none()

    if not user or not check_password_hash(user.password, password): 
        raise APIException("Wrong username or password", status_code=401)

    expiration = datetime.timedelta(days=3)
    access_token = create_access_token(identity=user, expires_delta=expiration)

    return jsonify({
        "access_token": access_token,
        "expires_token": expiration.total_seconds() * 1000
    }), 200