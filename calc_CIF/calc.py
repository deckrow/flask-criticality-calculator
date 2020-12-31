from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, json, jsonify, session
)

from datetime import datetime

from calc_CIF.db import get_db

import os

bp = Blueprint('calc', __name__)


@bp.route('/')
def index():
    data = get_json("detail_info.json")

    db = get_db()
    facilities = db.execute(
        'SELECT id, name, check_date, criticality_category FROM facilities'
    ).fetchall()

    return render_template('calc/index.html', facilities=facilities, info=data['info'])


@bp.route('/detail_info/<int:id>')
def detail_info(id):
    data = get_json("detail_info.json")
    info = data['info'][str(id)]

    db = get_db()
    facility = db.execute(
        'SELECT criticality_category, owner FROM facilities WHERE id = ?', (id,)
    ).fetchone()

    return render_template('calc/detail_info.html', info=info, id=id, facility=facility)


@bp.route('/questions/<int:id>', methods=('GET', 'POST'))
def questions(id):
    data = get_json("questions.json")

    db = get_db()
    sector = db.execute(
        'SELECT sector FROM facilities WHERE id = ?', (id,)
    ).fetchone()

    q = data['special_questions']['sector' + str(sector['sector'])] + data['questions']

    if request.method == 'POST':
        score = 0
        for i in range(len(q)):
            score += int(request.form['question__name--' + str(i)])

        first_group = [1, 3, 4, 5, 6, 7]
        if sector['sector'] in first_group:
            score = score / (19 * 4)
        else:
            score = score / (18 * 4)

        category = 0
        if 0.8 < score <= 1:
            category = 1
        elif 0.63 < score <= 0.8:
            category = 2
        elif 0.37 < score <= 0.63:
            category = 3
        elif 0.2 < score <= 0.37:
            category = 4
        else:
            category = 0

        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d')

        db.execute(
            'UPDATE facilities SET criticality_category = ?, check_date = ?'
            ' WHERE id = ?',
            (category, formatted_date, id)
        )
        db.commit()

        return redirect(url_for('calc.result', category=category))

    return render_template('calc/questions.html', questions=q)


@bp.route('/result/<int:category>')
def result(category):
    return render_template('calc/result.html', category=category)


def get_json(name):
    root = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(root, "static/data", name)
    data = json.load(open(json_url))

    return data
