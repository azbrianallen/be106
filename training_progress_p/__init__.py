# training_progress\training_progress\__init__.py

import os 
from flask import Flask
from training_progress_p.config import config_by_name
from training_progress_p.extensions import db, migrate
from training_progress_p.health import health_bp

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

    # Register blueprints
    from training_progress_p.routes import lessons_bp

    app.register_blueprint(lessons_bp)
    app.register_blueprint(health_bp)

    return app
 