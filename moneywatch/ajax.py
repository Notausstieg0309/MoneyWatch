from flask import (Blueprint, jsonify, url_for)
from flask_babel import format_currency
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

    return jsonify({
        "type": initial_transaction.type,
        "description": rule.description,
        "data": list(transactions_to_intervals(rule.regular, transactions, initial_transaction.id)),
    })



def transactions_to_intervals(interval, transactions, reference_id):

    tmp_valuta = 0
    tmp_transactions = []
    tmp_last_label = None

    def getTempDict():

        nonlocal tmp_valuta, tmp_transactions, tmp_last_label

        tmp_dict = {
            "valuta": round(tmp_valuta, 2),
            "valuta_formatted": format_currency(tmp_valuta, "EUR"),
            "ids": [transaction.id for transaction in tmp_transactions],
            "label": tmp_last_label,
        }

        tmp_dict["reference"] = 1 if reference_id in tmp_dict["ids"] else 0

        if tmp_dict["reference"] == 0:
            tmp_dict["link"] = url_for("overview.custom_overview", account_id=tmp_transactions[0].account_id, year=tmp_transactions[0].date.year, month=tmp_transactions[0].date.month, interval=interval, highlight=tmp_dict["ids"])

        tmp_valuta = 0
        tmp_transactions = []

        return tmp_dict

    for transaction in transactions:
        transaction_label = utils.get_label_for_date(transaction.date, interval)

        if tmp_last_label != transaction_label and tmp_last_label is not None:
            yield getTempDict()

        tmp_valuta += transaction.valuta
        tmp_last_label = transaction_label

        tmp_transactions.append(transaction)

    # add remaining items of the last interval
    if len(tmp_transactions) > 0:
        yield getTempDict()
