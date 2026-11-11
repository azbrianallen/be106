# training_progress_p/health.py

from flask import Blueprint, jsonify

# Create the health blueprint instance
health_bp = Blueprint("health", __name__, url_prefix="/health")


@health_bp.route("", methods=["GET"])
def check_health():
    """Health check endpoint to verify API and blueprint availability."""
    return jsonify({"status": "healthy", "service": "training_progress"}), 200


