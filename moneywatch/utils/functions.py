import datetime
import math
import re

from calendar import monthrange
from flask_babel import format_date, gettext


def get_date_from_string(date, format):

    return datetime.datetime.strptime(date, format).date()


def get_quarter_from_date(date):

    return (date.month - 1) // 3 + 1


def get_half_year_from_date(date):

    return (date.month - 1) // 6 + 1


def get_first_day_of_month(year=None, month=None):

    date_today = datetime.date.today()
    date_month = date_today.month
    date_year = date_today.year

    if month:
        date_month = month
    if year:
        date_year = year

    date_first = datetime.date(date_year, date_month, 1)

    return date_first


def get_last_day_of_month(year=None, month=None):

    date_first = get_first_day_of_month()

    date_last_year = date_first.year
    date_last_month = date_first.month

    if year:
        date_last_year = year

    if month:
        date_last_month = month

    if date_last_month == 12:
        date_last_year += 1
        date_last_month = 1
    else:
        date_last_month += 1

    date_first_next = datetime.date(date_last_year, date_last_month, 1)
    date_last_month = date_first_next - datetime.timedelta(days=1)

    return date_last_month


def get_number_of_months(start=None, end=None):

    start_date = get_first_day_of_month()
    end_date = get_last_day_of_month()

    if start:
        start_date = start

    if end:
        end_date = end

    diff = _monthdelta(start_date, end_date)

    if start_date == end_date:
        diff = 1

    return int(math.ceil(diff))


def _monthdelta(d1, d2):
    delta = 0
    while True:
        mdays = monthrange(d1.year, d1.month)[1]

        d1 += datetime.timedelta(days=mdays)
        if d1 < d2:
            delta += 1
        elif d1 == d2:
            delta += 1
            break
        else:
            break

    if d1 > d2:
        diff = d1 - d2
        delta += (monthrange(d2.year, d2.month)[1] - diff.days) / monthrange(d2.year, d2.month)[1]

    return delta


def add_months(date, months):
    date_new = date
    original_day = date.day
    maxdays_original = monthrange(date_new.year, date_new.month)[1]

    for dummy in range(months):
        year = date_new.year
        month = date_new.month

        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

        maxdays = monthrange(year, month)[1]

        # avoid 31.10 => 31.11 (does not exist, last day in november is 30.11)
        if original_day == maxdays_original or original_day > maxdays:
            date_new = datetime.date(year, month, maxdays)
        else:
            date_new = datetime.date(year, month, original_day)

    return date_new


def substract_months(date, months):
    date_new = date
    original_day = date.day
    maxdays_original = monthrange(date_new.year, date_new.month)[1]

    for dummy in range(months):
        year = date_new.year
        month = date_new.month

        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1

        maxdays_after = monthrange(year, month)[1]

        # avoid 31.10 => 31.11 (does not exist, last day in november is 30.11)
        if original_day == maxdays_original or original_day > maxdays_after:
            date_new = datetime.date(year, month, maxdays_after)
        else:
            date_new = datetime.date(year, month, original_day)

    return date_new


def is_same_month_in_list(date, date_list):

    result = False
    for item in date_list:
        if is_same_month(date, item):
            result = True
            break

    return result


def is_same_month(date1, date2):

    return True if date1.year == date2.year and date1.month == date2.month else False


def get_cyclic_dates_for_timerange(date, months_interval, start, end):

    result = []

    day = date.day

    while True:

        if date >= start and date <= end:
            result.append(date)

        date = add_months(date, months_interval)

        maxdays = monthrange(date.year, date.month)[1]

        # ensure 30.01 => 28.02 => 30.03
        if date.day == maxdays and day < maxdays:
            date = date.replace(day=day)

        if date > end:
            break

    return result


def get_babel_month_names():

    month_names = []

    for month in range(1, 13):
        d = datetime.date(2007, month, 1)
        month_names.append(format_date(d, "MMM"))

    return month_names


def get_label_by_interval(date, interval):

    month_names = get_babel_month_names()

    if interval == "12":
        return date.year
    elif interval == "6":
        return gettext(u'%(half_year)sH %(year)s', half_year=get_half_year_from_date(date), year=date.year)
    elif interval == "3":
        return gettext(u'Q%(quarter)s/%(year)s', quarter=get_quarter_from_date(date), year=date.year)
    else:
        return gettext("%(month_name)s %(year)s", month=date.month, month_name=month_names[date.month - 1], year=date.year)


def normalize_iban(value):

    value = value.upper()

    value = re.sub(r"[^A-Z0-9]+", "", value)

    return value


def is_valid_iban(value):

    value = normalize_iban(value)

    if not re.fullmatch(r"[A-Z]{2}\d{20}", value):
        return False

    return True


def format_iban_human(value):

    value = normalize_iban(value)
    items = []

    for index in range(0, len(value), 4):
        items.append(value[index: index + 4])

    return " ".join(items)
