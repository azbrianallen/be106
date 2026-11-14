# be106/training_progress/training_progress_p/user_bp.py

from flask import Blueprint, g, jsonify, request
from sqlalchemy.exc import IntegrityError
from .auth import _error_response, token_required
from .extensions import db
from .models import User

# Note: If you want the URL to be /user/profile, set url_prefix="/user" here
# (or pass url_prefix="/user" when calling app.register_blueprint in __init__.py).
user_bp = Blueprint("user", __name__, url_prefix="/user")

def _serialize_profile(user: User) -> dict:
    """Return only safe public fields for a User."""
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
    }

@user_bp.route("/profile", methods=["GET"])
@token_required
def get_profile():
    """Return safe public profile fields for the authenticated user."""
    user = db.session.get(User, g.current_user_id)
    if not user:
        return _error_response("unauthorized", "User not found.", 401)

    return jsonify(_serialize_profile(user)), 200


@user_bp.route("/profile", methods=["PATCH"])
@token_required
def update_profile():
    """Update the authenticated user's email and return the updated safe profile."""
    user = db.session.get(User, g.current_user_id)
    if not user:
        return _error_response("unauthorized", "Invalid credentials.", 401)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error_response("bad_request", "Request body must be valid JSON.", 400)

    # Allowlist approach: inspect only 'email' and ignore any other fields
    if "email" in data:
        email = (data.get("email") or "").strip().lower()

        if not email:
            return _error_response("bad_request", "Email is required.", 400)

        if len(email) > 105:
            return _error_response(
                "bad_request",
                "Email max length is 105 characters.",
                400,
            )

        # Check uniqueness if the email is actually changing
        if email != user.email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return _error_response(
                    "email_already_registered",
                    "An account with this email already exists.",
                    409,
                )

            user.email = email
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return _error_response(
                    "email_already_registered",
                    "An account with this email already exists.",
                    409,
                )

    return jsonify(_serialize_profile(user)), 200 
