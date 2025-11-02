from flask import Blueprint, jsonify, request, abort
from socks import method
from database import DataBase
import json
import random
from datetime import datetime

STATUS_MAP = {
    "new": "New",
    "in progress": "In Progress",
    "pending review": "Pending Review",
    "completed": "Completed",
}
ALLOWED_STATUSES = list(STATUS_MAP.values())


user_bp = Blueprint('user', __name__)

dbase = DataBase()
db = dbase.db
tasks = db['taskmanager']

@user_bp.route('/addSomet', methods=['POST'])
def add_something():
    task = {
        "name": "Moshe" ,
        "date": datetime.now().strftime("%d/%m/%Y"),
        "task": "Buy groceries",
        "points": 10,
        "status": "pending",
        "id": random.randint(1, 1000)
    }
    inserted = tasks.insert_one(task)
    return jsonify({"massage": "task added successfully"}), 201


@user_bp.route('/getAllTasks', methods=['GET'])
def get_all_tasks():
    try:
        cursor = tasks.find({})

        tasks_list = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            tasks_list.append(doc)

        return jsonify({"message": "ok", "tasks": tasks_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@user_bp.route('/getTasksByName', methods=['GET'])
def get_tasks_by_name():
    try:
        #http://192.168.1.177:5000/getTasksByName?name=Moshe
        name = request.args.get('name')
        if not name:
            return jsonify({"error": "Missing required parameter: name"}), 400


        cursor = tasks.find({"name": name})

        tasks_list = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            tasks_list.append(doc)

        if not tasks_list:
            return jsonify({"error": f"No tasks found for name '{name}'"}), 404

        return jsonify({"message": "ok", "tasks": tasks_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route('/addTask', methods=['POST'])
def add_task():
    try:
        data = request.get_json()

        required_fields = ["name", "task", "points"]
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required field(s): name, task, points"}), 400

        raw_status = str(data.get("status", "New")).strip()
        normalized = STATUS_MAP.get(raw_status.lower())

        if not normalized:
            return jsonify({
                "error": f"Status '{raw_status}' is not allowed",
                "allowed_statuses": ALLOWED_STATUSES
            }), 400

        unique_id = random.randint(1, 1000)
        while tasks.find_one({"id": unique_id}):
            unique_id = random.randint(1, 1000)

        task = {
            "name": data["name"],
            "date": datetime.now().strftime("%d/%m/%Y"),
            "task": data["task"],
            "points": data["points"],
            "status": normalized,
            "id": unique_id
        }

        inserted = tasks.insert_one(task)
        task["_id"] = str(inserted.inserted_id)

        return jsonify({"message": "task added successfully", "task": task}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route('/deleteTask/<int:task_id>', methods =['DELETE'])
def delete_task(task_id):
    try:
        result = tasks.delete_one({"id": task_id})
        if result.deleted_count == 0:
            return  jsonify({"ERROR":f"Task with id {task_id} not found"}), 400

        return jsonify({"message":"task deleted successfully", "id": task_id}), 200
    except Exception as e:
        return jsonify({"ERROR":str(e)}),500


@user_bp.route('/getTasksByDate', methods=['GET'])
def get_tasks_by_date():
    try:
        date_str = request.args.get('date')
        if not date_str:
            return jsonify({"error": "Missing required parameter: date", "hint": "Expected format: DD/MM/YYYY (e.g., 13/09/2025)" }), 400

        try:
            datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            return jsonify({
                "error": "Invalid date format", "hint": "Use DD/MM/YYYY (e.g., 13/09/2025)"}), 400
        cursor = tasks.find({"date": date_str})

        tasks_list = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            tasks_list.append(doc)

        if not tasks_list:
            return jsonify({"error": f"No tasks found for date '{date_str}'"}), 404

        return jsonify({"message": "ok", "tasks": tasks_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@@user_bp.route('/changeStatus', methods=['PATCH'])
def change_status():
    try:
        data = request.get_json(silent=True) or {}
        if 'id' not in data or 'status' not in data:
            return jsonify({
                "error": "Missin    xg required field(s): id, status",
                "hint": {
                    "body_example": {"id": 123, "status": "In Progress"},
                    "allowed_statuses": ALLOWED_STATUSES
                }
            }), 400

        try:
            task_id = int(data['id'])
        except (TypeError, ValueError):
            return jsonify({"error": "Field 'id' must be an integer"}), 400

        raw_status = str(data['status']).strip()
        normalized = STATUS_MAP.get(raw_status.lower())
        if not normalized:
            return jsonify({
                "error": f"Status '{raw_status}' is not allowed",
                "allowed_statuses": ALLOWED_STATUSES
            }), 400

        existing = tasks.find_one({"id": task_id})
        if not existing:
            return jsonify({"error": f"Task with id {task_id} not found"}), 404

        if existing.get("status") == normalized:
            existing["_id"] = str(existing["_id"])
            return jsonify({
                "message": "no change (status already set)",
                "task": existing
            }), 200

        tasks.update_one({"id": task_id}, {"$set": {"status": normalized}})
        updated = tasks.find_one({"id": task_id})
        if updated and "_id" in updated:
            updated["_id"] = str(updated["_id"])

        return jsonify({
            "message": "status updated successfully",
            "task": updated
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route('/Hello', methods=['GET'])
def print_hello():
    return "Hello World", 200
