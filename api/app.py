#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

from flask import Flask, flash, render_template, request, g, session, redirect, url_for, jsonify
import mysql.connector,requests, time, datetime
from passlib.hash import argon2
import json
import paramiko

app = Flask(__name__)

app.config.from_object('secret_config')

def connect_db () :
    g.mysql_connection = mysql.connector.connect(
        host = app.config['DATABASE_HOST'],
        user = app.config['DATABASE_USER'],
        password = app.config['DATABASE_PASSWORD'],
        database = app.config['DATABASE_NAME']
    )
    return g.mysql_connection

def get_db () :
    if not hasattr(g, 'db') :
        g.db = connect_db()
    return g.db

def check_token (id, token) :
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT token FROM user WHERE id=%(id)s', {'id' : id})
    entries = cur.fetchone()

    if entries[0] == token:
        return True
    return False

def isRaspberry (token) :
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT token FROM user WHERE username=%(name)s', {'name': 'pi'})
    entries = cur.fetchone()
    if entries[0] == token:
        return True
    return False

def badgeExist (uid) :
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT uid FROM badge WHERE uid = %(uid)s', {'uid': uid})
    uids = cur.fetchall()

    if cur.rowcount > 0 :
        return True
    return False

@app.route('/open/<int:uid>',  methods = ['GET', 'POST'])
def open (uid) :
    try :
        token = request.authorization.password
        userID = request.authorization.username

        Autorised = check_token(userID, token)

    except :
        Autorised = False


    if not Autorised :
        return jsonify({"success" : "Forbidden"})

    if badgeExist(uid) :

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect('172.20.10.14', username='pi', password='raspberry')
        client.exec_command('python3.5 /home/pi/openFromSite.py')
        client.close()

        return jsonify({"success" : True})

    return jsonify({"success" : False})

@app.route('/add_uid/<int:uid>',  methods = ['GET', 'POST'])
def add_uid (uid) :
    try :
        token = request.authorization.password
        isRasp = isRaspberry(token)
    except :
        isRasp = False
    
    if not isRasp :
        return jsonify({"success" : "not rasp"})

    if not badgeExist(uid) :

        db = get_db()
        cur = db.cursor()
        cur.execute('INSERT INTO badge(uid) VALUES (%(uid)s)', {'uid' : uid})
        db.commit()
        return jsonify({"success" : True})
    return jsonify({"success" : "badge existant"})

@app.route('/send_log/<int:uid>/<int:status>',  methods = ['GET', 'POST'])
def send_log (uid, status) :
    try :
        token = request.authorization.password
        userID = request.authorization.username

        Autorised = check_token(userID, token)
    except :
        Autorised = False

    if not Autorised :
        return jsonify({"success" : "Forbidden"})

    db = get_db()
    cur = db.cursor()
    cur.execute('INSERT INTO log (id, date, badge_uid, status) VALUES (DEFAULT, %s, %s, %s)', (datetime.datetime.now(), uid, status))
    db.commit()

    return jsonify({"success" : True})


@app.route('/get_logs/', methods = ['GET', 'POST'])
def get_logs () :
    try :
        token = request.authorization.password
        userID = request.authorization.username

        Autorised = check_token(userID, token)
    except :
        Autorised = False

    if not Autorised :
        return jsonify({"success" : "Forbidden"})
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT l.id, l.date, l.badge_uid, l.status, u.username FROM log l LEFT JOIN badge b ON b.uid = l.badge_uid LEFT JOIN user u ON u.id = b.owner_id ORDER BY l.date DESC')
    entries = cur.fetchall()

    for i in range(0, len(entries)) :
        entries[i] = list(entries[i])
        entries[i][1] = entries[i][1].strftime('%d %B %Y - %H:%M')
        entries[i] = tuple(entries[i])

    return jsonify(entries)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7000)
