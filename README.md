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
