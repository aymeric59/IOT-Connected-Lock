#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

from flask import Flask, flash, render_template, request, g, session, redirect, url_for
import mysql.connector,requests, time, datetime, random, string
from passlib.hash import argon2
import requests
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

def generateToken () :
    token = False
    db = get_db()
    cur = db.cursor()
    while token == False :
        token = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(48)])
        cur.execute("SELECT id FROM user WHERE token = %(token)s", ({'token': token}))
        cur.fetchall()
        if cur.rowcount > 0 :
            token = False
    return token

@app.route('/')
def index () :
    if session.get('user'):
        user = session['user']
        return render_template('home.html.j2', user = user)
    else :
        flash('Vous devez vous connecter pour accéder à cette url')
        return redirect(url_for('login'))

@app.route('/login/', methods = ['GET', 'POST'])
def login ():
    if session.get('user'):
        user = session['user']
        return redirect(url_for('index'))

    username = str(request.form.get('username'))
    password = str(request.form.get('password'))

    db = get_db()
    cur = db.cursor()
    # [0] id, [1] username, [2] password, [3] token, [4] is_admin
    cur.execute('SELECT * FROM user WHERE username = %(username)s', {'username' : username})
    users = cur.fetchall()

    valid_user = False
    for user in users :
        if argon2.verify(password, user[2]) :
            valid_user = user
    if valid_user :
        session['user'] = valid_user
        return redirect(url_for('index'))
    if request.method == 'POST':
        flash("Mauvais identifiants")
    return render_template('login.html.j2')

@app.route('/logout/')
def logout () :
    session.clear()
    return redirect(url_for('login'))

@app.route('/open/')
def open () :
    if not session.get('user') or not session.get('user')[2] :
        flash('Vous n\'avez pas les droits pour accéder à cette page')
        return redirect(url_for('login'))

    userID = session.get('user')[0]
    token = session.get('user')[3]

    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT uid FROM badge WHERE owner_id = %(id)s', {'id' : userID})
    uid = cur.fetchone()

    if uid is None :
        flash('Accès refusé, vous n\'avez pas de badge.')
        status = int(0)
        badge_uid = 0
    else :
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect('172.20.10.14', username='pi', password='raspberry')
        client.exec_command('python3.5 /home/pi/openFromSite.py')
        client.close()
        flash('Serrure ouverte')
        status = int(1)
        badge_uid = uid[0]

    requests.get('http://api.serrure.loc:7000/send_log/'+str(badge_uid)+'/'+str(status), auth=(userID, token))
    return redirect(url_for('index'))

@app.route('/logs/', methods = ['GET', 'POST'])
def logs () :
    if not session.get('user') or not session.get('user')[2] :
        flash('Vous n\'avez pas les droits pour accéder à cette page')
        return redirect(url_for('login'))

    user = session.get('user')[0]
    token = session.get('user')[3]

    entries = requests.get('http://api.serrure.loc:7000/get_logs/', auth=(user, token)).json()

    return render_template('logs.html.j2', entries = entries, user = session['user'])

@app.route('/admin/')
def admin () :
    if not session.get('user') or not session.get('user')[4] :
        flash('Vous n\'avez pas les droits pour accéder à cette page')
        return redirect(url_for('login'))
    db = get_db()
    cur = db.cursor()
    cur.execute("(SELECT u.id, u.username AS name, u.is_admin AS admin, b.id, b.uid FROM user u RIGHT OUTER JOIN badge b ON u.id = b.owner_id) UNION (SELECT u.id, u.username AS name, u.is_admin AS admin, b.id, b.uid FROM user u LEFT OUTER JOIN badge b ON u.id = b.owner_id) ORDER BY admin DESC, name")
    users = cur.fetchall()
    return render_template('admin.html.j2',  user = session['user'], users = users)

@app.route('/admin/users/add/', methods = ['GET', 'POST'])
def add_user () :
    if not session.get('user') or not session.get('user')[4] :
        flash('Vous n\'avez pas les droits pour accéder à cette page')
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    username = request.form.get('username')
    password = request.form.get('password')
    badges = request.form.get('badges')
    isAdmin = 1 if request.form.get('isAdmin') else 0
    token = generateToken()

    if username is not None and password is not None :
        sql = "INSERT INTO user(id, username, password, token, is_admin) VALUES(DEFAULT, %(username)s, %(password)s, %(token)s, %(isAdmin)s)"
        cur.execute(sql, ({'username': username, 'password': argon2.hash(password), 'token': token, 'isAdmin': isAdmin}))
        db.commit()
        if badges is not None :
            cur.execute("UPDATE badge SET owner_id = %(owner_id)s WHERE id = %(id)s", ({'owner_id': cur.lastrowid, 'id': badges}))
            db.commit()
        flash("L'utilisateur " + username + " a bien été ajouté")
        return redirect(url_for('admin'))
    # [0] id, [1] uid, [2] owner_id
    cur.execute("SELECT * FROM badge WHERE owner_id IS NULL")
    badges = cur.fetchall()

    return render_template('user_add.html.j2', user = session['user'], badges = badges)

@app.route('/admin/users/edit/<int:id>', methods = ['GET', 'POST'])
def edit_user (id) :
    if not session.get('user') or not session.get('user')[4] :
        flash('Vous n\'avez pas les droits pour accéder à cette page')
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    username = request.form.get('username')
    isAdmin = 1 if request.form.get('isAdmin') else 0
    badge = request.form.get('badges')

    #[0] id, [1] uid, [2] owner_id
    cur.execute("SELECT * FROM badge WHERE owner_id = %(id)s", ({'id': id}))
    userBadge = cur.fetchone()

    if username is None :
        # [0] id, [1] username, [2] password, [3] token, [4] is_admin
        cur.execute("SELECT * FROM user WHERE id = %(id)s", ({'id': id}))
        userInfo = cur.fetchone()
        if cur.rowcount <= 0 :
            flash("Cet utilisateur ne semble pas exister")
            return redirect(url_for('admin'))
        if request.method == 'POST':
            flash("Veuillez remplir tous les champs")
        # [0] id, [1] uid, [2] owner_id
        cur.execute("SELECT * FROM badge WHERE owner_id IS NULL")
        badges = cur.fetchall()

        return render_template('user_edit.html.j2', user = session['user'], userInfo = userInfo, badges = badges, userBadge = userBadge)
    else :
        sql = "UPDATE user SET username = %(username)s, is_admin = %(isAdmin)s WHERE id = %(id)s"
        params = ({'id': id, 'username': username, 'isAdmin': isAdmin})
        cur.execute(sql, params)
        db.commit()
        if badge is not None :
            cur.execute("UPDATE badge SET owner_id = %(owner_id)s WHERE id = %(id)s", ({'owner_id': id, 'id': badge}))
            db.commit()
            if userBadge is not None :
                cur.execute("UPDATE badge SET owner_id = NULL WHERE id = %(id)s", ({'id': userBadge[0]}))
                db.commit()
        flash("L'utilisateur " + username + " a bien été modifié")
        return redirect(url_for('admin'))

@app.route('/admin/users/delete/<int:id>')
def delete_user (id) :
    if not session.get('user') or not session.get('user')[4] :
        flash('Vous n\'avez pas les droits pour accéder à cette page')
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM user WHERE id = %(id)s", ({'id': id}))
    db.commit()

    if cur.rowcount > 0 :
        flash("L'utilisateur ayant l'id " + str(id) + " a bien été supprimé")
    else :
        flash("L'utilisateur ayant l'id " + str(id) + " n'a pas pu être supprimé car ne semble pas exister")
    return redirect(url_for('admin'))

@app.route('/admin/badge/add/', methods = ['GET', 'POST'])
def add_badge () :
    if not session.get('user') or not session.get('user')[4] :
        flash('Vous n\'avez pas les droits pour accéder à cette page')
        return redirect(url_for('login'))

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('172.20.10.14', username='pi', password='raspberry')
    client.exec_command('python3.5 /home/pi/add.py')
    client.close()
    flash('Poser votre badge durant quelques secondes sur le lecteur, et rafraichissez la page, vous devriez voir apparaître votre nouveau badge')

    return redirect(url_for('admin'))

@app.route('/admin/badge/delete/<int:id>')
def delete_badge (id) :
    if not session.get('user') or not session.get('user')[4] :
        flash('Vous n\'avez pas les droits pour accéder à cette page')
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM badge WHERE id = %(id)s", ({'id': id}))
    db.commit()

    if cur.rowcount > 0 :
        flash("Le badge ayant l'id " + str(id) + " a bien été supprimé")
    else :
        flash("Le badge ayant l'id " + str(id) + " n'a pas pu être supprimé car ne semble pas exister")
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
