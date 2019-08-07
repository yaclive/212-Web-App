from flask import Flask, render_template, g, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)

MENUDB = 'jar.db'

@app.route('/')
def index():
    return(render_template('index.html'))