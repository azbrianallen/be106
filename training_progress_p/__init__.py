# training_progress\training_progress\__init__.py

import click
from flask import Flask
from .config import config_by_name
from .extensions import db, migrate
from .auth import auth_bp
from .health import health_bp
from .routes import lessons_bp

def create_app(config_name="default"):
    """Application factory using dynamic configuration loading."""
    app = Flask(__name__)

    # Fallback safety in case an unmapped config name is passed
    if config_name not in config_by_name:
        config_name = "default"

    # Load configuration class matching config_name
    config_cls = config_by_name[config_name]
    app.config.from_object(config_cls)

    # Initialize extensions with app instance
    db.init_app(app)
    migrate.init_app(app, db)

    from . import models # noqa: F401

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(lessons_bp)
    app.register_blueprint(health_bp)

    @app.cli.command("show-config")
    def show_config():
        """Print non-secret runtime configuration values."""
        click.echo(f"DEBUG: {app.config.get('DEBUG')}")
        click.echo(f"TESTING: {app.config.get('TESTING')}")
        click.echo(f"DB_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

    return app
 