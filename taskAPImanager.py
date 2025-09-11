from flask import Blueprint, jsonify, request, abort
from socks import method
from database import DataBase
import json
import random
from datetime import datetime


user_bp = Blueprint('user', __name__)

dbase = DataBase()
db = dbase.db
tasks = db['taskmanager']

@user_bp.route('/addSomet', methods=['POST'])
def add_something():
    task = {
        "name": "Moshe" ,
        "date": datetime.now().strftime("%d/%m/%Y"),  # תאריך ברמת יום/חודש/שנה
        "task": "Buy groceries",  # שם המשימה
        "points": 10,  # ניקוד/משקל
        "status": "pending",  # סטטוס
        "id": random.randint(1, 1000)  # מזהה רנדומלי 1-1000
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

        required_fields = ["name", "task", "points", "status"]
        if not data or not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required field(s)"}), 400

        task = {
            "name": data["name"],
            "date": datetime.now().strftime("%d/%m/%Y"),
            "task": data["task"],
            "points": data["points"],
            "status": data["status"],
            "id": random.randint(1, 1000)
        }

        inserted = tasks.insert_one(task)
        task["_id"] = str(inserted.inserted_id)

        return jsonify({"message": "task added successfully", "task": task}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@user_bp.route('/Hello', methods=['GET'])
def print_hello():
    return "Hello World", 200
