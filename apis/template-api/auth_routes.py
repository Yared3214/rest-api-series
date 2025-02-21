from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from .. import mongo

auth = Blueprint("auth", name)

@auth.route("/signup", methods=["POST"])
def signup():
    data = request.json
    if not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email and password required"}), 400

    existing_user = mongo.db.users.find_one({"email": data["email"]})
    if existing_user:
        return jsonify({"message": "User already exists"}), 409

    hashed_pw = generate_password_hash(data["password"])
    mongo.db.users.insert_one({"email": data["email"], "password": hashed_pw})
    
    return jsonify({"message": "User registered successfully"}), 201

@auth.route("/login", methods=["POST"])
def login():
    data = request.json
    user = mongo.db.users.find_one({"email": data["email"]})
    
    if not user or not check_password_hash(user["password"], data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user["_id"]))
    return jsonify({"token": token}), 200