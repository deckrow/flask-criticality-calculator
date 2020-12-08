import functools
import sys
import os
import io

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5

from calc_CIF.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/sign_in', methods=('GET', 'POST'))
def sign_in():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif user['password'] != password:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('calc.choice'))

        flash(error)

    return render_template('auth/sign_in.html')


@bp.route('/login/<id>', methods=('GET', 'POST'))
def login(id):
    if request.method == 'POST':
        username = request.form['username']
        sig_file = request.files['file'].read()

        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif sig_file is None:
            error = 'Incorrect file.'

        root = os.path.realpath(os.path.dirname(__file__))
        pub_key = os.path.join(root, 'static/keys/{}/Pubkey.out'.format(username))
        with open(pub_key, 'rb') as f: key = f.read()

        answer = verifying_signature(key, username, sig_file)

        if error is None and answer:
            return redirect(url_for('calc.questions', id=id))

        flash(error)

    return render_template('auth/login.html')


def verifying_signature(key, data, sig):
    h = SHA256.new(str.encode(data))
    rsa = RSA.importKey(key)
    signer = PKCS1_v1_5.new(rsa)

    if signer.verify(h, sig):
        return True
    else:
        return False

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('calc.choice'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view