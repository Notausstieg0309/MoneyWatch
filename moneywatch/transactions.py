from flask import (
            Blueprint, flash, g, redirect, render_template, request, url_for,session, current_app, jsonify
            )
from werkzeug.exceptions import abort

import re

import moneywatch.utils.functions as utils
import datetime

from flask_babel import gettext


from moneywatch.utils.objects import Rule,Category,Transaction
from moneywatch.utils.exceptions import *

bp = Blueprint('transactions', __name__)


@bp.route('/transactions/')
def index():
    """Show all the transaction"""

    current_month = utils.get_first_day_of_month()
    last_month = utils.substract_months(current_month, 1)
    start = utils.get_first_day_of_month(last_month.year, last_month.month)
    end = datetime.date.today()
    
    transactions = Transaction.getTransactions(start, end)
    transactions.reverse()
    
    return render_template('transactions/index.html', transactions=transactions)


@bp.route('/transactions/edit/<int:id>/', methods=('GET', 'POST')) 
def edit(id):
    
    current_transaction = Transaction(id)
    
    if current_transaction.is_editable:
        
        if request.method == 'POST':
            error = None
            
            description = request.form['description'].strip()
            category_id = int(request.form['category_id'].strip())
            clear_rule = request.form.get('clear_rule', None)

            current_transaction.description = description
            current_transaction.category_id = category_id
            
            if clear_rule is not None:
                current_transaction.rule_id = None
                
            current_transaction.save()
            
            return redirect(url_for('overview.month_overview', year=current_transaction.date.year, month=current_transaction.date.month))
            
        categories = Category.getRootCategories(current_transaction.type)
        rules = Rule.getRulesByType(current_transaction.type)
        
        return render_template('transactions/edit.html', transaction=current_transaction, categories=categories, rules=rules)  
    else:
        flash(gettext("The transaction '%(description)s' cannot be edited anymore.", description=current_transaction.description))
        return redirect(url_for('overview.month_overview', year=current_transaction.date.year, month=current_transaction.date.month))
    

@bp.route('/transactions/single/<int:transaction_id>/')
def transaction_details(transaction_id):
    try:
        transaction = Transaction(transaction_id)
    except Exception as e:
        return jsonify(None), 404
    
    if transaction.type == "message":
        return jsonify(None), 404
        
    return  render_template('transactions/single_transaction.html', transaction=transaction)


@bp.errorhandler(NoSuchItemError)
def handle_no_such_transaction(error):
    current_app.logger.debug("transaction not found: %s" , error.data)
   
    return "Not found", 404

