from flask import Flask, render_template, g, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)

DBFILE = 'jar.db'

def check_ip():
    db = sqlite3.connect(DBFILE)

    user_ip = request.remote_addr
    cur = db.execute('SELECT count(*) FROM voters WHERE ip_address=?', (user_ip,)) # Check if user's ip is in database
    user_check = cur.fetchone()[0] # State of query

    db.close()

    return user_check
    
@app.route('/')
def index():
    return(render_template('index.html'))

@app.route('/jar')
def jar():
    return(render_template('jar.html', has_visited=check_ip())) # Check if user has visited before, if so send that to template

@app.route('/vote')
def vote():
    return(render_template('vote.html'))

@app.route('/confirm')
def confirm():
    return(render_template('confirm.html'))