from flask import (Blueprint, flash, redirect, render_template, request, url_for, abort)

import moneywatch.utils.functions as utils
from sqlalchemy import or_
from flask_babel import gettext

from moneywatch.utils.objects import db, Transaction, Account

bp = Blueprint('transactions', __name__)


@bp.route('/<int:account_id>/transactions/', methods=["POST", "GET"])
def index(account_id):
    """Show all the transaction"""

    account = Account.query.filter_by(id=account_id).one_or_none()

    if account is None:
        abort(404)

    scroll_url = url_for("transactions.scroll", account_id=account.id)

    return render_template('transactions/index.html', scroll_url=scroll_url)


@bp.route('/transactions/edit/<int:id>/', methods=('GET', 'POST'))
def edit(id):

    current_transaction = Transaction.query.filter_by(id=id).one_or_none()

    if current_transaction is None:
        abort(404)

    if current_transaction.is_editable:

        if request.method == 'POST':

            description = request.form['description'].strip()
            category_id = int(request.form['category'].strip())
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
        abort(404)

    if transaction.type == "message":
        abort(404)

    return render_template('transactions/single_transaction.html', transaction=transaction)


@bp.route('/transactions/multi/')
def transaction_details_multi():

    ids = request.args.getlist("id")

    ids = int_list(ids)

    if ids is None:
        abort(404)

    transactions = Transaction.query.filter(Transaction.id.in_(ids)).all()

    return render_template('transactions/multiple_transaction.html', transactions=transactions)


@bp.route('/<int:account_id>/transactions/messages/<int:year>/<int:month>/<int:month_count>/')
def transaction_messages(account_id, year, month, month_count):

    account = Account.query.filter_by(id=account_id).one_or_none()

    if account is None:
        abort(404)

    end_date = utils.add_months(utils.get_last_day_of_month(year, month), (month_count - 1))
    transactions = account.transactions_by_type("message", start=utils.get_first_day_of_month(year, month), end=end_date)

    return render_template('transactions/multiple_transaction.html', transactions=transactions)


@bp.route('/<int:account_id>/transactions/scroll/')
def scroll(account_id):

    data = request.args

    account = Account.query.filter_by(id=account_id).one_or_none()

    if account is None:
        abort(404)

    (previous_transaction, transactions) = get_scroll_items(account.id, data)

    return render_template('transactions/multiple_transaction.html', transactions=transactions, previous_transaction=previous_transaction).strip()


def int_list(values):

    result = []

    for value in values:
        try:
            result.append(int(value))
        except Exception:
            return None
    return result


def get_scroll_items(account_id, params):

    page_size = 50

    result = Transaction.query.filter_by(account_id=account_id)

    if "search" in params:
        term = params["search"]
        result = result.filter(or_(Transaction.description.contains(term, autoescape=True), Transaction.full_text.contains(term, autoescape=True)))

    result = result.order_by(Transaction.date.desc(), Transaction.id.desc())

    main_result = result.limit(page_size)

    prev_transaction = None

    if "page" in params:
        offset = (int(params["page"]) - 1) * page_size
        main_result = main_result.offset(offset)

        if int(params["page"]) > 1:
            prev_transaction = result.limit(1)
            prev_transaction = prev_transaction.offset(offset - 1).one_or_none()

    transactions = main_result.all()

    return (prev_transaction, transactions)
