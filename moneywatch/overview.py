from flask import (Blueprint, render_template, request)

import datetime

import moneywatch.utils.functions as utils

from moneywatch.utils.objects import Account


bp = Blueprint('overview', __name__)


def createOverview(account_id, start, end):

    account = Account.query.filter_by(id=account_id).one()

    oldest_transaction = account.oldest_transaction

    if oldest_transaction is not None and start < oldest_transaction.date:
        start = oldest_transaction.date

    if end < start:
        end = utils.get_last_day_of_month(start.year, start.month)

    current_month = start <= datetime.date.today() <= end

    list_in = account.categories("in", start=start, end=end)
    list_out = account.categories("out", start=start, end=end)

    sum_current_out = 0
    sum_current_in = 0

    sum_planned_out = 0
    sum_planned_in = 0

    sum_current_with_planned_transactions_in = 0
    sum_current_with_planned_transactions_out = 0

    for category in list_in:
        sum_current_in += category.valuta
        sum_planned_in += category.planned_valuta
        sum_current_with_planned_transactions_in += (category.valuta + category.planned_transactions_valuta)

    for category in list_out:
        sum_current_out += category.valuta
        sum_planned_out += category.planned_valuta
        sum_current_with_planned_transactions_out += (category.valuta + category.planned_transactions_valuta)

    particular_rules_dates_in = account.non_regular_rules("in", start=start, end=end)
    particular_rules_dates_out = account.non_regular_rules("out", start=start, end=end)

    months = utils.get_number_of_months(start, end)

    profit = {}

    profit['planned'] = {}
    profit['planned']['in'] = round(sum_planned_in, 2)
    profit['planned']['out'] = round(sum_planned_out, 2)

    profit['current'] = {}
    profit['current']['in'] = round(sum_current_in, 2)
    profit['current']['out'] = round(sum_current_out, 2)

    profit['current_with_planned_transactions'] = {}
    profit['current_with_planned_transactions']['in'] = round(sum_current_with_planned_transactions_in, 2)
    profit['current_with_planned_transactions']['out'] = round(sum_current_with_planned_transactions_out, 2)

    profit['current']['profit'] = round(sum_current_in + sum_current_out, 2)
    profit['planned']['profit'] = round(sum_planned_in + sum_planned_out, 2)
    profit['current_with_planned_transactions']['profit'] = round(sum_current_with_planned_transactions_in + sum_current_with_planned_transactions_out, 2)


    timing = {}

    timing["previous"] = utils.substract_months(start, months)
    timing["next"] = end + datetime.timedelta(days=1)
    timing["current_month_previous_year"] = utils.substract_months(start, 12)
    timing["current_month_next_year"] = utils.add_months(start, 12)
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

    highlight_ids = request.args.get("highlight", None)

    if highlight_ids:
        highlight_ids = str(highlight_ids).split(",")

    return render_template('overview/overview.html', account=account, list_in=list_in, list_out=list_out, profit=profit, timing=timing, current_month=current_month, particular_rules=particular_rules, messages=messages, highlight_ids=highlight_ids)


@bp.route('/')
def index():
    accounts = Account.query.all()

    sum = 0

    for account in accounts:
        sum += account.balance
    return render_template('overview/index.html', accounts=accounts, sum=sum)


@bp.route('/<int:account_id>/')
def overview(account_id):
    return createOverview(account_id, utils.get_first_day_of_month(), utils.get_last_day_of_month())


@bp.route('/<int:account_id>/<int:year>/')
def year_overview(account_id, year):
    return createOverview(account_id, utils.get_first_day_of_month(year, 1), utils.get_last_day_of_month(year, 12))


@bp.route('/<int:account_id>/<int:year>/<int:month>/')
def month_overview(account_id, year, month):
    return createOverview(account_id, utils.get_first_day_of_month(year, month), utils.get_last_day_of_month(year, month))


@bp.route('/<int:account_id>/<int:year>/<int:month>/<int:month_count>')
def custom_overview(account_id, year, month, month_count):
    return createOverview(account_id, utils.get_first_day_of_month(year, month), utils.add_months(utils.get_last_day_of_month(year, month), (month_count - 1)))
