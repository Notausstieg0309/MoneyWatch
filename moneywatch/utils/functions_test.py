from . import functions as utils

import pytest
import datetime

# get_date_from_string()
@pytest.mark.parametrize("input,format,expected", [
    ('2009-10-01', '%Y-%m-%d', datetime.date(2009, 10, 1)),
    ('2009.10.01', '%Y.%m.%d', datetime.date(2009, 10, 1)),
    ('12-31-2009', '%m-%d-%Y', datetime.date(2009, 12, 31)),
    
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
    (None, None, datetime.date(datetime.date.today().year, datetime.date.today().month, 1) ),
    (2009, None, datetime.date(2009, datetime.date.today().month, 1) ),
    (None, 12, datetime.date(datetime.date.today().year, 12, 1) ),
    (2009, 3, datetime.date(2009, 3, 1) ),
])
def test_get_first_day_of_month(year, month, expected):
    assert utils.get_first_day_of_month(year, month) == expected


# get_last_day_of_month()
@pytest.mark.parametrize("year,month,expected", [
    (2020, 1, datetime.date(2020,1, 31) ),
    (2020, 2, datetime.date(2020,2, 29) ),
    (2021, 2, datetime.date(2021,2, 28) ),
    (2100, 2, datetime.date(2100,2, 28) ),
    (2000, 2, datetime.date(2000,2, 29) ),
   
])
def test_get_last_day_of_month(year, month, expected):
    assert utils.get_last_day_of_month(year, month) == expected


# get_number_of_months()
@pytest.mark.parametrize("start,end,expected", [
    (None, None, 1 ),
    (datetime.date(2020,1, 1), datetime.date(2020, 1, 2),  1 ),
    (datetime.date(2020,1, 1), datetime.date(2020, 1, 31), 1 ),
    (datetime.date(2020,1, 1), datetime.date(2020, 2, 2),  2 ),
    (datetime.date(2020,1, 1), datetime.date(2020, 12, 31),  12 ),
    (datetime.date(2020,1, 1), datetime.date(2021, 1, 2),  13 ),
])
def test_get_number_of_months(start, end, expected):
    assert utils.get_number_of_months(start, end) == expected


# add_months()
@pytest.mark.parametrize("start,months,expected", [
    (datetime.date(2020,1, 1),  3,  datetime.date(2020, 4, 1) ),
    (datetime.date(2020,1, 28), 1,  datetime.date(2020, 2, 28) ),
    (datetime.date(2020,1, 29), 1,  datetime.date(2020, 2, 29) ),
    (datetime.date(2020,1, 29), 12,  datetime.date(2021, 1, 29) ),
    (datetime.date(2020,2, 29), 12,  datetime.date(2021, 2, 28) ),
    (datetime.date(2020,1, 30), 1,  datetime.date(2020, 2, 29) ),
    (datetime.date(2020,1, 30), 2,  datetime.date(2020, 3, 30) ),
    (datetime.date(2020,1, 31), 2,  datetime.date(2020, 3, 31) ),
    (datetime.date(2020,1, 31), 1,  datetime.date(2020, 2, 29) ),
    (datetime.date(2020,1, 31), 2,  datetime.date(2020, 3, 31) ),
    (datetime.date(2020,2, 29), 1,  datetime.date(2020, 3, 31) ),
])
def test_add_months(start, months, expected):
    assert utils.add_months(start, months) == expected


# substract_months()
@pytest.mark.parametrize("start,months,expected", [
    (datetime.date(2020, 4, 1),  3, datetime.date(2020,1, 1) ),
    (datetime.date(2020, 2, 28), 1,  datetime.date(2020,1, 28) ),
    (datetime.date(2020, 2, 29), 1,  datetime.date(2020,1, 31) ),
    (datetime.date(2020, 3, 29), 1,  datetime.date(2020,2, 29) ),
    (datetime.date(2020, 3, 29), 2,  datetime.date(2020,1, 29) ),
    (datetime.date(2020, 3, 30), 1,  datetime.date(2020,2, 29) ),
    (datetime.date(2020, 3, 31), 1,  datetime.date(2020,2, 29) ),
    (datetime.date(2020, 3, 31), 2,  datetime.date(2020,1, 31) ),

])
def test_substract_months(start, months, expected):
    assert utils.substract_months(start, months) == expected