import json
from flask import Blueprint, jsonify, request, Response
from flask import current_app as app
from project.services.todo import save_todo, fetch_todos
from project.elasticSearch.todo import index_todo 

# Blueprint Configuration
todo_blueprint = Blueprint(
    'todo_blueprint', __name__,
)

@todo_blueprint.route('/list', methods=['GET'])
def get_todos():
    todos = fetch_todos()
    return Response(todos,mimetype="application/json", status=200)

@todo_blueprint.route('/create', methods=['POST'])
def create_todo():
    data = request.get_json(force=True)
    todo = save_todo(data)
    todo_dict = json.loads(todo)
    index_todo(todo_dict)
    return Response(todo,mimetype="application/json", status=201)
