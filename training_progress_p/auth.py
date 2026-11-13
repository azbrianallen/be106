# be106/training_progress/training_progress_p/auth.py

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from .extensions import db
from .models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

def _error_response(code: str, message: str, status_code: int):
    """Helper to enforce the standardized error envelope."""
    return jsonify({"code": code, "message": message}), status_code

@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user matching the agreed API contract."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error_response("bad_request", "Email is required.", 400)

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    # 1. Distinct required-field checks
    if not email:
        return _error_response("bad_request", "Email is required.", 400)

    if not password:
        return _error_response("bad_request", "Password is required.", 400)

    # 2. Length validation rules (400 bad_request)
    if len(email) > 105:
        return _error_response(
            "bad_request",
            "Email max length is 105 characters.",
            400,
        )

    if len(password) < 9:
        return _error_response(
            "bad_request",
            "Password must be at least 9 characters long.",
            400,
        )

    # 3. Duplicate email check (409 email_already_registered)
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return _error_response(
            "email_already_registered",
            "An account with this email already exists.",
            409,
        )

    # 4. Create and persist new user
    new_user = User(
        email=email,
        password_hash=generate_password_hash(password),
    )

    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error_response(
            "email_already_registered",
            "An account with this email already exists.",
            409,
        )

    # 5. Flat success payload (201 Created)
    return jsonify(
        {
            "id": new_user.id,
            "email": new_user.email,
            "created_at": new_user.created_at.isoformat(),
        }
    ), 201