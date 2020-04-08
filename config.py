import os
from os import environ
from dotenv import load_dotenv

# Load env variables
load_dotenv()

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

SQL_USER = environ.get('SQL_USER')
SQL_PASSWORD = environ.get('SQL_PASSWORD')
SQL_DATABASE = environ.get('SQL_DATABASE')

# COMPLETED IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://' \
                          '{user}:{password}@' \
                          'localhost:5432/' \
                          '{database}'.format(user=SQL_USER, password=SQL_PASSWORD, database=SQL_DATABASE)
