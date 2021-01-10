from flask import (Blueprint, flash, redirect, render_template, request, url_for)

from flask_babel import gettext

from moneywatch.utils.objects import db, Account

import moneywatch.utils.functions as utils
import re

bp = Blueprint('accounts', __name__)


colors = (
         ("red lighten-4", "ffcdd2"),
         ("blue lighten-4", "bbdefb"),
         ("green lighten-4", "c8e6c9"),
         ("yellow lighten-4", "fff9c4"),
         ("orange lighten-4", "ffe0b2"),
         ("purple lighten-4", "e1bee7")
)


@bp.route('/accounts/add/', methods=('GET', 'POST'))
def add():

    if request.method == 'POST':
        error = None
        name = request.form['name']
        iban = request.form['iban']
        balance = request.form['balance'].replace(",", ".")
        color = request.form['color']

        if not name:
            error = gettext('Name is required.')

        if not iban:
            error = gettext('IBAN is required.')

        if not utils.is_valid_iban(iban):
            error = gettext('The provided IBAN is not valid')

        if re.match(r'^-?\d+(?:\.\d{1,2})?$', balance) is None:
            error = gettext('The provided balance is not a valid numeric value.')

        if color and color == "NONE":
            color = None


        if error is not None:
            flash(error)
        else:

            new_account = Account(name=name, iban=utils.normalize_iban(iban), balance=balance, color=color)
            db.session.add(new_account)
            db.session.commit()

            return redirect(url_for('overview.index'))

    return render_template('accounts/add.html', colors=colors)


@bp.route('/accounts/delete/<int:id>/')
def delete(id):

    Account.query.filter_by(id=id).delete()
    db.session.commit()

    return redirect(url_for('overview.index'))


@bp.route('/accounts/change/<int:id>/', methods=('GET', 'POST'))
def change(id):

    current_account = Account.query.filter_by(id=id).one()

    if request.method == 'POST':

        error = None
        name = request.form['name']
        iban = request.form['iban']
        balance = request.form['balance']
        color = request.form['color']


        if not name:
            error = gettext('Name is required.')

        if not iban:
            error = gettext('IBAN is required.')

        if not utils.is_valid_iban(iban):
            error = gettext('The provided IBAN is not valid')

        if color and color == "NONE":
            color = None

        if error is not None:
            flash(error)
        else:

            current_account.name = name
            current_account.iban = utils.normalize_iban(iban)
            current_account.balance = balance
            current_account.color = color

            db.session.commit()

            return redirect(url_for('overview.index'))

    return render_template('accounts/change.html', account=current_account, colors=colors)
