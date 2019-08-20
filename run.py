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

def check_frozen():
    db = sqlite3.connect(DBFILE)

    cur = db.execute('SELECT is_frozen FROM jars WHERE id=1') # Check if jar is frozen
    frozen_check = cur.fetchone()[0] # State of query

    db.close()

    return frozen_check

def check_full():
    db = sqlite3.connect(DBFILE)

    cur = db.execute('SELECT coins FROM jars WHERE id=1') # Get jar balance
    coins = cur.fetchone()[0] # State of query

    cur = db.execute('SELECT capacity FROM jars WHERE id=1') # Get jar balance
    capacity = cur.fetchone()[0] # State of query

    db.close()

    return (coins >= capacity)

def check_status():
    if (check_ip()): return "voted"
    if (check_frozen()): return "frozen"
    if (check_full()): return "full"

    return ""

@app.route('/')
def index():
    return(render_template('index.html'))

@app.route('/jar')
def jar():
    db = sqlite3.connect(DBFILE)

    cur = db.execute('SELECT * FROM jars WHERE id=1')
    stats = cur.fetchone()

    cur = db.execute('SELECT * FROM modifiers WHERE id=1')
    votes = cur.fetchone()

    return(render_template(
        'jar.html',
        coins=stats[1],
        capacity=stats[2],
        percent=round((stats[1]/stats[2]) * 100, 2),
        votes=votes,
        error=check_status() # Check if user has visited before, if so send that to template
    ))

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if (check_status()): return redirect(url_for('jar')) # Deny dodgy submission
    if 'action' not in request.form: return redirect(url_for('jar')) # Deny request without form data

    action = request.form['action']

    # Make change to jar
    db = sqlite3.connect(DBFILE)

    # First and foremost, log users ip address to mitigate attacks
    # COMMENT OUT THE FOLLOWING TO DISABLE IP TRACKING
    # to vote again, DELETE FROM voters WHERE ip_address=127.0.0.1
    user_ip = request.remote_addr
    cur = db.execute('INSERT INTO voters(ip_address, vote) VALUES(?, ?)', (user_ip, request.form['action']))
    db.commit()

    if (action == 'add coin' or action == 'take coin'):
        # Get jar balance
        cur = db.execute('SELECT coins FROM jars WHERE id=1')
        coins = cur.fetchone()[0] # Amount of coins currently in the jar

        if (action == 'add coin'):
            coins += 1
        elif (action == 'take coin'):
            coins -= 1

        coins = max(coins, 0) # Ensure jar cant have negative coins

        cur = db.execute('UPDATE jars SET coins=? WHERE id=1', (coins,)) # Set new jar balance
        db.commit()
    elif (action == 'add vote double' or action == 'add vote freeze' or action == 'add vote tip'):
        cur = db.execute('SELECT * FROM modifiers WHERE id=1')
        votes = cur.fetchone()

        if (action == 'add vote double'):
            vote = votes[1]
            if ((vote + 1) < 500):
                vote += 1
            else:
                vote = 0

                # Max votes reached, update jar
                cur = db.execute('UPDATE jars SET capacity = capacity * 2 WHERE id=1') # Double jar capacity
                db.commit()

            cur = db.execute('UPDATE modifiers SET double_capacity=? WHERE id=1', (vote,)) # Set new vote amount
            db.commit()
        elif (action == 'add vote freeze'):
            vote = votes[2]
            if ((vote + 1) < 500):
                vote += 1
            else:
                vote = 0
                
                # Max votes reached, update jar
                cur = db.execute('UPDATE jars SET is_frozen = true WHERE id=1') # Freeze jar
                db.commit()

            cur = db.execute('UPDATE modifiers SET freeze=? WHERE id=1', (vote,)) # Set new vote amount
            db.commit()
        elif (action == 'add vote tip'):
            vote = votes[3]
            if ((vote + 1) < 500):
                vote += 1
            else:
                vote = 0
                
                # Max votes reached, update jar
                cur = db.execute('UPDATE jars SET coins = coins / 2 WHERE id=1') # Double jar capacity
                db.commit()

            cur = db.execute('UPDATE modifiers SET tip_out=? WHERE id=1', (vote,)) # Set new vote amount
            db.commit()

    db.close()

    return(render_template('confirm.html', action=action))
