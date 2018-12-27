from flask import (
            Blueprint, flash, g, redirect, render_template, request, url_for,session
            )
from werkzeug.exceptions import abort

import re

import moneywatch.utils.functions as utils
import datetime

from flask_babel import gettext


from moneywatch.utils.objects import Rule,Category, Transaction

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

