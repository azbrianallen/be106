from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Instantiate extensions without binding them to a specific app instance yet
db = SQLAlchemy()
migrate = Migrate()
