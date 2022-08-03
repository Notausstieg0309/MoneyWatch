from flask import (Blueprint, current_app, render_template, request, jsonify, url_for)
from werkzeug.exceptions import abort

import datetime

import moneywatch.utils.functions as utils

from moneywatch.utils.objects import Rule, Category, Account
from flask_babel import format_date, gettext, format_currency


bp = Blueprint('analysis', __name__)


def calcAccountBalanceFor(account_id, date):


    balance = None

    if account_id == "ALL":

        accounts = Account.query.all()
        balance = 0

        for account in accounts:
            balance += round(calcAccountBalanceFor(account.id, date), 2)

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

    result["start"] = utils.get_label_for_date(start, interval)
    result["end"] = utils.get_label_for_date(end, interval)

    return result


def getProfit(account_id, start, end, interval):

    result = createBaseData(start, end, interval)

    transactions = []

    if account_id == "ALL":
        accounts = Account.query.all()
        for account in accounts:
            transactions.extend(account.transactions(utils.get_first_day_of_month(start), utils.get_last_day_of_month(end)))

        # transactions are not in the correct date order as the transaction list is extended per account with the given timerange, we need to sort everything correctly
        transactions.sort(key=lambda x: x.date)
    else:
        account = Account.query.filter_by(id=account_id).one()
        transactions = account.transactions(utils.get_first_day_of_month(start), utils.get_last_day_of_month(end))

    transactions = filter(lambda x: x.type != "message", transactions)

    result.update(createResultForTransactions(interval, transactions, create_links=(account_id != "ALL")))

    return result


def getAccountBalance(account_id, start, end, interval):

    result = getProfit(account_id, start, end, interval)

    if "data" in result:

        if len(result["data"]) > 0:
            balance = calcAccountBalanceFor(account_id, end)

            # substract the first item from the sum as
            # otherwise the difference between the first and last item will not match
            result["sum"] = round(result["sum"] - result["data"][0]["valuta"], 2)
            result["sum_formatted"] = format_currency(result["sum"], "EUR")

        new_data = []
        old_data = result["data"]

        # reverse the list to get the latest item first,
        # from here we start to calculate the account balance
        # back to the oldest item
        old_data.reverse()

        for item in result["data"]:

            orig_valuta = item["valuta"]

            item["valuta"] = balance
            item["valuta_formatted"] = format_currency(item["valuta"], "EUR")

            balance = round(balance - orig_valuta, 2)

            new_data.append(item)

        # now reverse again, to get the oldest item
        # first which is the order to display the data
        new_data.reverse()

        result["data"] = new_data


    return result


def getSumByType(account_id, start, end, interval, trans_type):

    result = createBaseData(start, end, interval)

    account = Account.query.filter_by(id=account_id).one_or_none()

    if account:

        transactions = account.transactions_by_type(trans_type, utils.get_first_day_of_month(start), utils.get_last_day_of_month(end))

        result.update(createResultForTransactions(interval, transactions))

    return result


def getSumByRule(start, end, interval, rule_id):

    result = createBaseData(start, end, interval)

    rule = Rule.query.filter_by(id=rule_id).one()

    transactions = rule.transactions(utils.get_first_day_of_month(start), utils.get_last_day_of_month(end))

    result.update(createResultForTransactions(interval, transactions, show_transaction_details=True))

    return result


def getSumByCategory(start, end, interval, category_id):

    result = createBaseData(start, end, interval)

    category = Category.query.filter_by(id=category_id).one_or_none()

    if category is not None:
        category.setTimeframe(start, end)

    transactions = category.transactions_with_childs

    # transactions are not in the correct date order, sort here only once instead of multiple recursive sorting runs in Category.transactions_with_childs()
    transactions.sort(key=lambda x: x.date)

    result.update(createResultForTransactions(interval, transactions, highlight_category=category.id, show_transaction_details=True))

    return result


def transToDict(transaction):

    result = {}

    result["valuta"] = transaction.valuta
    result["valuta_formatted"] = format_currency(transaction.valuta, "EUR")
    result["description"] = transaction.description
    result["full_text"] = transaction.full_text
    result["date"] = format_date(transaction.date, gettext("yyyy-MM-dd"))
    result["category"] = transaction.category.name

    return result



def createResultForTransactions(interval, transactions, create_links=True, show_transaction_details=False, highlight_category=None, reference_id=None):

    data = []
    result = {}

    sum_valuta = 0

    tmp_valuta = 0
    tmp_count = 0
    tmp_transactions = []
    tmp_last_label = None

    def getTempDict():

        nonlocal tmp_valuta, tmp_count, tmp_transactions, tmp_last_label

        tmp_dict = {
            "valuta": round(tmp_valuta, 2),
            "valuta_formatted": format_currency(tmp_valuta, "EUR"),
            "count": tmp_count,
            "label": tmp_last_label,
        }

        if (create_links and show_transaction_details) or reference_id is not None:
            tmp_dict["ids"] = [transaction.id for transaction in tmp_transactions]

        if (create_links and highlight_category is not None and isinstance(highlight_category, int)):
            tmp_dict["category"] = highlight_category


        if reference_id is not None:
            tmp_dict["reference"] = 1 if reference_id in tmp_dict["ids"] else 0


        if create_links:
            if highlight_category is not None:
                args = {"hc": tmp_dict.get("category", None)}
            else:
                args = {"ht": tmp_dict.get("ids", None)}

            if interval == 3:
                tmp_dict["overview_link"] = url_for("overview.quarter_overview", account_id=tmp_transactions[0].account_id, year=tmp_transactions[0].date.year, quarter=utils.get_quarter_from_date(tmp_transactions[0].date), **args)
            elif interval == 6:
                tmp_dict["overview_link"] = url_for("overview.halfyear_overview", account_id=tmp_transactions[0].account_id, year=tmp_transactions[0].date.year, half=utils.get_half_year_from_date(tmp_transactions[0].date), **args)
            elif interval == 12:
                tmp_dict["overview_link"] = url_for("overview.year_overview", account_id=tmp_transactions[0].account_id, year=tmp_transactions[0].date.year, **args)
            else:
                tmp_dict["overview_link"] = url_for("overview.month_overview", account_id=tmp_transactions[0].account_id, year=tmp_transactions[0].date.year, month=tmp_transactions[0].date.month, **args)

            if(show_transaction_details):
                tmp_dict["transaction_details_link"] = url_for("transactions.transaction_details_multi", id=tmp_dict.get("ids", None))


        tmp_valuta = 0
        tmp_count = 0
        tmp_transactions = []

        tmp_dict.pop("ids", None)
        tmp_dict.pop("categories", None)
        return tmp_dict


    for transaction in transactions:
        transaction_label = utils.get_label_for_date(transaction.date, interval)

        if tmp_last_label != transaction_label and tmp_last_label is not None:
            sum_valuta += tmp_valuta
            data.append(getTempDict())

        tmp_count += 1
        tmp_valuta += transaction.valuta
        tmp_last_label = transaction_label

        tmp_transactions.append(transaction)

    # add remaining items of the last interval
    if tmp_count > 0:
        sum_valuta += tmp_valuta
        data.append(getTempDict())

    result["data"] = data
    result["sum"] = round(sum_valuta, 2)
    result["sum_formatted"] = format_currency(result["sum"], "EUR")

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

        if oldest_transaction is None and latest_transaction is None:
            item["disabled"] = 1
        else:
            item["end"] = latest_transaction.date.strftime("%Y-%m")
            item["start"] = oldest_transaction.date.strftime("%Y-%m")

        if oldest_transaction is not None:
            if oldest is None:
                oldest = oldest_transaction.date
            elif oldest > oldest_transaction.date:
                oldest = oldest_transaction.date

        if latest_transaction is not None:
            if newest is None:
                newest = latest_transaction.date
            elif latest_transaction is not None and newest < latest_transaction.date:
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

    current_app.logger.debug("analysis data request with params: %r", dict(data))

    start_date = utils.get_date_from_string(data["start"], "%Y-%m")
    end_date = utils.get_date_from_string(data["end"], "%Y-%m")

    end_date = utils.get_last_day_of_month(end_date)

    interval = int(data.get("interval", 1))

    if start_date > end_date:

        tmp = end_date
        end_date = start_date
        start_date = tmp

    if "type" in data:

        if data["type"] == "profit":
            return jsonify(getProfit(data["account_id"], start_date, end_date, interval))

        elif data["type"] == "balance":
            return jsonify(getAccountBalance(data["account_id"], start_date, end_date, interval))


        elif data["type"] == "in" or data["type"] == "out":

            if "subtype" in data:
                if data["subtype"] == "overall":
                    return jsonify(getSumByType(data["account_id"], start_date, end_date, interval, data["type"]))
                elif data["subtype"] == "rule":
                    return jsonify(getSumByRule(start_date, end_date, interval, data["rule"]))
                elif data["subtype"] == "category":
                    return jsonify(getSumByCategory(start_date, end_date, interval, data["category"]))
            else:
                abort("400", "no subtype specified")

        else:
            abort("400", "unknown type specified")
    else:
        abort("400", "no type specified")

    return jsonify(data)



@bp.route('/analysis/rules/<int:account_id>/<string:trans_type>/')
def json_rules(account_id, trans_type):

    account = Account.query.filter_by(id=account_id).one()

    result = []

    for rule in account.rules_by_type(trans_type, active=None):
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


@bp.route('/analysis/categories/<int:account_id>/<string:trans_type>/')
def json_categories(account_id, trans_type):

    account = Account.query.filter_by(id=account_id).one()

    result = []

    for category in account.categories(trans_type):
        result.extend(category.getCategoryIdsAndPaths(" > "))

    return jsonify(result)
