# Steps to run after clone
- python -m venv env
- env\Scripts\activate
- pip install flask

- set FLASK_APP=run.py
- set FLASK_DEBUG=1

- python -m flask run

# Steps to run there after
- env\Scripts\activate

- set FLASK_APP=run.py
- set FLASK_DEBUG=1

- python -m flask run

# Disable ip logging
- find the comment in 'run.py' that says, 'COMMENT OUT THE FOLLOWING TO DISABLE IP TRACKING' to disable database logging
- to remove your ip from the database run the following, DELETE FROM voters WHERE ip_address=127.0.0.1