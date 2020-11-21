from flask import (Blueprint, jsonify, url_for)
from flask_babel import format_currency
import moneywatch.utils.functions as utils
from moneywatch.analysis import createResultForTransactions

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

    result = {
        "type": initial_transaction.type,
        "description": rule.description
    }

    result.update(createResultForTransactions(rule.regular, transactions, highlight_links=True, reference_id=initial_transaction.id))

    return jsonify(result)
