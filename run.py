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
    db = sqlite3.connect(DBFILE)

    cur = db.execute('SELECT * FROM jars WHERE id=1')
    stats = cur.fetchone()

    return(render_template(
        'jar.html',
        coins=stats[1],
        capacity=stats[2],
        has_visited=check_ip() # Check if user has visited before, if so send that to template
    ))

@app.route('/vote')
def vote():
    return(render_template('vote.html'))

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if (check_ip()): return redirect(url_for('jar')) # Deny double submission

    if (request.form['action'] == 'add coin' or request.form['action'] == 'take coin'):
        # Make change to jar
        db = sqlite3.connect(DBFILE)

        # First and foremost, log users ip address to mitigate attacks
        #user_ip = request.remote_addr
        #cur = db.execute('INSERT INTO voters(ip_address, vote) VALUES(?, ?)', (user_ip, request.form['action']))
        #db.commit()

        # Get jar balance
        cur = db.execute('SELECT coins FROM jars WHERE id=1')
        coins = cur.fetchone()[0] # Amount of coins currently in the jar

        if (request.form['action'] == 'add coin'):
            coins += 1
        elif (request.form['action'] == 'take coin'):
            coins -= 1

        coins = max(coins, 0) # Ensure jar cant have negative coins

        cur = db.execute('UPDATE jars SET coins=? WHERE id=1', (coins,)) # Set new jar balance

        # Detect if the jar is full
        # Close project

        db.commit()
        db.close()

        return(render_template('confirm.html', action=request.form['action']))
    else:
        return redirect(url_for('jar')) # Send them back