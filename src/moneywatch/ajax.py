from flask import (Blueprint, jsonify)

from moneywatch.analysis import createResultForTransactions
from moneywatch.utils.objects import Transaction
from moneywatch.utils.functions import add_months, substract_months, get_first_day_of_month, get_last_day_of_month

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

    if not rule.regular:
        return jsonify(None), 404

    if rule.regular == 1:
        months = 12
    elif rule.regular > 1 and rule.regular < 12:
        months = 24
    elif rule.regular == 12:
        months = 48
    else:
        months = 12

    transactions = rule.transactions(get_first_day_of_month(date=substract_months(transaction_date, months)), get_last_day_of_month(date=add_months(transaction_date, months)))

    result = {
        "type": initial_transaction.type,
        "description": rule.description
    }

    result.update(createResultForTransactions(rule.regular, transactions, create_links=True, reference_id=initial_transaction.id))

    return jsonify(result)
