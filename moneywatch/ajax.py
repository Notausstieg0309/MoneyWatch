from flask import (
            Blueprint, jsonify, current_app, request
            )
from werkzeug.exceptions import abort

import moneywatch.utils.functions as utils

from moneywatch.utils.objects import Rule, Transaction
from moneywatch.utils.exceptions import *

from datetime import timedelta, datetime, date
from flask_babel import format_date

bp = Blueprint('ajax', __name__)
        
@bp.route('/ajax/transaction_chart/<int:transaction_id>/')
def transaction_chart_data(transaction_id):

    try:
        initial_transaction = Transaction(transaction_id)
    except Exception as e:
        return jsonify(None), 404
        
    rule = initial_transaction.rule

    if rule is None:
        return jsonify(None), 404
        
    transaction_date  = initial_transaction.date
    
    transactions_after = rule.getTransactions(transaction_date + timedelta(days=1), None, 12)
    transactions_before = rule.getTransactions(None, transaction_date - timedelta(days=1), 12, True)
    
    transactions = []
    transactions.extend(transactions_before)
    transactions.append(initial_transaction)
    transactions.extend(transactions_after)
    
    result = []
    month_names = []
    
    for month in range(1,13):
        d = date(2007, month, 1)
        month_names.append(format_date(d, "MMM"))
      
    for transaction in transactions:
        result.append({
                        "valuta": transaction.valuta,
                        "year": transaction.date.year,
                        "month": transaction.date.month,
                        "day": transaction.date.day,
                        "reference": 1 if transaction.id == initial_transaction.id else 0
                      })
    
        
    return jsonify({"type": initial_transaction.type, "regular": rule.regular, "description": rule.description, "data": result, "month_names": month_names})
