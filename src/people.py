from flask import Blueprint, current_app, request, jsonify
from models import Person
from serializer import PersonSchema

from utils import APIException
from marshmallow import ValidationError


people_bp = Blueprint('people_bp', __name__)


@people_bp.route('/people', methods=['GET'])
def getAllPeople():
    page = request.args.get("page", default = 1, type = int)
    limit = request.args.get("limit", default = 10, type = int)

    peopleSchema = PersonSchema(many=True, only=["id", "name", "url"])

    people = Person.query\
        .order_by(Person.id.asc())\
        .paginate(page, limit, error_out=False)

    peopleSerialized = peopleSchema.dump(people.items)

    prevUrl = request.base_url + "?page=" + str(people.prev_num)
    nextUrl = request.base_url + "?page=" + str(people.next_num)
    
    return jsonify({
        "total_records": people.total,
        "total_pages": people.pages, 
        "previous": prevUrl if people.prev_num is not None and people.prev_num < people.pages else None,
        "next": nextUrl if people.has_next else None,
        "hasPrev": True if people.prev_num is not None and people.prev_num < people.pages else False,
        "hasNext": people.has_next,
        "results":  peopleSerialized
    }), 200


@people_bp.route('/people/<int:id>', methods=['GET'])
def getPersonById(id):
    personQuery = Person.query.get(id)
    
    if personQuery is None: raise APIException("Person not found", 400)
    else: return jsonify(PersonSchema(exclude=["url"]).dump(personQuery)), 200


@people_bp.route('/people', methods=['POST'])
def addPerson():
    if not request.data or request.is_json is not True:
        raise APIException('Missing JSON object', status_code=405)

    personSchema = PersonSchema()

    try:
        person = personSchema.load(request.json)
    except ValidationError as err:
        raise APIException(err.messages, status_code=400)

    current_app.db.session.add(person)
    current_app.db.session.commit()

    return jsonify(), 201


@people_bp.route('/people/<int:id>', methods=['PUT'])
def updatePersonById(id):
    person = Person.query.filter(Person.id == id)

    if person.first() is None: raise APIException("Person not found", 400)
    else:
         if request.json is not None and len(request.json) > 0:
            person.update(request.json)
            current_app.db.session.commit()

    return jsonify(), 204


@people_bp.route('/people/<int:id>', methods=['DELETE'])
def deletePerson(id):
    person = Person.query.get(id)

    if person is None: raise APIException("Person not found", 400)
    else:
        current_app.db.session.delete(person)
        current_app.db.session.commit()
    
    return jsonify(), 204
