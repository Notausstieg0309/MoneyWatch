from flask import (Blueprint, flash, redirect, render_template, request, url_for, session)

from flask_babel import gettext
from sqlalchemy.exc import IntegrityError
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
            return render_template('accounts/add.html', colors=colors)
        else:

            new_account = Account(name=name, iban=utils.normalize_iban(iban), balance=balance, color=color)
            db.session.add(new_account)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash(gettext('An account with the same name or IBAN already exists.'))
                return render_template('accounts/add.html', colors=colors)

        if "import_items" in session and "account_not_found" in session:
            session.pop("account_not_found", None)
            return redirect(url_for('import.index', resume=1))
        else:
            return redirect(url_for('overview.index'))

    return render_template('accounts/add.html', colors=colors)


@bp.route('/accounts/delete/<int:id>/')
def delete(id):

    account = Account.query.filter_by(id=id).one_or_none()

    if account is not None:
        db.session.delete(account)
        db.session.commit()

    return redirect(url_for('overview.index'))


@bp.route('/accounts/change/<int:id>/', methods=('GET', 'POST'))
def change(id):

    current_account = Account.query.filter_by(id=id).one()

    if request.method == 'POST':

        error = None
        name = request.form['name']
        balance = request.form['balance']
        color = request.form['color']


        if not name:
            error = gettext('Name is required.')

        if color and color == "NONE":
            color = None

        if error is not None:
            flash(error)
        else:

            current_account.name = name
            current_account.balance = balance
            current_account.color = color

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash(gettext('An account with the same name already exists.'))
                return render_template('accounts/change.html', account=current_account, colors=colors)

            return redirect(url_for('overview.index'))

    return render_template('accounts/change.html', account=current_account, colors=colors)
