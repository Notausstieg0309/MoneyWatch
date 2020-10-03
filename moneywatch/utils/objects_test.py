
from .objects import Account, Category, Rule, Transaction, PlannedTransaction

import pytest

import datetime
from datetime import timedelta




#   _____  ____ _______        _   _____        _
#  |  __ \|  _ \__   __|      | | |  __ \      | |
#  | |  | | |_) | | | ___  ___| |_| |  | | __ _| |_ __ _
#  | |  | |  _ <  | |/ _ \/ __| __| |  | |/ _` | __/ _` |
#  | |__| | |_) | | |  __/\__ \ |_| |__| | (_| | || (_| |
#  |_____/|____/  |_|\___||___/\__|_____/ \__,_|\__\__,_|
#  ======================================================
#

today = datetime.date.today()

start = today - datetime.timedelta(weeks=8)
start = datetime.date(year=start.year, month=start.month, day=1)


@pytest.fixture
def db_filled(db):

    # Accounts

    account = Account(id=1, name="Main Account", balance=0, iban="DE67100200301230002345")
    db.session.add(account)

    # Categories

    cat_in_main = Category(id=1, name="Main Category IN", type="in")
    db.session.add(cat_in_main)

    cat_in_sub1 = Category(id=2, name="Main Category SUB1", type="in", parent_id=None)
    db.session.add(cat_in_sub1)

    cat_out_main = Category(id=3, name="Main Category OUT", type="out", parent_id=None)
    db.session.add(cat_out_main)

    cat_out_sub1 = Category(id=4, name="Main Category SUB1", type="out", parent_id=None)
    db.session.add(cat_out_sub1)

    cat_out_sub2 = Category(id=5, name="Main Category SUB2", type="out", parent_id=None)
    db.session.add(cat_out_sub2)

    cat_out_subsub1 = Category(id=6, name="Sub-Sub Category SUBSUB1", budget_monthly=200, type="out", parent_id=cat_out_sub2.id)
    db.session.add(cat_out_subsub1)

    cat_out_sub3 = Category(id=7, name="Main Category SUB3 with overdue", type="out", parent_id=None)
    db.session.add(cat_out_sub3)

    # Rules

    rule_in_1 = Rule(id=1, name="Rule 1", type="in", category_id=cat_in_main.id, pattern="PATTERN1", description="Description - Rule 1")
    db.session.add(rule_in_1)

    rule_in_2 = Rule(id=2, name="Rule 2", type="in", category_id=cat_in_sub1.id, pattern="PATTERN2", regular=1, next_valuta=29.98, next_due=today + datetime.timedelta(days=15), description="Description - Rule 2")
    db.session.add(rule_in_2)

    rule_out_1 = Rule(id=3, name="Rule 3", type="out", category_id=cat_out_sub1.id, pattern="PATTERN3", regular=3, next_valuta=293.29, next_due=today + datetime.timedelta(days=3), description="Description - Rule 3")
    db.session.add(rule_out_1)

    rule_out_2 = Rule(id=4, name="Rule 4", type="out", category_id=cat_out_sub1.id, pattern=r"PATTERN4.*PATTERN4", description="Description - Rule 4")
    db.session.add(rule_out_2)

    rule_out_3 = Rule(id=5, name="Rule 5", type="out", category_id=cat_out_sub2.id, pattern="PATTERN5", regular=1, next_valuta=20, next_due=today + timedelta(days=2), description="Description - Rule 5")
    db.session.add(rule_out_3)

    # overdue rule
    rule_out_4 = Rule(id=6, name="Rule 6", type="out", category_id=cat_out_sub3.id, pattern="PATTERN6", regular=1, next_valuta=20, next_due=today - timedelta(days=6), description="Description - Rule 6 - Overdue")
    db.session.add(rule_out_4)

    db.session.commit()

    # Transactions

    trans_1 = Transaction(id=1,
                          full_text="BOOKING TEXT PATTERN1 #1",
                          valuta=1890.28,
                          date=start + timedelta(days=12),
                          description="Transaction 1",
                          rule_id=rule_in_1.id,
                          category_id=cat_in_main.id,
                          account_id=account.id)

    db.session.add(trans_1)

    trans_2 = Transaction(id=2,
                          full_text="BOOKING TEXT PATTERN1 #2",
                          valuta=1979.28,
                          date=start + timedelta(days=42),
                          description="Transaction 2",
                          rule_id=rule_in_1.id,
                          category_id=cat_in_main.id,
                          account_id=account.id)

    db.session.add(trans_2)


    trans_3 = Transaction(id=3,
                          full_text="BOOKING TEXT PATTERN3 #3",
                          valuta=-35.78,
                          date=start + timedelta(days=3),
                          description="Transaction 3",
                          rule_id=rule_out_1.id,
                          category_id=cat_out_sub1.id,
                          account_id=account.id)

    db.session.add(trans_3)

    trans_4 = Transaction(id=4,
                          full_text="BOOKING TEXT PATTERN3 #4",
                          valuta=-207.89,
                          date=start + timedelta(days=2),
                          description="Transaction 4",
                          rule_id=rule_out_2.id,
                          category_id=cat_out_sub1.id,
                          account_id=account.id)

    db.session.add(trans_4)

    trans_5 = Transaction(id=5,
                          full_text="BOOKING TEXT PATTERN3 #5",
                          valuta=-207.89,
                          date=start + timedelta(days=32),
                          description="Transaction 5",
                          rule_id=rule_out_2.id,
                          category_id=cat_out_sub1.id,
                          account_id=account.id)

    db.session.add(trans_5)

    trans_6 = Transaction(id=6,
                          full_text="MESSAGE TEXT #6",
                          valuta=0,
                          description="",
                          date=today - timedelta(days=2),
                          account_id=account.id)

    db.session.add(trans_6)


    db.session.commit()

    return db


#                                     _
#      /\                            | |
#     /  \   ___ ___ ___  _   _ _ __ | |_
#    / /\ \ / __/ __/ _ \| | | | '_ \| __|
#   / ____ \ (_| (_| (_) | |_| | | | | |
#  /_/    \_\___\___\___/ \__,_|_| |_|\__|
#


def test_account_oldest_transaction(db_filled):
    account = Account.query.filter_by(id=1).one()

    oldest_transaction = account.oldest_transaction

    assert oldest_transaction.id == 4


def test_account_latest_transaction(db_filled):
    account = Account.query.filter_by(id=1).one()

    latest_transaction = account.latest_transaction

    assert latest_transaction.id == 6


def test_account_iban_formatted(db_filled):
    account = Account.query.filter_by(id=1).one()

    iban = account.iban_formatted

    assert iban == 'DE67 1002 0030 1230 0023 45'


def test_account_last_update(db_filled):
    account = Account.query.filter_by(id=1).one()

    last_update = account.last_update
    latest_transaction = account.latest_transaction
    assert (latest_transaction.date - datetime.date.today()) == last_update


def test_account_categories_in(db_filled):
    account = Account.query.filter_by(id=1).one()

    categories = account.categories("in")

    result = Category.query.filter(Category.id.in_([1, 2])).all()

    assert categories == result


def test_account_categories_out(db_filled):
    account = Account.query.filter_by(id=1).one()

    categories = account.categories("out")

    # category 6 is a subcategory and therefore should not appear here
    result = Category.query.filter(Category.id.in_([3, 4, 5, 7])).all()

    assert categories == result


def test_account_categories_timeframe(db_filled):
    account = Account.query.filter_by(id=1).one()

    categories = account.categories("out")

    for category in categories:
        assert category.start is None
        assert category.end is None

    categories = account.categories("out", start, today)

    for category in categories:
        assert category.start == start
        assert category.end == today

        if category.childs is not None:

            for child in category.childs:
                assert child.start == start
                assert child.end == today


def test_account_rules_by_type_in(db_filled):
    account = Account.query.filter_by(id=1).one()

    rules = account.rules_by_type("in")
    result = Rule.query.filter(Rule.id.in_([1, 2])).all()

    assert rules == result


def test_account_rules_by_type_out(db_filled):
    account = Account.query.filter_by(id=1).one()

    rules = account.rules_by_type("out")
    result = Rule.query.filter(Rule.id.in_([3, 4, 5, 6])).all()

    assert rules == result


def test_account_nonmonthly_rules_in(db_filled):
    account = Account.query.filter_by(id=1).one()

    rules_in = account.non_regular_rules("in", today + timedelta(weeks=8), today + timedelta(weeks=12))

    assert rules_in == []


def test_account_nonmonthly_rules_out(db_filled):
    account = Account.query.filter_by(id=1).one()

    rules_out = account.non_regular_rules("out", today + timedelta(weeks=6), today + timedelta(weeks=23))

    assert len(rules_out) == 1
    assert isinstance(rules_out[0], tuple)
    assert len(rules_out[0]) == 2  # 2 elements in tuple
    assert isinstance(rules_out[0][0], Rule)
    assert rules_out[0][0].id == 3


def test_account_transactions(db_filled):
    account = Account.query.filter_by(id=1).one()

    transactions = account.transactions()

    assert len(transactions) == 6
    assert all(isinstance(el, Transaction) for el in transactions)

    transactions = account.transactions(start, start + timedelta(days=14))

    assert len(transactions) == 3
    assert all(isinstance(el, Transaction) for el in transactions)


def test_account_search_transactions(db_filled):
    account = Account.query.filter_by(id=1).one()

    result = account.search_for_transactions("PATTERN3")
    expected = Transaction.query.filter(Transaction.id.in_([3, 4, 5])).order_by(Transaction.date.desc()).all()

    assert result == expected

    result = account.search_for_transactions("NONEXISTINGPATTERN")

    assert result == []


def test_account_transactions_by_type_in(db_filled):
    account = Account.query.filter_by(id=1).one()

    result = account.transactions_by_type("in")
    expected = Transaction.query.filter(Transaction.id.in_([1, 2])).order_by(Transaction.date.asc()).all()

    assert result == expected


def test_account_transactions_by_type_out(db_filled):
    account = Account.query.filter_by(id=1).one()

    result = account.transactions_by_type("out")
    expected = Transaction.query.filter(Transaction.id.in_([3, 4, 5])).order_by(Transaction.date.asc()).all()

    assert result == expected


def test_account_transactions_by_type_message(db_filled):
    account = Account.query.filter_by(id=1).one()

    result = account.transactions_by_type("message")
    expected = Transaction.query.filter_by(id=6).order_by(Transaction.date.asc()).all()

    assert result == expected


def test_account_creation_primary_key(db):
    item = Account(name="test", balance=0, iban="DE71003002001232345678")
    assert item.id is None
    db.session.add(item)
    db.session.commit()
    assert item.id is not None


#     _____      _
#    / ____|    | |
#   | |     __ _| |_ ___  __ _  ___  _ __ _   _
#   | |    / _` | __/ _ \/ _` |/ _ \| '__| | | |
#   | |___| (_| | ||  __/ (_| | (_) | |  | |_| |
#    \_____\__,_|\__\___|\__, |\___/|_|   \__, |
#                         __/ |            __/ |
#                        |___/            |___/


def test_category_planned_transactions_none(db_filled):

    cat_1 = Category.query.filter_by(id=1).one()

    cat_1.setTimeframe(today, today + timedelta(weeks=5))

    planned_transactions = cat_1.planned_transactions

    assert planned_transactions == []




def test_category_planned_transactions_monthly(db_filled):

    cat_2 = Category.query.filter_by(id=2).one()

    cat_2.setTimeframe(today, today + timedelta(weeks=5))

    planned_transactions = cat_2.planned_transactions

    assert len(planned_transactions) == 1
    assert isinstance(planned_transactions[0], PlannedTransaction)
    assert planned_transactions[0].rule_id == 2


def test_category_planned_transactions_monthly_past_month_none(db_filled):

    cat_5 = Category.query.filter_by(id=5).one()

    cat_5.setTimeframe(start, start + timedelta(weeks=4))

    planned_transactions = cat_5.planned_transactions

    assert planned_transactions == []


def test_category_planned_transactions_quarterly(db_filled):

    cat_4 = Category.query.filter_by(id=4).one()

    cat_4.setTimeframe(today + timedelta(weeks=1), today + timedelta(weeks=10))

    planned_transactions = cat_4.planned_transactions

    assert len(planned_transactions) == 1
    assert isinstance(planned_transactions[0], PlannedTransaction)
    assert planned_transactions[0].rule_id == 3


def test_category_planned_transactions_only_in_future(db_filled):

    account = Account.query.filter_by(id=1).one()

    latest_transaction = account.latest_transaction

    cat_2 = Category.query.filter_by(id=2).one()

    cat_2.setTimeframe(start, today + timedelta(weeks=5))

    planned_transactions = cat_2.planned_transactions

    assert len(planned_transactions) > 0

    for planned_transaction in planned_transactions:
        assert planned_transaction.date >= latest_transaction.date


def test_category_has_regular_rules(db_filled):

    cat_1 = Category.query.filter_by(id=1).one()

    assert cat_1.has_regular_rules is False

    cat_2 = Category.query.filter_by(id=2).one()

    assert cat_2.has_regular_rules is True

    cat_3 = Category.query.filter_by(id=3).one()

    assert cat_3.has_regular_rules is False

    cat_4 = Category.query.filter_by(id=4).one()

    assert cat_4.has_regular_rules is True

    cat_5 = Category.query.filter_by(id=5).one()

    assert cat_5.has_regular_rules is True

    cat_6 = Category.query.filter_by(id=6).one()

    assert cat_6.has_regular_rules is False

    cat_7 = Category.query.filter_by(id=7).one()

    assert cat_7.has_regular_rules is True


def test_category_has_overdued_planned_transactions(db_filled):

    categories_no_overdue = Category.query.filter(Category.id.in_([1, 2, 3, 4, 5, 6])).all()

    assert len(categories_no_overdue) == 6

    for category in categories_no_overdue:
        category.setTimeframe(start, today)
        assert category.has_overdued_planned_transactions is False

    category_with_overdue = Category.query.filter_by(id=7).one()
    category_with_overdue.setTimeframe(start, today)

    assert category_with_overdue.has_overdued_planned_transactions is True


#   ____        __                       _   _             _     _    _                 _ _
#  |  _ \      / _|                 /\  | | | |           | |   | |  | |               | | |
#  | |_) | ___| |_ ___  _ __ ___   /  \ | |_| |_ __ _  ___| |__ | |__| | __ _ _ __   __| | | ___ _ __
#  |  _ < / _ \  _/ _ \| '__/ _ \ / /\ \| __| __/ _` |/ __| '_ \|  __  |/ _` | '_ \ / _` | |/ _ \ '__|
#  | |_) |  __/ || (_) | | |  __// ____ \ |_| || (_| | (__| | | | |  | | (_| | | | | (_| | |  __/ |
#  |____/ \___|_| \___/|_|  \___/_/    \_\__|\__\__,_|\___|_| |_|_|  |_|\__,_|_| |_|\__,_|_|\___|_|
#  ==================================================================================================


def test_before_attach_handler_account_balance(db_filled):
    account = Account.query.first()

    assert account.balance == 3418.0