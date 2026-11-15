# training_progress\README.md

===================================================== 
1. Project Description 
===================================================== 

This repository contains the backend RESTful API for tracking student lesson progress, built using Python, Flask, Flask-SQLAlchemy, and Flask-Migrate.

===================================================== 
2. Set Up the Virtual Environment
===================================================== 

Follow these steps to clone and set up the local development environment on a Windows machine (using PowerShell or Command Prompt).

- Clone the Repository

```cmd
git clone https://github.com/azbrianallen/be106.git 
cd be106/training_progress 

Create a local Python virtual environment inside the project directory:

DOS
python -m venv venv
Activate the virtual environment:

Command Prompt: venv\Scripts\activate.bat

PowerShell: .\venv\Scripts\Activate.ps1

- Install Dependencies

Install all required packages (These will be added to requirements.txt in a future update.)
pip install flask flask-sqlalchemy flask-migrate 

4. Configure Environment Variables
Copy the .env.example file to create your local .env configuration file:

DOS
copy .env.example .env

5. Run the Application
Ensure your virtual environment is active, then launch the Flask development server from the project root directory:

DOS
set FLASK_APP=training_progress_p
flask run
The API will start locally at http://127.0.0.1:5000/ 

=================================================== 
3. Environmental Variables 
=================================================== 

The application reads configuration from environment variables defined in .env. Below is a breakdown of available keys (refer to .env.example for defaults):

Variable: FLASK_APP
Description: Specifies the application package entry point for the Flask CLI.
Example / Recommended Value: training_progress_p

Variable: FLASK_ENV
Description: Sets the application configuration mode (development, testing, or production).
Example / Recommended Value: development

Variable: SECRET_KEY
Description: Secret key used for signing session cookies and securing sensitive operations.
Example / Recommended Value: Random string (e.g., change-me-in-real-env)

Variable: DATABASE_URL
Description: SQLAlchemy connection string pointing to the target database.
Example / Recommended Value: sqlite:///training_progress_dev.db

=================================================== 
4. Migrations
=================================================== 

Database schema updates are managed using Flask-Migrate (powered by Alembic).

Note: Initial migrations will be generated once models are defined in models.py.

General Migration Commands

1. Initialize Migration Tracking (One-Time Setup):
Generates the migrations/ directory structure for the repository.

DOS
flask db init

2. Generate a Migration Script:
Detects changes between SQLAlchemy models and the current database schema, drafting a new version script.

DOS
flask db migrate -m "Describe schema changes here"

3. Apply Migrations:
Executes pending migration scripts to update the database schema.

DOS
flask db upgrade

4. Roll Back Migrations (If Needed):
Reverts the database schema to the previous migration state.

DOS
flask db downgrade
=================================================== 
5. auth_evidence 
=================================================== 

HASH AUDIT IN FLASK SHELL:

## Hash audit in Flask shell

Command (run inside `python -m flask shell`):

```python
from training_progress_p.models import User
for u in User.query.limit(3).all():
    print(u.id, u.email, u.password_hash)

1 redacted-email-1 scrypt:32768:8:1$H224LnemASioWyle$de170257a2ca1ea6006a9182a48312f33cead9bd4cd8aed85d2262e90dda643955ab168774fa70ab6945d4b39ee2abab20ef63389ba6b99bdc8012d56918cc4d
2 redacted-email-2 scrypt:32768:8:1$4gRiO1EumAAjY4Yh$225e4e401d5faccb29ada36b409dcddc1612893dc04c63aaea396bdbe88362ceeb76b5349cde6d670dc97724b091be16b496efb414eda4ed8e8d12b0a92926b5
3 redacted-email-3 scrypt:32768:8:1$btR3I8Bhs7UFRMy5$1813e9a39c2924a2e5baae98117f465f477397d9850eb1888f8bc7861a6ee79fa7e88ee27b2f59edd5d5abebdd53e6ef4a9bd0b45074e4dabf53587da8df1644

GOOD EMAIL / BAD PASSWORD:

Request (from CMD, against running dev server):

```bash

be106\training_progress>curl -i -X POST http://localhost:5000/auth/login   -H "Content-Type: application/json"   -d "{\"email\": \"REDACTED EMAIL\", \"password\": \"definitely-wrong-password\"}"
HTTP/1.1 401 UNAUTHORIZED
Server: Werkzeug/3.1.9 Python/3.14.5
Date: Sun, 15 Nov 2026 22:50:03 GMT
Content-Type: application/json
Content-Length: 70
Connection: close

{"code":"invalid_credentials","message":"Invalid email or password."} 

