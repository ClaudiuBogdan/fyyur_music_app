# Udacity Fyyur project submission:
## Setup
1. Copy .env.example to .env file and add database connection parmas
2. Run `flask db upgrade`
3. Run `python manage.py seed` to seed the database
4. Run `python3 app.py` to start the application

## Considerations
* Unit testing is implemented for database queries. 
Tests location: `tests/query_tests.py`
* The project is available on github: https://github.com/ClaudiuBogdan/fyyur_music_app