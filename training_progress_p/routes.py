from flask import Blueprint, jsonify

# Create the Blueprint object
lessons_bp = Blueprint("lessons", __name__, url_prefix="/lessons")

@lessons_bp.route("/")
def get_lessons():
    return jsonify({"lessons": []})

