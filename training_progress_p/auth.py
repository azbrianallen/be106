# be106/training_progress/training_progress_p/auth.py

from datetime import datetime, timedelta, timezone
import jwt  
from flask import Blueprint, current_app, g, jsonify, request
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from .extensions import db
from .models import User
from functools import wraps

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

def token_required(f):
    """Verify the Bearer JWT and populate g.current_user_id."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split()

        if len(parts) != 2 or parts[0] != "Bearer":
            return _error_response(
                "unauthorized",
                "Missing or invalid Authorization header.",
                401,
            )

        token = parts[1]

        try:
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET"],
                algorithms=["HS256"],
            )
            g.current_user_id = int(payload["sub"])
        except jwt.ExpiredSignatureError:
            return _error_response("unauthorized", "Token has expired.", 401)
        except (jwt.InvalidTokenError, KeyError, ValueError, TypeError):
            return _error_response("unauthorized", "Invalid or malformed token.", 401)

        return f(*args, **kwargs)

    return decorated

def _error_response(code: str, message: str, status_code: int):
    """Helper to enforce the standardized error envelope."""
    return jsonify({"code": code, "message": message}), status_code

# Register Route 

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

# Login Route 

@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate a user and issue a signed HS256 JWT access token."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error_response("bad_request", "Email is required.", 400)

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

# 1. Distinct required-field checks (400 bad_request)

    if not email:
        return _error_response("bad_request", "Email is required.", 400)

    if not password:
        return _error_response("bad_request", "Password is required.", 400)

# 2. Look up user and verify password with identical generic 401 on failure

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return _error_response(
            "invalid_credentials",
            "Invalid email or password.",
            401,
        )

# 3. Build JWT payload using timezone-aware UTC timestamps

    now_utc = datetime.now(timezone.utc)
    lifetime_minutes = current_app.config["JWT_LIFETIME_MINUTES"]
    payload = {
        "sub": str(user.id),
        "role": "user",
        "iat": now_utc,
        "exp": now_utc + timedelta(minutes=lifetime_minutes),
    }

# 4. Sign with HS256 using JWT_SECRET from config

    token = jwt.encode(
        payload,
        current_app.config["JWT_SECRET"],
        algorithm="HS256",
    )

    return jsonify({"access_token": token}), 200
