from flask import (
            Blueprint, flash, g, redirect, render_template, request, url_for,session, current_app, jsonify
            )
from werkzeug.exceptions import abort

import re

import moneywatch.utils.functions as utils
import datetime

from flask_babel import gettext
from sqlalchemy.orm import exc

from moneywatch.utils.objects import db,Rule,Category,Transaction, Account
from moneywatch.utils.exceptions import *

bp = Blueprint('transactions', __name__)


@bp.route('/transactions/<int:account_id>/')
def index(account_id):
    """Show all the transaction"""

    account = Account.query.filter_by(id=account_id).one()
    
    current_month = utils.get_first_day_of_month()
    last_month = utils.substract_months(current_month, 1)
    start = utils.get_first_day_of_month(last_month.year, last_month.month)
    end = datetime.date.today()
    
    transactions = account.transactions(start, end)
    
    transactions.reverse()
    
    return render_template('transactions/index.html', transactions=transactions)


@bp.route('/transactions/edit/<int:id>/', methods=('GET', 'POST')) 
def edit(id):
    
    current_transaction = Transaction.query.filter_by(id=id).one()
 
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
                
            db.session.commit()
            
            return redirect(url_for('overview.month_overview', account_id=current_transaction.account_id, year=current_transaction.date.year, month=current_transaction.date.month))
            
        categories = current_transaction.account.categories(current_transaction.type)
        rules = current_transaction.account.rules_by_type(current_transaction.type)
        
        return render_template('transactions/edit.html', transaction=current_transaction, categories=categories, rules=rules)  
    else:
        flash(gettext("The transaction '%(description)s' cannot be edited anymore.", description=current_transaction.description))
        return redirect(url_for('overview.month_overview', account_id=current_transaction.account_id, year=current_transaction.date.year, month=current_transaction.date.month))
    

@bp.route('/transactions/single/<int:id>/')
def transaction_details(id):
    
    transaction = Transaction.query.filter_by(id=id).one()
   
    if transaction is None:
        return jsonify(None), 404
    
    if transaction.type == "message":
        return jsonify(None), 404
        
    return  render_template('transactions/single_transaction.html', transaction=transaction)


@bp.route('/<int:account_id>/transactions/messages/<int:year>/<int:month>/<int:month_count>/')
def transaction_messages(account_id, year, month, month_count):
    try:
        account = Account.query.filter_by(id=account_id).one()
        
        end_date = utils.add_months(utils.get_last_day_of_month(year,month),(month_count-1))
        transactions = account.transactions_by_type("message", start=utils.get_first_day_of_month(year,month), end=end_date)
    except exc.NoResultFound as e:
        return jsonify(None), 404
        
    return  render_template('transactions/multiple_transaction.html', transactions=transactions)



@bp.errorhandler(NoSuchItemError)
def handle_no_such_transaction(error):
    current_app.logger.debug("transaction not found: %s" , error.data)
   
    return "Not found", 404

