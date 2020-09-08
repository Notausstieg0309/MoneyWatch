from flask import (Blueprint, jsonify)

import moneywatch.utils.functions as utils

from .utils.objects import Transaction

from datetime import timedelta

bp = Blueprint('ajax', __name__)


@bp.route('/ajax/transaction_chart/<int:transaction_id>/')
def transaction_chart_data(transaction_id):

    try:
        initial_transaction = Transaction.query.filter_by(id=transaction_id).one()
    except Exception:
        return jsonify(None), 404

    rule = initial_transaction.rule

    if rule is None:
        return jsonify(None), 404

    transaction_date = initial_transaction.date

    transactions_after = rule.getTransactions(transaction_date + timedelta(days=1), None, 12)
    transactions_before = rule.getTransactions(None, transaction_date - timedelta(days=1), 12, True)

    transactions = []
    transactions.extend(transactions_before)
    transactions.append(initial_transaction)
    transactions.extend(transactions_after)

    result = []
    month_names = utils.get_babel_month_names()

    for transaction in transactions:
        result.append({
            "valuta": transaction.valuta,
            "year": transaction.date.year,
            "month": transaction.date.month,
            "day": transaction.date.day,
            "reference": 1 if transaction.id == initial_transaction.id else 0
        })


    return jsonify({
        "type": initial_transaction.type,
        "account_id": initial_transaction.account_id,
        "regular": rule.regular,
        "description": rule.description,
        "data": result,
        "month_names": month_names
    })
