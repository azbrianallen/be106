# be106/training_progress/training_progress_p/routes.py

from datetime import datetime, timezone
from functools import wraps
import jwt
from flask import Blueprint, current_app, g, jsonify, request
from .extensions import db
from .models import LessonProgress, User

# Create the Blueprint object
lessons_bp = Blueprint("lessons", __name__, url_prefix="/lessons")

ALLOWED_STATUSES = {"not_started", "in_progress", "completed"}

def _error(code: str, message: str, status_code: int):
    """Return a standardized JSON error envelope."""
    return jsonify({"code": code, "message": message}), status_code

def _unauthorized(message: str):
    """Return a consistent 401 JSON error response."""
    return _error("unauthorized", message, 401)

def _forbidden(message: str):
    """Return a consistent 403 JSON error response."""
    return _error("forbidden", message, 403)

def _bad_request(message: str):
    """Return a consistent 400 JSON error response."""
    return _error("validation_error", message, 400)

def _not_found(message: str):
    """Return a consistent 404 JSON error response."""
    return _error("not_found", message, 404)

def _serialize_progress(progress: LessonProgress) -> dict:
    """Return a clean JSON-safe dictionary for a LessonProgress row."""
    return {
        "id": progress.id,
        "user_id": progress.user_id,
        "lesson_slug": progress.lesson_slug,
        "status": progress.status,
        "updated_at": progress.updated_at.isoformat(),
    }

DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 20
MAX_PER_PAGE = 50

def _parse_positive_int(raw_value: str | None, default: int, param_name: str):
    """Parse a query parameter into an integer >= 1, or return an error string."""
    if raw_value is None:
        return default, None

    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return None, f"'{param_name}' must be a valid integer."

    if value < 1:
        return None, f"'{param_name}' must be a positive integer (>= 1)."

    return value, None

def require_progress_owner_or_admin(view_fn):
    """Load LessonProgress by ID, enforce owner-or-admin access, and store on g.progress."""
    @wraps(view_fn)
    def wrapper(*args, **kwargs):
        # (1) Read lesson_progress_id from Flask's keyword view args
        lesson_progress_id = kwargs.get("lesson_progress_id")

        # (2) Load the record (404 if missing)
        progress = db.session.get(LessonProgress, lesson_progress_id)
        if progress is None:
            return _not_found("Lesson progress record not found.")

        # (3) Load current user to check admin privileges (missing user = non-admin)
        user = db.session.get(User, g.current_user_id)
        is_admin = bool(user and user.role == "admin")

        # (4) Enforce ownership or admin privilege (403 if neither)
        if progress.user_id != g.current_user_id and not is_admin:
            return _forbidden(
                "You do not have permission to access this lesson progress record."
            )

        # (5) Stash verified record on g and invoke the wrapped route
        g.progress = progress
        return view_fn(*args, **kwargs)

    return wrapper

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
    """Return a paginated list of LessonProgress records for the authenticated user."""
    page, page_err = _parse_positive_int(
        request.args.get("page"), DEFAULT_PAGE, "page"
    )
    if page_err:
        return _bad_request(page_err)

    per_page, per_page_err = _parse_positive_int(
        request.args.get("per_page"), DEFAULT_PER_PAGE, "per_page"
    )
    if per_page_err:
        return _bad_request(per_page_err)

    if per_page > MAX_PER_PAGE:
        return _bad_request(f"'per_page' cannot exceed {MAX_PER_PAGE}.")

    pagination = (
        LessonProgress.query
        .filter_by(user_id=g.current_user_id)
        .order_by(LessonProgress.id.asc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return jsonify(
        {
            "lessons": [_serialize_progress(record) for record in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
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

@lessons_bp.route("/<int:lesson_progress_id>", methods=["GET"])
@require_progress_owner_or_admin
def get_lesson_progress(lesson_progress_id: int):
    """Return a single LessonProgress record (already loaded & authorized on g.progress)."""
    return jsonify(_serialize_progress(g.progress)), 200

@lessons_bp.route("/<int:lesson_progress_id>", methods=["PATCH"])
@require_progress_owner_or_admin
def update_lesson_progress(lesson_progress_id: int):
    """Update the status of an authorized LessonProgress record."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _bad_request("Request body must be valid JSON.")

    disallowed_fields = set(data.keys()) - {"status"}
    if disallowed_fields:
        return _bad_request(
            f"Only 'status' can be updated. Disallowed field(s): {', '.join(sorted(disallowed_fields))}."
        )

    raw_status = data.get("status")
    if not isinstance(raw_status, str) or raw_status.strip() not in ALLOWED_STATUSES:
        return _bad_request(
            "status is required and must be one of: not_started, in_progress, completed."
        )

    g.progress.status = raw_status.strip()
    g.progress.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify(_serialize_progress(g.progress)), 200

@lessons_bp.route("/<int:lesson_progress_id>", methods=["DELETE"])
@require_progress_owner_or_admin
def delete_lesson_progress(lesson_progress_id: int):
    """Delete an authorized LessonProgress record."""
    db.session.delete(g.progress)
    db.session.commit()

    return jsonify({"deleted": True, "id": lesson_progress_id}), 200

