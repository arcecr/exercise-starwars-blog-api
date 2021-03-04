from flask import Blueprint, current_app, request, jsonify
from models import Planet
from serializer import PlanetSchema

from utils import APIException
from marshmallow import ValidationError


planets_bp = Blueprint('planets_bp', __name__)


@planets_bp.route('/planets', methods=['GET'])
def getAllPlanets():
    page = request.args.get("page", default = 1, type = int)
    limit = request.args.get("limit", default = 10, type = int)

    planetsSchema = PlanetSchema(many=True, only=["id", "name", "url"])

    planets = Planet.query\
        .order_by(Planet.id.asc())\
        .paginate(page, limit, error_out=False)

    planetsSerialized = planetsSchema.dump(planets.items)

    prevUrl = request.base_url + "?page=" + str(planets.prev_num)
    nextUrl = request.base_url + "?page=" + str(planets.next_num)
    
    return jsonify({
        "total_records": planets.total,
        "total_pages": planets.pages, 
        "previous": prevUrl if planets.prev_num is not None and planets.prev_num < planets.pages else None,
        "next": nextUrl if planets.has_next else None,
        "hasPrev": True if planets.prev_num is not None and planets.prev_num < planets.pages else False,
        "hasNext": planets.has_next,
        "results":  planetsSerialized
    }), 200


@planets_bp.route('/planets/<int:id>', methods=['GET'])
def getPlanetById(id):
    planetQuery = Planet.query.get(id)
    
    if planetQuery is None: raise APIException("Planet not found", 400)
    else: return jsonify(PlanetSchema(exclude=["url"]).dump(planetQuery)), 200


@planets_bp.route('/planets', methods=['POST'])
def addPlanet():
    if not request.data or request.is_json is not True:
        raise APIException('Missing JSON object', status_code=405)

    planetSchema = PlanetSchema()

    try:
        planet = planetSchema.load(request.json)
    except ValidationError as err:
        raise APIException(err.messages, status_code=400)

    current_app.db.session.add(planet)
    current_app.db.session.commit()

    return jsonify(), 201


@planets_bp.route('/planets/<int:id>', methods=['PUT'])
def updateOrDeletePlanet(id):
    planet = Planet.query.filter(Planet.id == id)

    if planet.first() is None: raise APIException("Planet not found", 400)
    else:
    
        if request.json is not None and len(request.json) > 0:
            planet.update(request.json)
            current_app.db.session.commit()

    return jsonify(), 204


@planets_bp.route('/planets/<int:id>', methods=['DELETE'])
def deletePlanet(id):
    planet = Planet.query.get(id)

    if planet is None: raise APIException("Planet not found", 400)
    else:
        current_app.db.session.delete(planet)
        current_app.db.session.commit()
    
    return jsonify(), 204
