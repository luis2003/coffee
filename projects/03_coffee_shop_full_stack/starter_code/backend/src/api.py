import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
import logging
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO (DONE) uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO (DONE) implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    all_drinks = Drink.query.all()
    drinks_list = []
    for drink in all_drinks:
        drinks_list.append(drink.short())
    if len(drinks_list) == 0:
        abort(404)
    return jsonify({
        'success': True,
        'drinks': drinks_list
    })


'''
@TODO (DONE) implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drink-details')
def get_drinks_detail(jwt):
    all_drinks = Drink.query.all()
    drinks_list = []
    for drink in all_drinks:
        drinks_list.append(drink.long())
    if len(drinks_list) == 0:
        abort(404)
    return jsonify({
        'success': True,
        'drinks': drinks_list
    })


'''
@TODO (DONE) implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(jwt):
    drink = request.get_json()
    created_drink = Drink(title=drink['title'], recipe=json.dumps(drink['recipe']))
    try:
        Drink.insert(created_drink)
    except Exception as e:
        logging.exception('An exception occurred while inserting drink')
        abort(422)
    return jsonify({"success": True,
                    "drinks": [{"title": drink['title'],
                                "recipe": drink['recipe']}]})

'''
@TODO (STARTED) implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(jwt, drink_id):
    body = request.get_json()

    try:
        drink_to_patch = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink_to_patch is None:
            abort(404)

        if 'title' in body:
            drink_to_patch.title = str(body.get('title'))

        if 'recipe' in body:
            drink_to_patch.recipe = body.get('recipe')

        drink_to_patch.update()
        updated_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        return jsonify({"success": True,
                        "drinks": updated_drink.long()})

    except Exception as E:
        logging.exception('An exception occurred while updating drink')
        abort(400)


'''
@TODO (DONE) implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    selection = Drink.query.filter(Drink.id == drink_id).all()
    if len(selection) == 0:
        abort(404)
    selection[0].delete()
    return jsonify({"success": True,
                    "deleted": drink_id})

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400
'''
@TODO (DONE) implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def notfound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
