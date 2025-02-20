import os
import numpy as np
import cv2
import tensorflow as tf
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import mongo

classify = Blueprint("classify", name)

MODEL_PATH = "model/skin_disease_model.h5"
model = tf.keras.models.load_model(MODEL_PATH)

CLASSES = ["Melanoma", "Nevus", "Basal Cell Carcinoma"]
UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@classify.route("/", methods=["POST"])
@jwt_required()
def predict():
    if "file" not in request.files:
        return jsonify({"message": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Process image
    img = cv2.imread(filepath)
    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    predictions = model.predict(img)
    predicted_class = CLASSES[np.argmax(predictions)]
    confidence = float(np.max(predictions))

    result_data = {
        "user_id": get_jwt_identity(),
        "filename": filename,
        "prediction": predicted_class,
        "confidence": confidence,
        "date": datetime.utcnow()
    }
    mongo.db.results.insert_one(result_data)

    return jsonify(result_data), 200