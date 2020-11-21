from flask import (Blueprint, flash, redirect, render_template, request, url_for, jsonify)

import moneywatch.utils.functions as utils

from flask_babel import gettext

from moneywatch.utils.objects import db, Transaction, Account

bp = Blueprint('transactions', __name__)


@bp.route('/<int:account_id>/transactions/', methods=["POST", "GET"])
def index(account_id):
    """Show all the transaction"""

    account = Account.query.filter_by(id=account_id).one()

    transactions = []
    term = None


    if request.method == 'POST' and "search" in request.form and request.form["search"] and request.form["search"].strip() != "":
        term = request.form["search"]
        transactions = account.search_for_transactions(term)
    else:

        latest_transaction = account.latest_transaction

        if latest_transaction:

            end = latest_transaction.date
            start = utils.substract_months(end, 2)

            transactions = account.transactions(start, end)

        transactions.reverse()

    return render_template('transactions/index.html', transactions=transactions, term=term)


@bp.route('/transactions/edit/<int:id>/', methods=('GET', 'POST'))
def edit(id):

    current_transaction = Transaction.query.filter_by(id=id).one()

    if current_transaction.is_editable:

        if request.method == 'POST':

            description = request.form['description'].strip()
            category_id = int(request.form['category_id'].strip())
            clear_rule = request.form.get('clear_rule', None)

            current_transaction.description = description
            current_transaction.category_id = category_id

            if clear_rule is not None:
                current_transaction.rule_id = None
                current_transaction.trend = None

            db.session.commit()

            return redirect(url_for('overview.month_overview', account_id=current_transaction.account_id, year=current_transaction.date.year, month=current_transaction.date.month))

        categories = current_transaction.account.categories(current_transaction.type)
        rules = current_transaction.account.rules_by_type(current_transaction.type)

        return render_template('transactions/edit.html', transaction=current_transaction, categories=categories, rules=rules)
    else:
        flash(gettext("The transaction '%(description)s' cannot be edited anymore.", description=current_transaction.description))
        return redirect(url_for('overview.month_overview', account_id=current_transaction.account_id, year=current_transaction.date.year, month=current_transaction.date.month))


@bp.route('/transactions/single/<int:id>/')
def transaction_details_single(id):

    transaction = Transaction.query.filter_by(id=id).one_or_none()

    if transaction is None:
        return jsonify(None), 404

    if transaction.type == "message":
        return jsonify(None), 404

    return render_template('transactions/single_transaction.html', transaction=transaction)


@bp.route('/transactions/multi/')
def transaction_details_multi():

    ids = request.args.getlist("h")

    ids = int_list(ids)

    if ids is None:
        return jsonify(None), 404

    transactions = Transaction.query.filter(Transaction.id.in_(ids)).all()

    return render_template('transactions/multiple_transaction.html', transactions=transactions)


@bp.route('/<int:account_id>/transactions/messages/<int:year>/<int:month>/<int:month_count>/')
def transaction_messages(account_id, year, month, month_count):

    account = Account.query.filter_by(id=account_id).one_or_none()

    if account is None:
        return jsonify(None), 404

    end_date = utils.add_months(utils.get_last_day_of_month(year, month), (month_count - 1))
    transactions = account.transactions_by_type("message", start=utils.get_first_day_of_month(year, month), end=end_date)

    return render_template('transactions/multiple_transaction.html', transactions=transactions)


def int_list(values):

    result = []

    for value in values:
        try:
            result.append(int(value))
        except Exception:
            return None
    return result
