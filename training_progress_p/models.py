# be106/training_progress/training_progress_p/models.py

from datetime import datetime, timezone
from .extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(
        db.String(20),
        default="user",
        server_default="user",
        nullable=False,
    )
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    lesson_progresses = db.relationship(
        "LessonProgress",
        back_populates="user",
    )

class LessonProgress(db.Model):
    __tablename__ = "lesson_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    lesson_slug = db.Column(db.String(120), nullable=False)
    status = db.Column(
        db.String(20),
        default="not_started",
        server_default="not_started",
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "lesson_slug", name="uq_user_lesson_slug"),
    )

    user = db.relationship(
        "User",
        back_populates="lesson_progresses",
    ) 
