from flask import (
            Blueprint, flash, current_app, g, redirect, render_template, request, url_for,session, jsonify
            )
from werkzeug.exceptions import abort

import datetime
import re

import moneywatch.utils.functions as utils

from moneywatch.utils.objects import Transaction, Rule, Category, Account
from flask_babel import format_date, gettext



bp = Blueprint('analysis', __name__)


def calcAbsAccountBalanceFor(account_id, date):


    balance = None

    if account_id == "ALL":

        accounts = Account.query.all()
        balance = 0

        for account in accounts:
            balance += round(calcAbsAccountBalanceFor(account.id, date), 2)

    else:

        account = Account.query.filter_by(id=account_id).one()
        
        balance = account.balance

        last_transaction = account.latest_transaction
        
        if last_transaction:
        
            start = date + datetime.timedelta(days=1)
    
            transactions = account.transactions(start, last_transaction.date)
            
            for transaction in transactions:
                balance = round(balance - transaction.valuta, 2)

    return balance
          
    
def createBaseData(start, end, interval):

    result = {}
    
    result["interval"] = interval

    result["start"] = getLabelForDate(start, interval)
    result["end"] =  getLabelForDate(end, interval)
        
    return result
    
def getRelativeBalance(account_id, start, end, interval):

    result = createBaseData(start, end, interval)

    transactions = []

    if account_id == "ALL":
        accounts = Account.query.all()
        for account in accounts:
            transactions.extend(account.transactions(utils.get_first_day_of_month(start.year, start.month), utils.get_last_day_of_month(end.year, end.month)))
    else:
        account = Account.query.filter_by(id=account_id).one()
        transactions = account.transactions(utils.get_first_day_of_month(start.year, start.month), utils.get_last_day_of_month(end.year, end.month))
    
    transactions = filter(lambda x: x.type != "message", transactions)
    
    result = createResultForTransactions(result, transactions)
   
    return result

def getAbsoluteBalance(account_id, start, end, interval):

    result = getRelativeBalance(account_id, start, end, interval)
    
    if "data" in result:
    
        if len(result["data"]) > 0:
            balance = calcAbsAccountBalanceFor(account_id, end)
            
        new_data = []
        old_data = result["data"]
        
        old_data.reverse()
        
        for item in result["data"]:
        
            orig_valuta = item["valuta"]
            
            item["valuta"] = balance

            balance = round(balance - orig_valuta, 2)
            
            new_data.append(item)
    
        new_data.reverse()
        result["data"] = new_data
    
   
    return result

def getBalanceByType(account_id, start, end, interval, type_val):

    result = createBaseData(start, end, interval)

    account = Account.query.filter_by(id=account_id).one_or_none()
    
    if account:
    
        transactions = account.transactions_by_type(type_val, utils.get_first_day_of_month(start.year, start.month), utils.get_last_day_of_month(end.year, end.month))

        result = createResultForTransactions(result, transactions)
     
    return result
    
def getBalanceByRule(start, end, interval, rule_id):

    result = createBaseData(start, end, interval)
    
    rule = Rule.query.filter_by(id=rule_id).one()
    
    transactions = rule.getTransactions(utils.get_first_day_of_month(start.year, start.month), utils.get_last_day_of_month(end.year, end.month))

    result = createResultForTransactions(result, transactions)

    return result

def getBalanceByCategory(start, end, interval, category_id):

    result = createBaseData(start, end, interval)
    
    category = Category.query.filter_by(id=category_id).one_or_none();
    
    if category is not None:
        category.setTimeframe(start, end)
    
    transactions = category.transactions_with_childs
    
    # transactions are not in the correct date order, sort here only once instead of multiple recursive sorting runs in Category.transactions_with_childs()
    transactions.sort(key=lambda x: x.date)
    
    result = createResultForTransactions(result, transactions)
     
    return result  

def transToDict(transaction):

    result = {}

    result["valuta"] = transaction.valuta
    result["description"] = transaction.description
    result["full_text"] = transaction.full_text
    result["date"] = format_date(transaction.date,gettext("yyyy-MM-dd"))
    result["category"] = transaction.category.name

    return result


def getLabelForDate(date, interval):

    month_names = utils.get_babel_month_names()

    if interval == "12":
        return date.year
    elif interval == "6":
        return gettext(u'%(half_year)sH %(year)s', half_year = utils.get_half_year_from_date(date), year = date.year)
    elif interval == "3":
        return gettext(u'Q%(quarter)s/%(year)s', quarter = utils.get_quarter_from_date(date), year = date.year)
    else:
        return gettext("%(month_name)s %(year)s", month_name = month_names[date.month-1], year = date.year)    


def createResultForTransactions(result, transactions):
    
    tmp = {"valuta": 0, "count": 0, "transactions": []}
    
    data = []
    sum = 0
    
    interval = result["interval"]

    for transaction in transactions:
        transaction_label = getLabelForDate(transaction.date, interval)

        if tmp.get("label", transaction_label) != transaction_label:
            sum = round(sum + tmp["valuta"], 2)
            
            data.append(tmp.copy())
            
            tmp["valuta"] = 0
            tmp["count"] = 0
            tmp["transactions"] = []

        tmp["count"] += 1
        tmp["valuta"] = round(tmp["valuta"] + transaction.valuta, 2)
        tmp["label"] = transaction_label
        
        tmp["transactions"].append(transToDict(transaction))

    # add remaining items of the last interval
    if tmp["count"] > 0:
        sum = round(sum + tmp["valuta"], 2)
        data.append(tmp)

    result["data"] = data
    result["sum"] = sum 

    return result
           

@bp.route('/analysis/')
def index():
    accounts = Account.query.all()
    
    account_list = []
    oldest = None
    newest = None

    for account in accounts:
    
        item = {}
        latest_transaction = account.latest_transaction
        oldest_transaction = account.oldest_transaction
        
        item["id"] = account.id
        item["name"] = account.name
        
        if oldest_transaction and latest_transaction is None:
            item["disabled"] = 1
        else:
            item["end"] = latest_transaction.date.strftime("%Y-%m")
            item["start"] = oldest_transaction.date.strftime("%Y-%m")

        if oldest is None:
            oldest = oldest_transaction.date   
        elif oldest > oldest_transaction.date:
            oldest = oldest_transaction.date

        if newest is None:
            newest = latest_transaction.date   
        elif newest < latest_transaction.date:
            newest = latest_transaction.date

        account_list.append(item)
        
    if oldest is not None:
        oldest = oldest.strftime("%Y-%m")

    if newest is not None:
        newest = newest.strftime("%Y-%m")
        
    return render_template('analysis/index.html', account_list=account_list, oldest=oldest, newest=newest)


@bp.route('/analysis/data/', methods=["POST"])
def data():

    data = request.form
    
    current_app.logger.debug("analysis data request with params: %s", data)
    
    start_date = utils.get_date_from_string(data["start"], "%Y-%m")
    end_date = utils.get_date_from_string(data["end"], "%Y-%m")
    
    end_date = utils.get_last_day_of_month(year=end_date.year, month=end_date.month)
    
    if start_date > end_date:
        
        tmp = end_date
        end_date = start_date
        start_date = tmp
        
    

    
    
    
    if "type" in data:
    
        if data["type"] == "balance_relative":
            return jsonify(getRelativeBalance(data["account_id"], start_date, end_date, data["interval"]))
            
        elif  data["type"] == "balance_absolute":
           return jsonify(getAbsoluteBalance(data["account_id"], start_date, end_date, data["interval"]))
            
        
        elif data["type"] == "in" or data["type"] == "out":
        
            if "subtype" in data:
                if data["subtype"] == "overall":
                    return jsonify(getBalanceByType(data["account_id"], start_date, end_date, data["interval"], data["type"]))
                elif data["subtype"] == "rule":
                    return jsonify(getBalanceByRule(start_date, end_date, data["interval"], data["rule"]))
                elif data["subtype"] == "category":
                    return jsonify(getBalanceByCategory(start_date, end_date, data["interval"], data["category"]))
            else:
                abort("400", "no subtype specified")
            
        else:
            abort("400", "unknown type specified")
    else:
        abort("400", "no type specified")
    
    return jsonify(data)
    


@bp.route('/analysis/rules/<int:account_id>/<string:type>/')
def json_rules(account_id, type):

    account = Account.query.filter_by(id=account_id).one()
    
    result = []

    for rule in account.rules_by_type(type):
        item = {}
        item["id"] = rule.id        
        item["name"] = rule.name

        oldest_transaction = rule.oldest_transaction
        latest_transaction = rule.latest_transaction()

        if oldest_transaction is None and latest_transaction is None:
            item["disabled"] = 1
        else:
            item["start"] = oldest_transaction.date.strftime("%Y-%m")
            item["end"] = latest_transaction.date.strftime("%Y-%m")
            

        result.append(item)
            
    return jsonify(result)


@bp.route('/analysis/categories/<int:account_id>/<string:type>/')
def json_categories(account_id, type):

    account = Account.query.filter_by(id=account_id).one()
    
    result = []

    for category in account.categories(type):
        result.extend(category.getCategoryIdsAndPaths(" > "))
            
    return jsonify(result)