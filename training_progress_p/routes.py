# be106/training_progress/training_progress_p/routes.py

import jwt
from flask import Blueprint, current_app, g, jsonify, request
from .extensions import db
from .models import LessonProgress, User

# Create the Blueprint object
lessons_bp = Blueprint("lessons", __name__, url_prefix="/lessons")

ALLOWED_STATUSES = {"not_started", "in_progress", "completed"}

def _unauthorized(message: str):
    """Return a consistent 401 JSON error response."""
    return jsonify({"code": "unauthorized", "message": message}), 401

def _forbidden(message: str):
    """Return a consistent 403 JSON error response."""
    return jsonify({"code": "forbidden", "message": message}), 403

def _bad_request(message: str):
    """Return a consistent 400 JSON error response."""
    return jsonify({"code": "bad_request", "message": message}), 400

def _serialize_progress(progress: LessonProgress) -> dict:
    """Return a clean JSON-safe dictionary for a LessonProgress row."""
    return {
        "id": progress.id,
        "user_id": progress.user_id,
        "lesson_slug": progress.lesson_slug,
        "status": progress.status,
        "updated_at": progress.updated_at.isoformat(),
    }

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

@lessons_bp.route("/", methods=["GET"])
def get_lessons():
    """Return all LessonProgress records belonging to the authenticated user."""
    records = (
        LessonProgress.query
        .filter_by(user_id=g.current_user_id)
        .order_by(LessonProgress.id.asc())
        .all()
    )
    return jsonify(
        {
            "lessons": [_serialize_progress(record) for record in records],
        }
    ), 200

@lessons_bp.route("/", methods=["POST"])
def create_lesson_progress():
    """Create a new LessonProgress record for the authenticated user."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _bad_request("Request body must be valid JSON.")

    raw_slug = data.get("lesson_slug")
    if not isinstance(raw_slug, str) or not raw_slug.strip():
        return _bad_request("lesson_slug is required and must be a non-empty string.")

    lesson_slug = raw_slug.strip()
    if len(lesson_slug) > 120:
        return _bad_request("lesson_slug max length is 120 characters.")

    progress_kwargs = {
        "user_id": g.current_user_id,
        "lesson_slug": lesson_slug,
    }

    if "status" in data and data["status"] is not None:
        raw_status = data["status"]
        if not isinstance(raw_status, str) or raw_status.strip() not in ALLOWED_STATUSES:
            return _bad_request(
                "status must be one of: not_started, in_progress, completed."
            )
        progress_kwargs["status"] = raw_status.strip()

    progress = LessonProgress(**progress_kwargs)
    db.session.add(progress)
    db.session.commit()

    return jsonify(_serialize_progress(progress)), 201

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
