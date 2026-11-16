# be106/training_progress/training_progress_p/routes.py

import jwt
from flask import Blueprint, current_app, g, jsonify, request
from .extensions import db
from .models import User

# Create the Blueprint object
lessons_bp = Blueprint("lessons", __name__, url_prefix="/lessons")

def _unauthorized(message: str):
    """Return a consistent 401 JSON error response."""
    return jsonify({"code": "unauthorized", "message": message}), 401

def _forbidden(message: str):
    """Return a consistent 403 JSON error response."""
    return jsonify({"code": "forbidden", "message": message}), 403

@lessons_bp.before_request
def require_auth():
    """Verify the Bearer JWT before every /lessons request and set g.current_user_id."""
    auth_header = request.headers.get("Authorization", "")
    parts = auth_header.split()

    # Must match exact "Bearer <token>" structure
    if len(parts) != 2 or parts[0] != "Bearer":
        return _unauthorized("Missing or invalid Authorization header.")

    token = parts[1]

    try:
        # PyJWT verifies signature and enforces 'exp' expiration by default
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET"],
            algorithms=["HS256"],
        )
        g.current_user_id = int(payload["sub"])
    except jwt.ExpiredSignatureError:
        return _unauthorized("Token has expired.")
    except (jwt.InvalidTokenError, KeyError, ValueError, TypeError):
        return _unauthorized("Invalid or malformed token.")

@lessons_bp.route("/")
def get_lessons():
    return jsonify({"lessons": [], "user_id": g.current_user_id})

@lessons_bp.route("/admin-ping", methods=["GET"])
def admin_ping():
    """Verify the authenticated user has the 'admin' role in the database."""
    user = db.session.get(User, g.current_user_id)
    if not user or user.role != "admin":
        return _forbidden("Admin privileges are required.")

    return jsonify(
        {
            "status": "ok",
            "message": "Admin access confirmed.",
            "user_id": user.id,
        }
    ), 200
