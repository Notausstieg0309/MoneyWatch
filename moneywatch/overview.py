from flask import (
            Blueprint, flash, current_app, g, redirect, render_template, request, url_for,session
            )
from werkzeug.exceptions import abort

import datetime
import re

import moneywatch.utils.functions as utils

from moneywatch.utils.objects import Category, Transaction, Rule, Account




bp = Blueprint('overview', __name__)

def createOverview(account_id, start, end):
    
    account = Account.query.filter_by(id=account_id).one()
    
    oldest_transaction = account.oldest_transaction
   
    if oldest_transaction is not None and start < oldest_transaction.date:
        start = oldest_transaction.date
   
    if end < start:
        end = utils.get_last_day_of_month(start.year,start.month)
   
    current_month = start <= datetime.date.today() <= end
    
    list_in =  account.categories("in", start=start, end=end)
    list_out = account.categories("out", start=start, end=end)
    
    sum_current_out = 0
    sum_current_in = 0
    
    for category in list_out:
        sum_current_out += category.valuta
        
    for category in list_in:
        sum_current_in += category.valuta
        
    sum_planned_out = 0
    sum_planned_in = 0    
    
    for category in list_in:
        sum_planned_in += category.planned_valuta

    for category in list_out:
        sum_planned_out += category.planned_valuta
        
        
    sum_current_with_planned_transactions_in = 0
    sum_current_with_planned_transactions_out = 0    
    
    for category in list_in:
        sum_current_with_planned_transactions_in += category.valuta + category.planned_transactions_valuta

    for category in list_out:
        sum_current_with_planned_transactions_out += category.valuta + category.planned_transactions_valuta

    particular_rules_dates_in = account.getNonMonthlyRegularRulesForTimeframe("in", start=start, end=end)
    particular_rules_dates_out = account.getNonMonthlyRegularRulesForTimeframe("out", start=start, end=end)
    

    months = utils.get_number_of_months(start,end)

    balance = {}
    
    balance['planned'] = {}
    balance['planned']['in'] = sum_planned_in
    balance['planned']['out'] = sum_planned_out
    
    balance['current'] = {}
    balance['current']['in'] = sum_current_in
    balance['current']['out'] = sum_current_out
    
    balance['current_with_planned_transactions'] = {}
    balance['current_with_planned_transactions']['in'] = sum_current_with_planned_transactions_in
    balance['current_with_planned_transactions']['out'] = sum_current_with_planned_transactions_out
    
    balance['current']['balance'] = sum_current_in + sum_current_out
    balance['planned']['balance'] = sum_planned_in + sum_planned_out
    balance['current_with_planned_transactions']['balance'] = sum_current_with_planned_transactions_in + sum_current_with_planned_transactions_out


    timing = {}
    
    timing["previous"] =  utils.substract_months(start, months)
    timing["next"] = end + datetime.timedelta(days=1)
    timing["current_month_previous_year"] = utils.substract_months(start,12)
    timing["current_month_next_year"] = utils.add_months(start,12)
    timing["months"] = months
    timing["start"] = start
    timing["end"] = end
    
    if oldest_transaction:
        timing["oldest"] = oldest_transaction.date
        
    particular_rules = {}
    
    particular_rules["in"] = particular_rules_dates_in
    particular_rules["out"] = particular_rules_dates_out
    particular_rules["count"] = len(particular_rules_dates_in) + len(particular_rules_dates_out)
    
    
    messages = len(account.transactions_by_type("message", start=start, end=end))


    return render_template('overview/overview.html', account=account, list_in=list_in, list_out=list_out, balance=balance, timing=timing, current_month=current_month, particular_rules=particular_rules, messages=messages) 
     
@bp.route('/')
def index():
    accounts = Account.query.all()
    return render_template('overview/index.html',accounts=accounts)
        
@bp.route('/<int:account_id>/')
def overview(account_id):
   return  createOverview(account_id, utils.get_first_day_of_month(), utils.get_last_day_of_month())
    
@bp.route('/<int:account_id>/<int:year>/')
def year_overview(account_id, year):
   return  createOverview(account_id, utils.get_first_day_of_month(year,1), utils.get_last_day_of_month(year,12))
    
@bp.route('/<int:account_id>/<int:year>/<int:month>/')
def month_overview(account_id, year, month):
   return  createOverview(account_id, utils.get_first_day_of_month(year,month), utils.get_last_day_of_month(year,month))

@bp.route('/<int:account_id>/<int:year>/<int:month>/<int:month_count>')
def custom_overview(account_id, year, month, month_count):
   return  createOverview(account_id, utils.get_first_day_of_month(year,month), utils.add_months(utils.get_last_day_of_month(year,month),(month_count-1)))
   