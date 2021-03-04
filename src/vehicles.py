from flask import Blueprint, current_app, request, jsonify
from models import Vehicle
from serializer import VehicleSchema

from utils import APIException
from marshmallow import ValidationError


vehicles_bp = Blueprint('vehicles_bp', __name__)


@vehicles_bp.route('/vehicles', methods=['GET'])
def getAllVehicles():
    page = request.args.get("page", default = 1, type = int)
    limit = request.args.get("limit", default = 10, type = int)

    vehicleSchema = VehicleSchema(many=True, only=["id", "name", "url"])

    vehicles = Vehicle.query\
        .order_by(Vehicle.id.asc())\
        .paginate(page, limit, error_out=False)

    vehiclesSerialized = vehicleSchema.dump(vehicles.items)

    prevUrl = request.base_url + "?page=" + str(vehicles.prev_num)
    nextUrl = request.base_url + "?page=" + str(vehicles.next_num)
    
    return jsonify({
        "total_records": vehicles.total,
        "total_pages": vehicles.pages, 
        "previous": prevUrl if vehicles.prev_num is not None and vehicles.prev_num < vehicles.pages else None,
        "next": nextUrl if vehicles.has_next else None,
        "hasPrev": True if vehicles.prev_num is not None and vehicles.prev_num < vehicles.pages else False,
        "hasNext": vehicles.has_next,
        "results":  vehiclesSerialized
    }), 200


@vehicles_bp.route('/vehicles/<int:id>', methods=['GET'])
def getVehicleById(id):
    vehicleQuery = Vehicle.query.get(id)
    
    if vehicleQuery is None: raise APIException("Vehicle not found", 400)
    else: return jsonify(VehicleSchema(exclude=["url"]).dump(vehicleQuery)), 200


@vehicles_bp.route('/vehicles', methods=['POST'])
def addVehicle():
    if not request.data or request.is_json is not True:
        raise APIException('Missing JSON object', status_code=405)

    vehicleSchema = VehicleSchema()

    try:
        vehicle = vehicleSchema.load(request.json)
    except ValidationError as err:
        raise APIException(err.messages, status_code=400)

    current_app.db.session.add(vehicle)
    current_app.db.session.commit()

    return jsonify(), 201


@vehicles_bp.route('/vehicles/<int:id>', methods=['PUT'])
def updateVehicleById(id):
    vehicle = Vehicle.query.filter(Vehicle.id == id)

    if vehicle.first() is None: raise APIException("Vehicle not found", 400)
    else:
         if request.json is not None and len(request.json) > 0:
            vehicle.update(request.json)
            current_app.db.session.commit()

    return jsonify(), 204


@vehicles_bp.route('/vehicles/<int:id>', methods=['DELETE'])
def deleteVehicle(id):
    vehicle = Vehicle.query.get(id)

    if vehicle is None: raise APIException("Vehicle not found", 400)
    else:
        current_app.db.session.delete(vehicle)
        current_app.db.session.commit()
    
    return jsonify(), 204
