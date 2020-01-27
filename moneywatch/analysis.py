from flask import (
            Blueprint, flash, current_app, g, redirect, render_template, request, url_for,session, jsonify
            )
from werkzeug.exceptions import abort

import datetime
import re

import moneywatch.utils.functions as utils

from moneywatch.utils.objects import Transaction, Rule, Category
from flask_babel import format_date, gettext



bp = Blueprint('analysis', __name__)


def createBaseData(start, end, interval):

    result = {}
    
    result["interval"] = interval
    
    if interval == "1":#
        result["start"] = format_date(start,gettext("yyyy/MM"))
        result["end"] = format_date(end,gettext("yyyy/MM"))
        result["month_names"] = utils.get_babel_month_names()
    elif interval == "3":
        result["start"] = gettext(u'Q%(quarter)s/%(year)s', quarter = utils.get_quarter_from_date(start), year = start.year)
        result["end"] = gettext(u'Q%(quarter)s/%(year)s', quarter = utils.get_quarter_from_date(end), year = end.year)
    elif interval == "12":
        result["start"] = str(start.year)
        result["end"] = str(end.year)
        
    return result
    
def getBalance(start, end, interval):

    result = createBaseData(start, end, interval)
    
    transactions = Transaction.getTransactions(utils.get_first_day_of_month(start.year, start.month), utils.get_last_day_of_month(end.year, end.month))
    
    transactions = filter(lambda x: x.type != "message", transactions)
    
    (result["sum"], result["data"]) = createResultForTransactions(transactions, interval)
   
    return result
    

def getBalanceByType(start, end, interval, type):

    result = createBaseData(start, end, interval)

    transactions = Transaction.getTransactions(utils.get_first_day_of_month(start.year, start.month), utils.get_last_day_of_month(end.year, end.month))

    (result["sum"], result["data"]) = createResultForTransactions(filter(lambda x: x.type == type, transactions), interval)
   
    return result
    
def getBalanceByRule(start, end, interval, rule_id):

    result = createBaseData(start, end, interval)
    
    rule = Rule(int(rule_id))
    
    transactions = rule.getTransactions(utils.get_first_day_of_month(start.year, start.month), utils.get_last_day_of_month(end.year, end.month))

    (result["sum"], result["data"]) = createResultForTransactions(transactions, interval)

    return result

def getBalanceByCategory(start, end, interval, category_id):

    result = createBaseData(start, end, interval)
    
    category = Category(int(category_id), start=utils.get_first_day_of_month(start.year, start.month), end=utils.get_last_day_of_month(end.year, end.month))
    
    transactions = category.transactions_with_childs
    transactions.sort(key=lambda x: x.date)
    
    (result["sum"], result["data"]) = createResultForTransactions(transactions, interval)
    
    if interval == "1":
        result["month_names"] = utils.get_babel_month_names()
     
    return result  

def transToDict(transaction):

    result = {}

    result["valuta"] = transaction.valuta
    result["description"] = transaction.description
    result["full_text"] = transaction.full_text
    result["date"] = format_date(transaction.date,gettext("yyyy-MM-dd"))
    result["category"] = transaction.category.name

    return result

def createResultForTransactions(transactions, interval):
    
    current_app.logger.debug("returned transactions: %s", transactions)
    tmp = {"valuta": 0, "count": 0, "transactions": []}
    
    result = []
    sum = 0
    
    if interval == "1":
            
        for transaction in transactions:
            
            if tmp.get("month", transaction.date.month) != transaction.date.month:
                tmp["valuta"] = round(tmp["valuta"],2)
                
                sum += tmp["valuta"]
                
                result.append(tmp.copy())
                
                tmp["valuta"] = 0
                tmp["count"] = 0
                tmp["transactions"] = []

            tmp["count"] += 1
            tmp["valuta"] += transaction.valuta
            tmp["month"] = transaction.date.month
            tmp["year"] = transaction.date.year
            tmp["transactions"].append(transToDict(transaction))

        if tmp["count"] > 0:
            tmp["valuta"] = round(tmp["valuta"],2)
            sum += tmp["valuta"]
            result.append(tmp)

    elif interval == "12":
        for transaction in transactions:
            
            if tmp.get("year", transaction.date.year) != transaction.date.year:
                tmp["valuta"] = round(tmp["valuta"],2)
                sum += tmp["valuta"]
                result.append(tmp.copy())
                tmp["valuta"] = 0
                tmp["count"] = 0
                tmp["transactions"] = []
                
            tmp["valuta"] += transaction.valuta
            tmp["count"] += 1
            tmp["year"] = transaction.date.year
            tmp["transactions"].append(transToDict(transaction))
        
        if tmp["count"] > 0:
            tmp["valuta"] = round(tmp["valuta"],2)
            sum += tmp["valuta"]
            result.append(tmp.copy())
            
    elif interval == "3":
        for transaction in transactions:
            quarter = utils.get_quarter_from_date(transaction.date)
           
            if tmp.get("quarter",quarter) != quarter:
                tmp["valuta"] = round(tmp["valuta"],2)
                tmp["quarter_formatted"] = gettext(u'Q%(quarter)s/%(year)s', quarter = tmp["quarter"], year = tmp["year"])
                sum += tmp["valuta"]
                result.append(tmp.copy())
                
                tmp["valuta"] = 0
                tmp["count"] = 0
                tmp["transactions"] = []
                
            tmp["valuta"] += transaction.valuta
            tmp["count"] += 1
            tmp["quarter"] = quarter
            tmp["year"] = transaction.date.year
            tmp["transactions"].append(transToDict(transaction))
        
        if tmp["count"] > 0:
            tmp["quarter_formatted"] = gettext(u'Q%(quarter)s/%(year)s', quarter = tmp["quarter"], year = tmp["year"])
            tmp["valuta"] = round(tmp["valuta"],2)
            sum += tmp["valuta"]
            result.append(tmp.copy())


    return (round(sum, 2), result)
           

@bp.route('/analysis/')

def index():


    oldest_transaction = Transaction.getOldestTransaction()
    newest_transaction = Transaction.getNewestTransaction()

    min_date = oldest_transaction.date.strftime("%Y-%m-%d")
    max_date = newest_transaction.date.strftime("%Y-%m-%d")

    years_start = oldest_transaction.date.year
    years_end = newest_transaction.date.year
    
    rules = {}    
    rules["in"] = Rule.getRulesByType("in")
    rules["out"] = Rule.getRulesByType("out")
    
    categories = {}
    categories["in"] = Category.getRootCategories("in", transactions=False)
    categories["out"] = Category.getRootCategories("out", transactions=False)
    
    return render_template('analysis/index.html', years_start = years_start, years_end = years_end, min_date = min_date, max_date = max_date, rules = rules, categories = categories)


@bp.route('/analysis/data/', methods=["POST"])
def data():

    data = request.form
    
    current_app.logger.debug("analysis data request with params: %s", data)
    
    start_date = utils.get_date_from_string(data["start"], "%Y-%m-%d")
    end_date = utils.get_date_from_string(data["end"], "%Y-%m-%d")
    
    if "type" in data:
        if data["type"] == "balance":
            return jsonify(getBalance(start_date, end_date, data["interval"]))
            
        if "subtype" in data:
            if data["subtype"] == "overall":
                return jsonify(getBalanceByType(start_date, end_date, data["interval"], data["type"]))
            elif data["subtype"] == "rule":
                return jsonify(getBalanceByRule(start_date, end_date, data["interval"], data["rule"]))
            elif data["subtype"] == "category":
                return jsonify(getBalanceByCategory(start_date, end_date, data["interval"], data["category"]))
            
            
        
    else:
        abort("400", "no type specified")
    
    return jsonify(data)
    
