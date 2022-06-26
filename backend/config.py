import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True
# configure track modifications when we run app to false
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Connect to the database
# SECret_KEY = 
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:YasTesh2123@localhost:5432/trivia'