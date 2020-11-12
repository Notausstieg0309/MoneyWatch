from . import functions as utils

import pytest
import datetime


# get_date_from_string()
@pytest.mark.parametrize("input,format,expected", [
    ('2009-10-01', '%Y-%m-%d', datetime.date(2009, 10, 1)),
    ('2009.10.01', '%Y.%m.%d', datetime.date(2009, 10, 1)),
    ('12-31-2009', '%m-%d-%Y', datetime.date(2009, 12, 31))
])
def test_get_date_from_string(input, format, expected):
    assert utils.get_date_from_string(input, format) == expected


# get_quarter_from_date()
@pytest.mark.parametrize("input,expected", [
    (datetime.date(2009, 1, 1), 1),
    (datetime.date(2009, 2, 2), 1),
    (datetime.date(2009, 3, 2), 1),
    (datetime.date(2009, 4, 2), 2),
    (datetime.date(2009, 5, 2), 2),
    (datetime.date(2009, 6, 2), 2),
    (datetime.date(2009, 7, 2), 3),
    (datetime.date(2009, 8, 2), 3),
    (datetime.date(2009, 9, 2), 3),
    (datetime.date(2009, 10, 2), 4),
    (datetime.date(2009, 11, 2), 4),
    (datetime.date(2009, 12, 2), 4),
])
def test_get_quarter_from_date(input, expected):
    assert utils.get_quarter_from_date(input) == expected


# get_half_year_from_date()
@pytest.mark.parametrize("input,expected", [
    (datetime.date(2009, 1, 1), 1),
    (datetime.date(2009, 2, 2), 1),
    (datetime.date(2009, 3, 2), 1),
    (datetime.date(2009, 4, 2), 1),
    (datetime.date(2009, 5, 2), 1),
    (datetime.date(2009, 6, 2), 1),
    (datetime.date(2009, 7, 2), 2),
    (datetime.date(2009, 8, 2), 2),
    (datetime.date(2009, 9, 2), 2),
    (datetime.date(2009, 10, 2), 2),
    (datetime.date(2009, 11, 2), 2),
    (datetime.date(2009, 12, 2), 2),
])
def test_get_half_year_from_date(input, expected):
    assert utils.get_half_year_from_date(input) == expected


# get_first_day_of_month()
@pytest.mark.parametrize("year,month,expected", [
    (None, None, datetime.date(datetime.date.today().year, datetime.date.today().month, 1)),
    (2009, None, datetime.date(2009, datetime.date.today().month, 1)),
    (None, 12, datetime.date(datetime.date.today().year, 12, 1)),
    (2009, 3, datetime.date(2009, 3, 1)),
])
def test_get_first_day_of_month(year, month, expected):
    assert utils.get_first_day_of_month(year, month) == expected


# get_last_day_of_month()
@pytest.mark.parametrize("year,month,expected", [
    (2020, 1, datetime.date(2020, 1, 31)),
    (2020, 2, datetime.date(2020, 2, 29)),
    (2021, 2, datetime.date(2021, 2, 28)),
    (2100, 2, datetime.date(2100, 2, 28)),
    (2000, 2, datetime.date(2000, 2, 29))
])
def test_get_last_day_of_month(year, month, expected):
    assert utils.get_last_day_of_month(year, month) == expected


# get_first_day_of_quarter()
@pytest.mark.parametrize("year,quarter,expected", [
    (None, None, datetime.date(datetime.date.today().year, (((datetime.date.today().month - 1) // 3) + 1) * 3 - 2, 1)),
    (2009, None, datetime.date(2009, (((datetime.date.today().month - 1) // 3) + 1) * 3 - 2, 1)),
    (None, 2, datetime.date(datetime.date.today().year, 4, 1)),
    (2009, 3, datetime.date(2009, 7, 1)),
    (2020, 4, datetime.date(2020, 10, 1)),
])
def test_get_first_day_of_quarter(year, quarter, expected):
    assert utils.get_first_day_of_quarter(year, quarter) == expected


# get_last_day_of_quarter()
@pytest.mark.parametrize("year,quarter,expected", [
    (2020, 1, datetime.date(2020, 3, 31)),
    (2020, 2, datetime.date(2020, 6, 30)),
    (2021, 3, datetime.date(2021, 9, 30)),
    (2100, 2, datetime.date(2100, 6, 30)),
    (2000, 4, datetime.date(2000, 12, 31))
])
def test_get_last_day_of_quarter(year, quarter, expected):
    assert utils.get_last_day_of_quarter(year, quarter) == expected



# get_first_day_of_halfyear()
@pytest.mark.parametrize("year,half,expected", [
    (None, None, datetime.date(datetime.date.today().year, (((datetime.date.today().month - 1) // 6) + 1) * 6 - 5, 1)),
    (2009, None, datetime.date(2009, (((datetime.date.today().month - 1) // 6) + 1) * 6 - 5, 1)),
    (None, 2, datetime.date(datetime.date.today().year, 7, 1)),
    (2009, 1, datetime.date(2009, 1, 1)),
    (2020, 2, datetime.date(2020, 7, 1))
])
def test_get_first_day_of_halfyear(year, half, expected):
    assert utils.get_first_day_of_halfyear(year, half) == expected


# get_last_day_of_halfyear()
@pytest.mark.parametrize("year,half,expected", [
    (2020, 1, datetime.date(2020, 6, 30)),
    (2020, 2, datetime.date(2020, 12, 31)),
    (2021, 1, datetime.date(2021, 6, 30)),
    (2100, 2, datetime.date(2100, 12, 31))
])
def test_get_last_day_of_quarter(year, half, expected):
    assert utils.get_last_day_of_halfyear(year, half) == expected




# get_number_of_months()
@pytest.mark.parametrize("start,end,expected", [
    (None, None, 1),
    (datetime.date(2020, 1, 1), datetime.date(2020, 1, 2), 1),
    (datetime.date(2020, 1, 1), datetime.date(2020, 1, 31), 1),
    (datetime.date(2020, 1, 1), datetime.date(2020, 2, 2), 2),
    (datetime.date(2020, 1, 1), datetime.date(2020, 12, 31), 12),
    (datetime.date(2020, 1, 1), datetime.date(2021, 1, 2), 13),
])
def test_get_number_of_months(start, end, expected):
    assert utils.get_number_of_months(start, end) == expected


# add_months()
@pytest.mark.parametrize("start,months,expected", [
    (datetime.date(2020, 1, 1), 3, datetime.date(2020, 4, 1)),
    (datetime.date(2020, 1, 28), 1, datetime.date(2020, 2, 28)),
    (datetime.date(2020, 1, 29), 1, datetime.date(2020, 2, 29)),
    (datetime.date(2020, 1, 29), 12, datetime.date(2021, 1, 29)),
    (datetime.date(2020, 2, 29), 12, datetime.date(2021, 2, 28)),
    (datetime.date(2020, 1, 30), 1, datetime.date(2020, 2, 29)),
    (datetime.date(2020, 1, 30), 2, datetime.date(2020, 3, 30)),
    (datetime.date(2020, 1, 31), 2, datetime.date(2020, 3, 31)),
    (datetime.date(2020, 1, 31), 1, datetime.date(2020, 2, 29)),
    (datetime.date(2020, 1, 31), 2, datetime.date(2020, 3, 31)),
    (datetime.date(2020, 2, 29), 1, datetime.date(2020, 3, 31))
])
def test_add_months(start, months, expected):
    assert utils.add_months(start, months) == expected


# substract_months()
@pytest.mark.parametrize("start,months,expected", [
    (datetime.date(2020, 4, 1), 3, datetime.date(2020, 1, 1)),
    (datetime.date(2020, 2, 28), 1, datetime.date(2020, 1, 28)),
    (datetime.date(2020, 2, 29), 1, datetime.date(2020, 1, 31)),
    (datetime.date(2020, 3, 29), 1, datetime.date(2020, 2, 29)),
    (datetime.date(2020, 3, 29), 2, datetime.date(2020, 1, 29)),
    (datetime.date(2020, 3, 30), 1, datetime.date(2020, 2, 29)),
    (datetime.date(2020, 3, 31), 1, datetime.date(2020, 2, 29)),
    (datetime.date(2020, 3, 31), 2, datetime.date(2020, 1, 31))
])
def test_substract_months(start, months, expected):
    assert utils.substract_months(start, months) == expected


# is_same_month_in_list()
@pytest.mark.parametrize("date,expected", [
    (datetime.date(2020, 1, 19), True),
    (datetime.date(2020, 1, 16), True),
    (datetime.date(2020, 4, 16), False),
    (datetime.date(2019, 3, 14), False),
    (datetime.date(2020, 6, 19), True),
    (datetime.date(2020, 9, 30), False),
    (datetime.date(2020, 12, 30), True),
])
def test_is_same_month_in_list(date, expected):

    date_list = [
        datetime.date(2020, 1, 16),
        datetime.date(2020, 2, 29),
        datetime.date(2020, 3, 4),
        datetime.date(2020, 6, 5),
        datetime.date(2020, 12, 31),
    ]

    assert utils.is_same_month_in_list(date, date_list) == expected


# is_same_month()
@pytest.mark.parametrize("date1,date2,expected", [
    (datetime.date(2020, 1, 19), datetime.date(2020, 1, 1), True),
    (datetime.date(2020, 1, 16), datetime.date(2020, 1, 31), True),
    (datetime.date(2020, 1, 16), datetime.date(2021, 1, 16), False),
    (datetime.date(2020, 2, 16), datetime.date(2020, 1, 16), False),
])
def test_is_same_month(date1, date2, expected):

    assert utils.is_same_month(date1, date2) == expected


# get_cyclic_dates_for_timerange()
@pytest.mark.parametrize("date,months_interval,start,end,expected", [
    (datetime.date(2020, 9, 19), 1, datetime.date(2020, 9, 1), datetime.date(2020, 10, 31), [datetime.date(2020, 9, 19), datetime.date(2020, 10, 19)]),
    (datetime.date(2020, 1, 29), 1, datetime.date(2020, 1, 1), datetime.date(2020, 3, 31), [datetime.date(2020, 1, 29), datetime.date(2020, 2, 29), datetime.date(2020, 3, 29)]),
    (datetime.date(2020, 1, 30), 1, datetime.date(2020, 1, 1), datetime.date(2020, 3, 31), [datetime.date(2020, 1, 30), datetime.date(2020, 2, 29), datetime.date(2020, 3, 30)]),
    (datetime.date(2020, 5, 11), 3, datetime.date(2020, 1, 1), datetime.date(2020, 12, 31), [datetime.date(2020, 5, 11), datetime.date(2020, 8, 11), datetime.date(2020, 11, 11)]),
    (datetime.date(2020, 1, 31), 1, datetime.date(2020, 1, 1), datetime.date(2020, 4, 30), [datetime.date(2020, 1, 31), datetime.date(2020, 2, 29), datetime.date(2020, 3, 31), datetime.date(2020, 4, 30)]),
])
def test_get_cyclic_dates_for_timerange(date, months_interval, start, end, expected):

    assert utils.get_cyclic_dates_for_timerange(date, months_interval, start, end) == expected


# normalize_iban()
@pytest.mark.parametrize("iban,expected", [
    ("DE73 7294 0493 0000 4030 05", "DE73729404930000403005"),
    ("'DE73 - 7294 - 0493 - 0000 - 4030 - 05'", "DE73729404930000403005"),
    ("DE73729404930000403005", "DE73729404930000403005")
])
def test_normalize_iban(iban, expected):

    assert utils.normalize_iban(iban) == expected


# is_valid_iban()
@pytest.mark.parametrize("iban,expected", [
    ("DE73 7294 0493 0000 4030 05", True),
    ("'DE73 - 7294 - 0493 - 0000 - 4030 - 05'", True),
    ("DE73729404930000403005", True),
    ("DE7372940493000040300", False)
])
def test_is_valid_iban(iban, expected):

    assert utils.is_valid_iban(iban) == expected
