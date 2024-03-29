from moneywatch.utils.functions import get_first_day_of_month, get_last_day_of_month
from moneywatch.utils.objects import Account, Category, Rule, Transaction, PlannedTransaction
from moneywatch.utils.exceptions import MultipleRuleMatchError
import pytest
import logging
import datetime




#   _____  ____ _______        _   _____        _
#  |  __ \|  _ \__   __|      | | |  __ \      | |
#  | |  | | |_) | | | ___  ___| |_| |  | | __ _| |_ __ _
#  | |  | |  _ <  | |/ _ \/ __| __| |  | |/ _` | __/ _` |
#  | |__| | |_) | | |  __/\__ \ |_| |__| | (_| | || (_| |
#  |_____/|____/  |_|\___||___/\__|_____/ \__,_|\__\__,_|
#  ======================================================
#




@pytest.fixture
def today(fixed_date):

    datetime.date.set_today(2020, 3, 20)  # type: ignore

    return datetime.date.today()


@pytest.fixture
def start(today):
    start = today - datetime.timedelta(weeks=8)
    start = datetime.date(year=start.year, month=start.month, day=1)
    return start


@pytest.fixture
def end():
    return datetime.date(2020, 3, 31)


@pytest.fixture
def db_only_account(db):

    # Account
    account = Account(id=1, name="Main Account", balance=0, iban="DE16500105171721253655")
    db.session.add(account)

    db.session.commit()

    return db



@pytest.fixture
def db_filled(db, today, start):

    # Accounts

    account = Account(id=1, name="Main Account", balance=0, iban="DE16500105171721253655")
    db.session.add(account)

    # Categories

    cat_in_main = Category(id=1, name="Main Category IN", type="in")
    db.session.add(cat_in_main)

    cat_in_sub1 = Category(id=2, name="Main Category SUB1", type="in", parent_id=cat_in_main.id)
    db.session.add(cat_in_sub1)

    cat_out_main = Category(id=3, name="Main Category OUT", type="out", parent_id=None)
    db.session.add(cat_out_main)

    cat_out_sub1 = Category(id=4, name="Main Category SUB1", type="out", parent_id=cat_out_main.id)
    db.session.add(cat_out_sub1)

    cat_out_sub2 = Category(id=5, name="Main Category SUB2", type="out", parent_id=cat_out_main.id)
    db.session.add(cat_out_sub2)

    cat_out_subsub1 = Category(id=6, name="Sub-Sub Category SUBSUB1", budget_monthly=200, type="out", parent_id=cat_out_sub2.id)
    db.session.add(cat_out_subsub1)

    cat_out_sub3 = Category(id=7, name="Main Category SUB3 with overdue", type="out", parent_id=cat_out_main.id)
    db.session.add(cat_out_sub3)

    # Rules

    # change the today date to get a differing "start" date
    datetime.date.set_today(2020, 3, 1)  # type: ignore

    rule_in_1 = Rule(id=1, name="Rule 1", type="in", category_id=cat_in_main.id, pattern="PATTERN1", description="Description - Rule 1")
    db.session.add(rule_in_1)

    datetime.date.set_today(2020, 3, 2)  # type: ignore

    rule_in_2 = Rule(id=2, name="Rule 2", type="in", category_id=cat_in_sub1.id, pattern="PATTERN2", regular=1, next_valuta=29.98, next_due=today + datetime.timedelta(days=15), description="Description - Rule 2")
    db.session.add(rule_in_2)

    datetime.date.set_today(2020, 3, 3)  # type: ignore

    rule_out_1 = Rule(id=3, name="Rule 3", type="out", category_id=cat_out_sub1.id, pattern="PATTERN3", regular=3, next_valuta=293.29, next_due=today + datetime.timedelta(days=3), description="Description - Rule 3")
    db.session.add(rule_out_1)

    datetime.date.set_today(2020, 3, 4)  # type: ignore

    rule_out_2 = Rule(id=4, name="Rule 4", type="out", category_id=cat_out_sub1.id, pattern=r"PATTERN4.*PATTERN4", description="Description - Rule 4")
    db.session.add(rule_out_2)

    datetime.date.set_today(2020, 3, 5)  # type: ignore

    rule_out_3 = Rule(id=5, name="Rule 5", type="out", category_id=cat_out_sub2.id, pattern="PATTERN5", regular=1, next_valuta=20, next_due=today + datetime.timedelta(days=2), description="Description - Rule 5")
    db.session.add(rule_out_3)

    datetime.date.set_today(2020, 3, 6)  # type: ignore

    # overdue rule
    rule_out_4 = Rule(id=6, name="Rule 6", type="out", category_id=cat_out_sub3.id, pattern="PATTERN6", regular=1, next_valuta=20, next_due=today - datetime.timedelta(days=6), description="Description - Rule 6 - Overdue")
    db.session.add(rule_out_4)

    db.session.commit()

    datetime.date.set_today_date(today)  # type: ignore

    # Transactions

    trans_1 = Transaction(id=1,
                          full_text="BOOKING TEXT PATTERN1 #1",
                          valuta=1890.28,
                          date=start + datetime.timedelta(days=12),
                          description="Transaction 1",
                          rule_id=rule_in_1.id,
                          category_id=cat_in_main.id,
                          account_id=account.id)

    db.session.add(trans_1)

    trans_2 = Transaction(id=2,
                          full_text="BOOKING TEXT PATTERN1 #2",
                          valuta=1979.28,
                          date=start + datetime.timedelta(days=42),
                          description="Transaction 2",
                          rule_id=rule_in_1.id,
                          category_id=cat_in_main.id,
                          account_id=account.id)

    db.session.add(trans_2)


    trans_3 = Transaction(id=3,
                          full_text="BOOKING TEXT PATTERN3 #3",
                          valuta=-35.78,
                          date=start + datetime.timedelta(days=2),
                          description="Transaction 3",
                          rule_id=rule_out_1.id,
                          category_id=cat_out_sub1.id,
                          account_id=account.id)

    db.session.add(trans_3)

    trans_4 = Transaction(id=4,
                          full_text="BOOKING TEXT PATTERN3 #4",
                          valuta=-207.89,
                          date=start + datetime.timedelta(days=3),
                          description="Transaction 4",
                          rule_id=rule_out_1.id,
                          category_id=cat_out_sub1.id,
                          account_id=account.id)

    db.session.add(trans_4)

    trans_5 = Transaction(id=5,
                          full_text="BOOKING TEXT PATTERN3 #5",
                          valuta=-207.89,
                          date=start + datetime.timedelta(days=32),
                          description="Transaction 5",
                          rule_id=rule_out_1.id,
                          category_id=cat_out_sub1.id,
                          account_id=account.id)

    db.session.add(trans_5)

    trans_6 = Transaction(id=6,
                          full_text="MESSAGE TEXT #6",
                          valuta=0,
                          description="",
                          date=today - datetime.timedelta(days=2),
                          account_id=account.id)

    db.session.add(trans_6)

    trans_7 = Transaction(id=7,
                          full_text="BOOKING TEXT PATTERN2 #1",
                          valuta=29.98,
                          date=start + datetime.timedelta(days=2),
                          description="Transaction 7",
                          rule_id=rule_in_2.id,
                          category_id=cat_in_sub1.id,
                          account_id=account.id)

    db.session.add(trans_7)

    trans_8 = Transaction(id=8,
                          full_text="BOOKING TEXT NO PATTERN #1",
                          valuta=40.45,
                          date=start + datetime.timedelta(days=19),
                          description="Transaction 8",
                          category_id=cat_in_sub1.id,
                          account_id=account.id)

    db.session.add(trans_8)

    trans_9 = Transaction(id=9,
                          full_text="BOOKING TEXT NO PATTERN #2",
                          valuta=40.45,
                          date=datetime.date(today.year, today.month, 2),
                          description="Transaction 8",
                          category_id=cat_in_sub1.id,
                          account_id=account.id)

    db.session.add(trans_9)

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

    assert oldest_transaction.id == 3


def test_account_latest_transaction(db_filled):
    account = Account.query.filter_by(id=1).one()

    latest_transaction = account.latest_transaction

    assert latest_transaction.id == 6


def test_account_iban_formatted(db_filled):
    account = Account.query.filter_by(id=1).one()

    iban = account.iban_formatted

    assert iban == 'DE16 5001 0517 1721 2536 55'


def test_account_last_update(db_filled):
    account = Account.query.filter_by(id=1).one()

    last_update = account.last_update
    latest_transaction = account.latest_transaction
    assert latest_transaction.date == last_update


def test_account_categories_in(db_filled):
    account = Account.query.filter_by(id=1).one()

    categories = account.categories("in")

    result = Category.query.filter(Category.id.in_([1])).all()

    assert categories == result


def test_account_categories_out(db_filled):
    account = Account.query.filter_by(id=1).one()

    categories = account.categories("out")

    result = Category.query.filter(Category.id.in_([3])).all()

    assert categories == result


def test_account_categories_timeframe(db_filled, today, start):
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


def test_account_nonmonthly_rules_in(db_filled, today):
    account = Account.query.filter_by(id=1).one()

    rules_in = account.non_regular_rules("in", today + datetime.timedelta(weeks=8), today + datetime.timedelta(weeks=12))

    assert rules_in == []


def test_account_nonmonthly_rules_out(db_filled, today):
    account = Account.query.filter_by(id=1).one()

    rules_out = account.non_regular_rules("out", today + datetime.timedelta(weeks=6), today + datetime.timedelta(weeks=23))

    assert len(rules_out) == 1
    assert isinstance(rules_out[0], tuple)
    assert len(rules_out[0]) == 2  # 2 elements in tuple
    assert isinstance(rules_out[0][0], Rule)
    assert rules_out[0][0].id == 3


def test_account_transactions(db_filled, start, today):
    account = Account.query.filter_by(id=1).one()

    transactions = account.transactions()

    assert len(transactions) == 9
    assert all(isinstance(el, Transaction) for el in transactions)

    transactions = account.transactions(start, start + datetime.timedelta(days=14))

    assert len(transactions) == 4
    assert all(isinstance(el, Transaction) for el in transactions)

    transactions = account.transactions(start + datetime.timedelta(days=20))

    assert len(transactions) > 0
    assert all(isinstance(el, Transaction) for el in transactions)
    assert transactions[0].id == 5
    assert transactions[-1].id == 6

    transactions = account.transactions(None, today - datetime.timedelta(days=20))

    assert len(transactions) > 0
    assert all(isinstance(el, Transaction) for el in transactions)
    assert transactions[0].id == 3
    assert transactions[-1].id == 2


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
    expected = Transaction.query.filter(Transaction.id.in_([1, 2, 7, 8, 9])).order_by(Transaction.date.asc()).all()

    assert result == expected


def test_account_transactions_by_type_out(db_filled, start, today):
    account = Account.query.filter_by(id=1).one()

    result = account.transactions_by_type("out")
    expected = Transaction.query.filter(Transaction.id.in_([3, 4, 5])).order_by(Transaction.date.asc()).all()

    assert result == expected

    transactions = account.transactions_by_type("out", start + datetime.timedelta(days=20))

    assert len(transactions) == 1
    assert all(isinstance(el, Transaction) for el in transactions)
    assert transactions[0].id == 5

    transactions = account.transactions_by_type("out", None, today - datetime.timedelta(days=20))

    assert len(transactions) > 0
    assert all(isinstance(el, Transaction) for el in transactions)
    assert transactions[0].id == 3
    assert transactions[-1].id == 5

    transactions = account.transactions_by_type("out", start + datetime.timedelta(days=15), today - datetime.timedelta(days=20))

    assert len(transactions) == 1
    assert all(isinstance(el, Transaction) for el in transactions)
    assert transactions[0].id == 5


def test_account_transactions_by_type_message(db_filled):
    account = Account.query.filter_by(id=1).one()

    result = account.transactions_by_type("message")
    expected = Transaction.query.filter_by(id=6).order_by(Transaction.date.asc()).all()

    assert result == expected


def test_account_creation_primary_key(db):
    item = Account(name="test", balance=0, iban="DE16500105171721253655")
    assert item.id is None
    db.session.add(item)
    db.session.commit()
    assert item.id is not None


def test_account_empty(db):
    item = Account(name="test", balance=0, iban="DE16500105171721253655")

    assert item.latest_transaction is None
    assert item.oldest_transaction is None
    assert item.last_update is None


def test_account_duplicate_iban(db):
    from sqlalchemy.exc import IntegrityError


    item1 = Account(name="test", balance=0, iban="DE16500105171721253655")
    db.session.add(item1)
    db.session.commit()

    item2 = Account(name="test2", balance=0, iban="DE16500105171721253655")
    db.session.add(item2)

    with pytest.raises(IntegrityError):
        db.session.commit()



def test_account_duplicate_name(db):
    from sqlalchemy.exc import IntegrityError

    item1 = Account(name="test", balance=0, iban="DE16500105171721253655")
    db.session.add(item1)
    db.session.commit()

    item2 = Account(name="test", balance=0, iban="DE35500105177714537799")
    db.session.add(item2)

    with pytest.raises(IntegrityError):
        db.session.commit()


#     _____      _
#    / ____|    | |
#   | |     __ _| |_ ___  __ _  ___  _ __ _   _
#   | |    / _` | __/ _ \/ _` |/ _ \| '__| | | |
#   | |___| (_| | ||  __/ (_| | (_) | |  | |_| |
#    \_____\__,_|\__\___|\__, |\___/|_|   \__, |
#                         __/ |            __/ |
#                        |___/            |___/


def test_category_planned_transactions_none(db_filled, today):

    cat_1 = Category.query.filter_by(id=1).one()

    cat_1.setTimeframe(today, today + datetime.timedelta(weeks=5))

    planned_transactions = cat_1.planned_transactions

    assert planned_transactions == []




def test_category_planned_transactions_monthly(db_filled, today):

    cat_2 = Category.query.filter_by(id=2).one()

    cat_2.setTimeframe(today, today + datetime.timedelta(weeks=5))

    planned_transactions = cat_2.planned_transactions

    assert len(planned_transactions) == 1
    assert isinstance(planned_transactions[0], PlannedTransaction)
    assert planned_transactions[0].rule_id == 2


def test_category_planned_transactions_monthly_past_month_none(db_filled, start):

    cat_5 = Category.query.filter_by(id=5).one()

    cat_5.setTimeframe(start, start + datetime.timedelta(weeks=4))

    planned_transactions = cat_5.planned_transactions

    assert planned_transactions == []


def test_category_planned_transactions_monthly_without_existing(db_filled, start, today):

    cat_2 = Category.query.filter_by(id=2).one()

    cat_2.setTimeframe(start, today + datetime.timedelta(weeks=3))

    planned_transactions = cat_2.planned_transactions
    transactions = cat_2.transactions
    assert len(planned_transactions) == 1
    assert planned_transactions[0].date == datetime.date(2020, 4, 4)
    assert planned_transactions[0].valuta == 29.98
    assert len(transactions) == 3
    assert transactions[0].id == 7
    assert transactions[1].id == 8
    assert transactions[2].id == 9


def test_category_planned_transactions_quarterly(db_filled, today):

    cat_4 = Category.query.filter_by(id=4).one()

    cat_4.setTimeframe(datetime.date(2020, 4, 1), datetime.date(2020, 6, 30))

    planned_transactions = cat_4.planned_transactions

    assert len(planned_transactions) == 1
    assert isinstance(planned_transactions[0], PlannedTransaction)
    assert planned_transactions[0].rule_id == 3


def test_category_planned_transactions_only_in_future(db_filled, today, start):

    account = Account.query.filter_by(id=1).one()

    latest_transaction = account.latest_transaction

    cat_2 = Category.query.filter_by(id=2).one()

    cat_2.setTimeframe(start, today + datetime.timedelta(weeks=5))

    planned_transactions = cat_2.planned_transactions

    assert len(planned_transactions) > 0

    for planned_transaction in planned_transactions:
        assert planned_transaction.date >= latest_transaction.date


def test_category_planned_transactions_overdue(db_only_account, fixed_date):

    db = db_only_account
    datetime.date.set_today(2020, 1, 1)  # type: ignore

    cat = Category(id=1, name="Main Category", account_id=1, type="in", parent_id=None)

    rule = Rule(id=1,
                account_id=1,
                name="Rule In",
                type="in",
                category=cat,
                pattern="PATTERN",
                regular=1,
                next_valuta=10,
                next_due=datetime.date(2020, 1, 1),
                description="Description - Rule 1")

    trans_1 = Transaction(id=1,
                          full_text="TEST TRANSACTION #1",
                          valuta=20,
                          date=datetime.date(2020, 1, 1),
                          description="Transaction 1",
                          category=cat,
                          account_id=1)

    db.session.add_all([cat, rule])
    db.session.commit()

    cat.setTimeframe(get_first_day_of_month(), get_last_day_of_month())

    assert len(cat.planned_transactions) == 1
    assert cat.planned_transactions[0].rule_id == rule.id
    assert cat.planned_transactions[0].valuta == rule.next_valuta
    assert cat.planned_transactions[0].date == rule.next_due
    assert cat.planned_transactions[0].overdue is False


    def insert_transaction(transaction, expected_overdue):

        db.session.add(transaction)
        db.session.commit()

        datetime.date.set_today_date(datetime.date.today() + datetime.timedelta(days=1))  # type: ignore

        cat._cache = {}

        assert len(cat.planned_transactions) == 1
        assert cat.planned_transactions[0].rule_id == rule.id
        assert cat.planned_transactions[0].valuta == rule.next_valuta
        assert cat.planned_transactions[0].date == rule.next_due
        assert cat.planned_transactions[0].overdue is expected_overdue

    insert_transaction(trans_1, False)  # day 1 - 2020-01-01

    trans_2 = Transaction(id=2,
                          account_id=1,
                          full_text="TEST TRANSACTION #2",
                          valuta=20,
                          date=datetime.date(2020, 1, 2),
                          description="Transaction 2",
                          category_id=cat.id
                          )

    insert_transaction(trans_2, False)  # day 2 - 2020-01-02

    trans_3 = Transaction(id=3,
                          account_id=1,
                          full_text="TEST TRANSACTION #3",
                          valuta=20,
                          date=datetime.date(2020, 1, 3),
                          description="Transaction 3",
                          category_id=cat.id
                          )

    insert_transaction(trans_3, False)  # day 3 - 2020-01-03

    trans_4 = Transaction(id=4,
                          account_id=1,
                          full_text="TEST TRANSACTION #4",
                          valuta=20,
                          date=datetime.date(2020, 1, 4),
                          description="Transaction 4",
                          category_id=cat.id
                          )

    insert_transaction(trans_4, True)   # day 4 - 2020-01-04


def test_category_regular_rules_done(db_only_account, today):

    datetime.date.set_today(2020, 1, 15)  # type: ignore
    db = db_only_account

    cat = Category(id=1, name="Main Category", account_id=1, type="in", parent_id=None)

    rule = Rule(id=1, account_id=1, name="Rule Sub", type="in", category_id=cat.id, pattern="PATTERN2", regular=1, next_valuta=10, next_due=datetime.date(2020, 1, 20), description="Description - Rule 2")

    trans_1 = Transaction(id=1,
                          full_text="BOOKING TEXT PATTERN",
                          valuta=20,
                          date=datetime.date(2020, 1, 10),
                          description="Transaction 1",
                          category_id=cat.id,
                          account_id=1)


    db.session.add_all([cat, rule, trans_1])
    db.session.commit()

    cat.setTimeframe(datetime.date(2020, 1, 1), datetime.date(2020, 1, 31))

    # Category has one planned transaction by Rule #1 => False
    assert cat.regular_rules_done is False

    cat._cache = {}

    trans_2 = Transaction(id=2,
                          full_text="BOOKING TEXT PATTERN2",
                          valuta=20,
                          date=datetime.date(2020, 1, 12),
                          account_id=1)

    trans_2.check_rule_matching()

    db.session.add(trans_2)
    db.session.commit()

    # Category has one booked transaction by Rule #1, no other planned transactions => True
    assert cat.regular_rules_done is True


    cat._cache = {}

    rule2 = Rule(id=2, account_id=1, name="Rule Sub 2", type="in", category_id=cat.id, pattern="PATTERN3", regular=1, next_valuta=10, next_due=datetime.date(2020, 1, 14), description="Description - Rule 2")

    db.session.add(rule2)
    db.session.commit()

    # Category has one booked transaction by Rule #1, and one planned transaction by Rule #2 => False
    assert cat.regular_rules_done is False


def test_category_has_overdued_planned_transactions(db_filled, start, today):

    categories_no_overdue = Category.query.filter(Category.id.in_([1, 2, 4, 5, 6])).all()

    assert len(categories_no_overdue) == 5

    for category in categories_no_overdue:
        category.setTimeframe(start, today)
        assert category.has_overdued_planned_transactions is False

    categories_with_overdue = Category.query.filter(Category.id.in_([3, 7])).all()

    for category in categories_with_overdue:
        category.setTimeframe(start, today)

        assert category.has_overdued_planned_transactions is True



def test_category_budget(db_filled):
    cat_1 = Category.query.filter_by(id=1).one()

    assert cat_1.budget is None

    cat_2 = Category.query.filter_by(id=2).one()

    assert cat_2.budget is None

    cat_3 = Category.query.filter_by(id=3).one()

    assert cat_3.budget is None

    cat_4 = Category.query.filter_by(id=4).one()

    assert cat_4.budget is None

    cat_5 = Category.query.filter_by(id=5).one()

    assert cat_5.budget is None

    cat_6 = Category.query.filter_by(id=6).one()

    assert cat_6.budget == -200

    cat_7 = Category.query.filter_by(id=7).one()

    assert cat_7.budget is None


def test_category_transactions_with_childs(db_filled, start, end):

    # Main Category In
    cat_1 = Category.query.filter_by(id=1).one()
    cat_1.setTimeframe(start, end)
    transactions_in = Transaction.query.filter(Transaction.id.in_([1, 2, 7, 8, 9])).all()
    assert set(cat_1.transactions_with_childs) == set(transactions_in)

    # Main Category Out
    cat_3 = Category.query.filter_by(id=3).one()
    cat_3.setTimeframe(start, end)
    transactions_out = Transaction.query.filter(Transaction.id.in_([3, 4, 5])).all()

    # resulting list is not ordered => compare as set
    assert set(cat_3.transactions_with_childs) == set(transactions_out)


def test_category_transactions_combined(db_filled, start, end):

    # Main Category In
    cat_1 = Category.query.filter_by(id=1).one()
    cat_1.setTimeframe(start, end)
    transactions_in = Transaction.query.filter(Transaction.id.in_([1, 2])).all()
    assert cat_1.transactions_combined == transactions_in

    # Sub Category In
    cat_2 = Category.query.filter_by(id=2).one()
    cat_2.setTimeframe(start, end)
    transactions_in = Transaction.query.filter(Transaction.id.in_([7, 8, 9])).all()
    assert cat_2.transactions_combined == transactions_in


    # Main Category Out
    cat_3 = Category.query.filter_by(id=3).one()
    cat_3.setTimeframe(start, end)
    assert cat_3.transactions_combined == []

    # Sub #1  Category Out
    cat_4 = Category.query.filter_by(id=4).one()
    cat_4.setTimeframe(start, end)
    transactions_out = Transaction.query.filter(Transaction.id.in_([3, 4, 5])).order_by(Transaction.date.asc()).all()
    transactions_out.append(PlannedTransaction(date=datetime.date(2020, 3, 23),
                                               valuta=-293.29,
                                               description="Description - Rule 3",
                                               rule_id=3,
                                               overdue=False)
                            )
    assert cat_4.transactions_combined == transactions_out

    # Sub #2 Category Out
    cat_5 = Category.query.filter_by(id=5).one()
    cat_5.setTimeframe(start, end)
    transactions_out = []
    transactions_out.append(PlannedTransaction(date=datetime.date(2020, 3, 22),
                                               valuta=-20.0,
                                               description="Description - Rule 5",
                                               rule_id=5,
                                               overdue=False)
                            )
    assert cat_5.transactions_combined == transactions_out

    # Sub #2 Sub Category Out
    cat_6 = Category.query.filter_by(id=6).one()
    cat_6.setTimeframe(start, end)
    assert cat_6.transactions_combined == []

    # Sub #3 Category Out with overdued planned transaction
    cat_7 = Category.query.filter_by(id=7).one()
    cat_7.setTimeframe(start, end)
    transactions_out = []
    transactions_out.append(PlannedTransaction(date=datetime.date(2020, 3, 14),
                                               valuta=-20.0,
                                               description="Description - Rule 6 - Overdue",
                                               rule_id=6,
                                               overdue=True)
                            )
    assert cat_7.transactions_combined == transactions_out


def test_category_getCategoryPath(db_filled):

    cat_1 = Category.query.filter_by(id=1).one()
    assert cat_1.getCategoryPath(" > ") == "Main Category IN"

    cat_2 = Category.query.filter_by(id=2).one()
    assert cat_2.getCategoryPath(" > ") == "Main Category IN > Main Category SUB1"

    cat_3 = Category.query.filter_by(id=3).one()
    assert cat_3.getCategoryPath(" > ") == "Main Category OUT"

    cat_4 = Category.query.filter_by(id=4).one()
    assert cat_4.getCategoryPath(" > ") == "Main Category OUT > Main Category SUB1"

    cat_5 = Category.query.filter_by(id=5).one()
    assert cat_5.getCategoryPath(" > ") == "Main Category OUT > Main Category SUB2"

    cat_6 = Category.query.filter_by(id=6).one()
    assert cat_6.getCategoryPath(" > ") == "Main Category OUT > Main Category SUB2 > Sub-Sub Category SUBSUB1"

    cat_7 = Category.query.filter_by(id=7).one()
    assert cat_7.getCategoryPath(" > ") == "Main Category OUT > Main Category SUB3 with overdue"


def test_category_getCategoryIdsAndPaths(db_filled):

    cat_1 = Category.query.filter_by(id=1).one()
    result = [
        {'id': 1, 'path': 'Main Category IN'},
        {'id': 2, 'path': 'Main Category IN > Main Category SUB1'},
    ]
    assert cat_1.getCategoryIdsAndPaths(" > ") == result

    cat_2 = Category.query.filter_by(id=2).one()
    result = [
        {'id': 2, 'path': 'Main Category IN > Main Category SUB1'},
    ]
    assert cat_2.getCategoryIdsAndPaths(" > ") == result


    cat_3 = Category.query.filter_by(id=3).one()
    result = [
        {'id': 3, 'path': 'Main Category OUT'},
        {'id': 4, 'path': 'Main Category OUT > Main Category SUB1'},
        {'id': 5, 'path': 'Main Category OUT > Main Category SUB2'},
        {'id': 6, 'path': 'Main Category OUT > Main Category SUB2 > Sub-Sub Category SUBSUB1'},
        {'id': 7, 'path': 'Main Category OUT > Main Category SUB3 with overdue'},
    ]
    assert cat_3.getCategoryIdsAndPaths(" > ") == result

    cat_4 = Category.query.filter_by(id=4).one()
    result = [
        {'id': 4, 'path': 'Main Category OUT > Main Category SUB1'},
    ]
    assert cat_4.getCategoryIdsAndPaths(" > ") == result

    cat_5 = Category.query.filter_by(id=5).one()
    result = [
        {'id': 5, 'path': 'Main Category OUT > Main Category SUB2'},
        {'id': 6, 'path': 'Main Category OUT > Main Category SUB2 > Sub-Sub Category SUBSUB1'},
    ]
    assert cat_5.getCategoryIdsAndPaths(" > ") == result

    cat_6 = Category.query.filter_by(id=6).one()
    result = [
        {'id': 6, 'path': 'Main Category OUT > Main Category SUB2 > Sub-Sub Category SUBSUB1'},
    ]
    assert cat_6.getCategoryIdsAndPaths(" > ") == result

    cat_7 = Category.query.filter_by(id=7).one()
    result = [
        {'id': 7, 'path': 'Main Category OUT > Main Category SUB3 with overdue'},
    ]
    assert cat_7.getCategoryIdsAndPaths(" > ") == result


def test_category_valuta(db_filled, start, end):

    cat_1 = Category.query.filter_by(id=1).one()
    cat_1.setTimeframe(start, end)
    assert cat_1.valuta == 3980.44

    cat_2 = Category.query.filter_by(id=2).one()
    cat_2.setTimeframe(start, end)
    assert cat_2.valuta == 110.88

    cat_3 = Category.query.filter_by(id=3).one()
    cat_3.setTimeframe(start, end)
    assert cat_3.valuta == -451.56

    cat_4 = Category.query.filter_by(id=4).one()
    cat_4.setTimeframe(start, end)
    assert cat_4.valuta == -451.56

    cat_5 = Category.query.filter_by(id=5).one()
    cat_5.setTimeframe(start, end)
    assert cat_5.valuta == 0.0

    cat_6 = Category.query.filter_by(id=6).one()
    cat_6.setTimeframe(start, end)
    assert cat_6.valuta == 0.0

    cat_7 = Category.query.filter_by(id=7).one()
    cat_7.setTimeframe(start, end)
    assert cat_7.valuta == 0.0


def test_category_planned_transactions_valuta(db_filled, start, end):

    cat_1 = Category.query.filter_by(id=1).one()
    cat_1.setTimeframe(start, end)
    assert cat_1.planned_transactions_valuta == 0.0

    cat_2 = Category.query.filter_by(id=2).one()
    cat_2.setTimeframe(start, end)
    assert cat_2.planned_transactions_valuta == 0.0

    cat_3 = Category.query.filter_by(id=3).one()
    cat_3.setTimeframe(start, end)
    assert cat_3.planned_transactions_valuta == -333.29

    cat_4 = Category.query.filter_by(id=4).one()
    cat_4.setTimeframe(start, end)
    assert cat_4.planned_transactions_valuta == -293.29

    cat_5 = Category.query.filter_by(id=5).one()
    cat_5.setTimeframe(start, end)
    assert cat_5.planned_transactions_valuta == -20.0

    cat_6 = Category.query.filter_by(id=6).one()
    cat_6.setTimeframe(start, end)
    assert cat_6.planned_transactions_valuta == 0.0

    cat_7 = Category.query.filter_by(id=7).one()
    cat_7.setTimeframe(start, end)
    assert cat_7.planned_transactions_valuta == -20.0


def test_category_planned_valuta(db_filled, start, end):

    cat_1 = Category.query.filter_by(id=1).one()
    cat_1.setTimeframe(start, end)
    assert cat_1.planned_valuta == 3980.44

    cat_2 = Category.query.filter_by(id=2).one()
    cat_2.setTimeframe(start, end)
    assert cat_2.planned_valuta == 110.88

    cat_3 = Category.query.filter_by(id=3).one()
    cat_3.setTimeframe(start, end)
    assert cat_3.planned_valuta == -1384.85

    cat_4 = Category.query.filter_by(id=4).one()
    cat_4.setTimeframe(start, end)
    assert cat_4.planned_valuta == -744.85

    cat_5 = Category.query.filter_by(id=5).one()
    cat_5.setTimeframe(start, end)
    assert cat_5.planned_valuta == -620.0

    cat_6 = Category.query.filter_by(id=6).one()
    cat_6.setTimeframe(start, end)
    assert cat_6.planned_valuta == -600.0

    cat_7 = Category.query.filter_by(id=7).one()
    cat_7.setTimeframe(start, end)
    assert cat_7.planned_valuta == -20.0


def test_category_has_sibling_name(db_filled):

    cat_1 = Category.query.filter_by(id=1).one()
    assert cat_1.has_sibling_name("New Category") is False
    assert cat_1.has_sibling_name("Main Category IN") is True

    cat_2 = Category.query.filter_by(id=2).one()
    assert cat_2.has_sibling_name("New Category") is False
    assert cat_2.has_sibling_name("Main Category SUB1") is True


#    _____       _
#   |  __ \     | |
#   | |__) |   _| | ___
#   |  _  / | | | |/ _ \
#   | | \ \ |_| | |  __/
#   |_|  \_\__,_|_|\___|
#
#

def test_rule_transactions(db_filled, start, end, today):
    rule_1 = Rule.query.filter_by(id=1).one()
    transactions_result = Transaction.query.filter(Transaction.id.in_([1, 2])).order_by(Transaction.date.asc()).all()
    assert rule_1.transactions() == transactions_result
    assert rule_1.transactions(start) == transactions_result
    assert rule_1.transactions(None, end) == transactions_result
    assert rule_1.transactions(start, end) == transactions_result
    assert rule_1.transactions(today, end) == []

    rule_2 = Rule.query.filter_by(id=2).one()
    transactions_result = Transaction.query.filter(Transaction.id.in_([7])).order_by(Transaction.date.asc()).all()
    assert rule_2.transactions() == transactions_result
    assert rule_2.transactions(start) == transactions_result
    assert rule_2.transactions(None, end) == transactions_result
    assert rule_2.transactions(start, end) == transactions_result
    assert rule_2.transactions(today, end) == []

    rule_3 = Rule.query.filter_by(id=3).one()
    transactions_result = Transaction.query.filter(Transaction.id.in_([3, 4, 5])).order_by(Transaction.date.asc()).all()
    assert rule_3.transactions() == transactions_result
    assert rule_3.transactions(start) == transactions_result
    assert rule_3.transactions(None, end) == transactions_result
    assert rule_3.transactions(start, end) == transactions_result
    assert rule_3.transactions(today, end) == []

    rule_4 = Rule.query.filter_by(id=4).one()
    transactions_result = []
    assert rule_4.transactions() == transactions_result
    assert rule_4.transactions(start, end) == transactions_result
    assert rule_4.transactions(None, end) == transactions_result
    assert rule_4.transactions(start, end) == transactions_result
    assert rule_4.transactions(today, end) == []

    rule_5 = Rule.query.filter_by(id=5).one()
    transactions_result = []
    assert rule_5.transactions() == transactions_result
    assert rule_5.transactions(start, end) == transactions_result
    assert rule_5.transactions(None, end) == transactions_result
    assert rule_5.transactions(start, end) == transactions_result
    assert rule_5.transactions(today, end) == []

    rule_6 = Rule.query.filter_by(id=6).one()
    transactions_result = []
    assert rule_6.transactions() == transactions_result
    assert rule_6.transactions(start, end) == transactions_result
    assert rule_6.transactions(None, end) == transactions_result
    assert rule_6.transactions(start, end) == transactions_result
    assert rule_6.transactions(today, end) == []


def test_rule_latest_transaction(db_filled):

    rule_3 = Rule.query.filter_by(id=3).one()

    transactions_result = Transaction.query.filter_by(id=5).one()
    assert rule_3.latest_transaction() == transactions_result

    transactions_result = Transaction.query.filter_by(id=4).one()
    assert rule_3.latest_transaction(5) == transactions_result

    transactions_result = Transaction.query.filter_by(id=3).one()
    assert rule_3.latest_transaction(4) == transactions_result


def test_rule_oldest_transaction(db_filled):

    rule_1 = Rule.query.filter_by(id=1).one()
    transactions_result = Transaction.query.filter_by(id=1).one()
    assert rule_1.oldest_transaction == transactions_result

    rule_2 = Rule.query.filter_by(id=2).one()
    transactions_result = Transaction.query.filter_by(id=7).one()
    assert rule_2.oldest_transaction == transactions_result

    rule_3 = Rule.query.filter_by(id=3).one()
    transactions_result = Transaction.query.filter_by(id=3).one()
    assert rule_3.oldest_transaction == transactions_result

    rule_4 = Rule.query.filter_by(id=4).one()
    assert rule_4.oldest_transaction is None

    rule_5 = Rule.query.filter_by(id=5).one()
    assert rule_5.oldest_transaction is None

    rule_6 = Rule.query.filter_by(id=6).one()
    assert rule_6.oldest_transaction is None


def test_rule_update_next_due(db_filled, today):

    # Rule 1 (non regular)
    rule_1 = Rule.query.filter_by(id=1).one()

    assert rule_1.regular is None
    assert rule_1.next_due is None
    assert rule_1.next_valuta is None

    rule_1.update_next_due(today, 100.0)

    assert rule_1.regular is None
    assert rule_1.next_due is None
    assert rule_1.next_valuta is None

    # Rule 2 (monthly) but it is already updated to 2020-04-04, so it should not update
    rule_2 = Rule.query.filter_by(id=2).one()

    assert rule_2.regular == 1
    assert rule_2.next_due == datetime.date(2020, 4, 4)
    assert rule_2.next_valuta == 29.98

    rule_2.update_next_due(today, 100.0)

    assert rule_2.regular == 1
    assert rule_2.next_due == datetime.date(2020, 4, 4)
    assert rule_2.next_valuta == 29.98

    # Rule 3 (quarterly)
    rule_3 = Rule.query.filter_by(id=3).one()

    assert rule_3.regular == 3
    assert rule_3.next_due == datetime.date(2020, 3, 23)
    assert rule_3.next_valuta == 293.29

    rule_3.update_next_due(today, 100.0)

    assert rule_3.regular == 3
    assert rule_3.next_due == datetime.date(2020, 6, 20)
    assert rule_3.next_valuta == 100.0

    # Rule 4 (non regular)
    rule_4 = Rule.query.filter_by(id=4).one()

    assert rule_4.regular is None
    assert rule_4.next_due is None
    assert rule_4.next_valuta is None

    rule_4.update_next_due(today, 100.0)

    assert rule_4.regular is None
    assert rule_4.next_due is None
    assert rule_4.next_valuta is None

    # Rule 5 (monthly)
    rule_5 = Rule.query.filter_by(id=5).one()

    assert rule_5.regular == 1
    assert rule_5.next_due == datetime.date(2020, 3, 22)
    assert rule_5.next_valuta == 20.0

    rule_5.update_next_due(today, 100.0)

    assert rule_5.regular == 1
    assert rule_5.next_due == datetime.date(2020, 4, 20)
    assert rule_5.next_valuta == 100.0

    # Rule 6 (monthly / overdued)
    rule_6 = Rule.query.filter_by(id=6).one()

    assert rule_6.regular == 1
    assert rule_6.next_due == datetime.date(2020, 3, 14)
    assert rule_6.next_valuta == 20.0

    rule_6.update_next_due(today, 100.0)

    assert rule_6.regular == 1
    assert rule_6.next_due == datetime.date(2020, 4, 20)
    assert rule_6.next_valuta == 100.0

    # update to a date that is older than current next due => no update should be performed
    rule_6.update_next_due(today - datetime.timedelta(days=2), 90.0)

    assert rule_6.regular == 1
    assert rule_6.next_due == datetime.date(2020, 4, 20)
    assert rule_6.next_valuta == 100.0


def test_rule_assign_transaction_ids(db_filled):
    db = db_filled

    trans_7 = Transaction.query.filter_by(id=7).one()  # should NOT be updated
    trans_8 = Transaction.query.filter_by(id=8).one()  # should be updated

    rule_2 = Rule.query.filter_by(id=2).one()

    category_1 = Category.query.filter_by(id=1).one()
    category_2 = Category.query.filter_by(id=2).one()


    assert trans_7.rule_id == 2
    assert trans_8.rule_id is None

    rule_7 = Rule(id=7, account_id=1, name="Rule 7", type="in", category_id=1, pattern="NO PATTERN", description="Description - Rule 7")
    db.session.add(rule_7)
    db.session.commit()

    assert trans_7.rule_id == 2
    assert trans_7.rule is rule_2
    assert trans_7.category_id == 2
    assert trans_7.category == category_2

    assert trans_8.rule_id is None
    assert trans_8.rule is None
    assert trans_8.category_id == 2
    assert trans_8.category == category_2

    rule_7.assign_transaction_ids([7, 8])

    assert trans_7.rule_id == 2
    assert trans_7.rule is rule_2
    assert trans_7.category_id == 2
    assert trans_7.category == category_2

    assert trans_8.rule is rule_7
    assert trans_8.rule_id is None
    assert trans_8.category_id == 2
    assert trans_8.category == category_1

    # rule_id update takes place after commit
    db.session.commit()

    assert trans_7.rule_id == 2
    assert trans_7.rule is rule_2
    assert trans_7.category_id == 2
    assert trans_7.category == category_2

    assert trans_8.rule is rule_7
    assert trans_8.rule_id == 7
    assert trans_8.category_id == 1
    assert trans_8.category == category_1


@pytest.mark.parametrize("pattern,result", [
    ("PATTERN", True),
    ("PATTERN$", True),
    ("Text", True),
    ("TEXT", True),
    ("TEST", True),
    (".*TEST", True),
    ("BOOKING", True),
    ("^BOOKING", True),
    ("^TEXT", False),
    ("TEXT 12345", True),
    ("TEXT.*TEST PATTERN", True),
])
def test_rule_match_transaction(db_filled, today, pattern, result):

    trans = Transaction(id=10,
                        full_text="BOOKING TEXT  12345//TEST PATTERN",
                        valuta=-100,
                        date=today,
                        description="Transaction 1",
                        account_id=1)

    rule = Rule(id=7, account_id=1, name="Rule 7", type="in", category_id=2, pattern=pattern, description="Description - Rule 7")

    # missmatch of type (in/out)
    assert rule.match_transaction(trans) is False

    # correct type (out)
    trans.valuta = 100.0
    assert rule.match_transaction(trans) == result


def test_rule_has_assigned_transactions(db_filled):

    rule_7 = Rule(id=7, account_id=1, name="Rule 7", type="in", category_id=2, pattern="NO PATTERN", description="Description - Rule 7")

    assert rule_7.has_assigned_transactions is False

    rule_1 = Rule.query.filter_by(id=1).one()
    rule_2 = Rule.query.filter_by(id=2).one()

    assert rule_1.has_assigned_transactions is True
    assert rule_2.has_assigned_transactions is True


def test_rule_start_date_is_today(db_filled, today):

    rule_7 = Rule(id=7, account_id=1, name="Rule 7", type="in", category_id=2, pattern="NO PATTERN", description="Description - Rule 7")

    assert rule_7.start == today

    rule_1 = Rule.query.filter_by(id=1).one()
    assert rule_1.start == datetime.date(2020, 3, 1)


def test_rule_active(db_filled):

    db = db_filled

    rule_1 = Rule.query.filter_by(id=1).one()

    assert rule_1.end is None
    assert rule_1.active is True

    rule_1.end = datetime.date.today()

    db.session.commit()

    assert rule_1.active is False

    rule_result = Rule.query.filter_by(active=False).one()
    assert rule_result == rule_1

    rule_2 = Rule.query.filter_by(id=2).one()
    assert rule_2.active is True


#    _______                             _   _
#   |__   __|                           | | (_)
#      | |_ __ __ _ _ __  ___  __ _  ___| |_ _  ___  _ __
#      | | '__/ _` | '_ \/ __|/ _` |/ __| __| |/ _ \| '_ \
#      | | | | (_| | | | \__ \ (_| | (__| |_| | (_) | | | |
#      |_|_|  \__,_|_| |_|___/\__,_|\___|\__|_|\___/|_| |_|
#
#

@pytest.mark.parametrize("trans_type,ids", [
    ("in", [1, 2, 7, 8, 9]),
    ("out", [3, 4, 5]),
    ("message", [6]),
])
def test_transaction_type(db_filled, trans_type, ids):

    transactions = Transaction.query.filter_by(type=trans_type).all()
    expected = Transaction.query.filter(Transaction.id.in_(ids)).all()

    assert set(transactions) == set(expected)

    for transaction in transactions:
        assert transaction.type == trans_type

    transactions = Transaction.query.filter(Transaction.type == trans_type).all()

    assert set(transactions) == set(expected)

    for transaction in transactions:
        assert transaction.type == trans_type


def test_transaction_complete(db_filled):

    trans = Transaction(id=10,
                        full_text="BOOKING TEXT  12345 //TEST PATTERN",
                        valuta=-100,
                        date=today,
                        account_id=1)

    assert trans.complete is False

    trans.description = "Description"

    assert trans.complete is False

    trans.category_id = 1

    assert trans.complete is True

    message = Transaction(id=11,
                          full_text="BOOKING TEXT  12345 //TEST PATTERN",
                          valuta=0.0,
                          date=today,
                          account_id=1)

    assert message.complete is False

    message.description = True

    assert message.complete is True


def test_transaction_check_rule_matching_multiple_rule_match(db_filled):

    db = db_filled

    rule = Rule(id=7, account_id=1, name="Rule 7", type="out", category_id=4, pattern="PATTERN3", description="Description - Rule Multiple Match")
    rule_3 = Rule.query.filter_by(id=3).one()

    db.session.add(rule)
    db.session.commit()

    trans = Transaction(id=10,
                        full_text="BOOKING TEXT PATTERN3 MULTIPLE MATCH",
                        valuta=-100,
                        date=today,
                        account_id=1)

    with pytest.raises(MultipleRuleMatchError) as e_info:
        trans.check_rule_matching()

    assert e_info.type is MultipleRuleMatchError
    assert e_info.value.transaction is trans
    assert set(e_info.value.rules) == set([rule, rule_3])
    assert e_info.value.index is None


def test_transaction_check_rule_matching_false(db_filled, today):

    db = db_filled

    # transaction would be matched by Rule(id=3) but it should not match
    # due to rule_id=False
    trans = Transaction(id=10,
                        full_text="BOOKING TEXT PATTERN3 SHOULD NOT MATCH",
                        valuta=-100,
                        date=today,
                        rule_id=False,
                        account_id=1)

    db.session.add(trans)

    assert trans.rule_id is False
    assert trans.rule is None
    assert trans.description is None
    assert trans.category_id is None

    trans.check_rule_matching()

    assert trans.rule_id is None
    assert trans.rule is None
    assert trans.description is None
    assert trans.category_id is None


@pytest.mark.parametrize("transaction_id,trend", [
    (1, None),
    (2, None),
    (3, None),
    (4, -172.11),
    (5, None),
    (6, None),
    (7, None),
    (8, None)
])
def test_transaction_calculate_trend(db_filled, transaction_id, trend, caplog):

    trans = Transaction.query.filter_by(id=transaction_id).one()
    trans.trend = None

    assert trans.trend is None

    with caplog.at_level(logging.DEBUG):
        trans._calculate_trend()

    assert trans.trend == trend

    if trend is not None:
        assert "calculated trend" in caplog.text


@pytest.mark.parametrize("transaction_id,editable", [
    (1, False),
    (2, False),
    (3, False),
    (4, False),
    (5, False),
    (6, True),
    (7, False),
    (8, False),
    (9, True)
])
def test_transaction_is_editable(db_filled, transaction_id, editable, today):

    trans = Transaction.query.filter_by(id=transaction_id).one()

    assert trans.is_editable == editable



@pytest.mark.parametrize("text,result", [
    ("BOOKING TEXT", "BOOKING TEXT"),
    ("Booking Text", "BOOKING TEXT"),
    ("  Booking  Text  ", "BOOKING TEXT"),
    ("Booking // \\ Text ", "BOOKING TEXT"),
    ("BOOKING TEXT 20.01.2020", "BOOKING TEXT 20 01 2020"),
    ("BOOKING TEXT 20.01.2020 - 10:00", "BOOKING TEXT 20 01 2020 - 10 00"),
])
def test_transaction_normalize_text(text, result):

    assert Transaction._normalizeText(text) == result


@pytest.mark.parametrize("date,valuta,full_text,exists", [
    (datetime.date(2020, 1, 13), 1890.28, "BOOKING TEXT PATTERN1 #1", True),
    (datetime.date(2020, 2, 12), 1979.28, "BOOKING TEXT PATTERN1 #2", True),
    (datetime.date(2020, 1, 3), -35.78, "BOOKING TEXT PATTERN3 #3", True),
    (datetime.date(2020, 1, 4), -207.89, "BOOKING TEXT PATTERN3 #4", True),
    (datetime.date(2020, 2, 2), -207.89, "BOOKING TEXT PATTERN3 #5", True),
    (datetime.date(2020, 3, 18), 0.0, "MESSAGE TEXT #6", True),
    (datetime.date(2020, 1, 3), 29.98, "BOOKING TEXT PATTERN2 #1", True),
    (datetime.date(2020, 1, 20), 40.45, "BOOKING TEXT NO PATTERN #1", True),
    (datetime.date(2020, 3, 2), 40.45, "BOOKING TEXT NO PATTERN #2", True),
    (datetime.date(2020, 3, 2), 40.45, "    Booking   Text No Pattern   #2   ", True),
    (datetime.date(2020, 1, 13), 1800.28, "BOOKING TEXT PATTERN1 #1", False),
    (datetime.date(2020, 2, 13), 1979.28, "BOOKING TEXT PATTERN1 #2", False),
])
def test_transaction_exist(db_filled, date, valuta, full_text, exists):

    trans = Transaction(
        date=date,
        valuta=valuta,
        full_text=full_text,
    )

    assert trans.exist == exists

    if(exists is True):
        assert trans.account_id is not None


#   ____        __                       _   _             _     _    _                 _ _
#  |  _ \      / _|                 /\  | | | |           | |   | |  | |               | | |
#  | |_) | ___| |_ ___  _ __ ___   /  \ | |_| |_ __ _  ___| |__ | |__| | __ _ _ __   __| | | ___ _ __
#  |  _ < / _ \  _/ _ \| '__/ _ \ / /\ \| __| __/ _` |/ __| '_ \|  __  |/ _` | '_ \ / _` | |/ _ \ '__|
#  | |_) |  __/ || (_) | | |  __// ____ \ |_| || (_| | (__| | | | |  | | (_| | | | | (_| | |  __/ |
#  |____/ \___|_| \___/|_|  \___/_/    \_\__|\__\__,_|\___|_| |_|_|  |_|\__,_|_| |_|\__,_|_|\___|_|
#  ==================================================================================================


def test_before_attach_handler_account_balance(db_filled):
    account = Account.query.first()

    assert account.balance == 3528.88


#  ____        __                _____ _           _     _   _                 _ _
# | __ )  ___ / _| ___  _ __ ___|  ___| |_   _ ___| |__ | | | | __ _ _ __   __| | | ___ _ __
# |  _ \ / _ \ |_ / _ \| '__/ _ \ |_  | | | | / __| '_ \| |_| |/ _` | '_ \ / _` | |/ _ \ '__|
# | |_) |  __/  _| (_) | | |  __/  _| | | |_| \__ \ | | |  _  | (_| | | | | (_| | |  __/ |
# |____/ \___|_|  \___/|_|  \___|_|   |_|\__,_|___/_| |_|_| |_|\__,_|_| |_|\__,_|_|\___|_|
# ===========================================================================================


def test_before_flush_handler_inactive_rule_deleted(db_filled, today):

    db = db_filled

    # set Rule 2 to inactive (deleted)
    rule_2 = Rule.query.filter_by(id=2).one()
    rule_2.end = today - datetime.timedelta(days=1)

    assert rule_2.active is False

    # now delete all transactions
    transactions = Transaction.query.all()

    for transaction in transactions:
        db.session.delete(transaction)
    db.session.commit()

    # check if rule 2 (inactive) was deleted by before_flush handler
    rule_2_deleted = Rule.query.filter_by(id=2).one_or_none()
    assert rule_2_deleted is None

    # active rules should remain intact
    rule_1 = Rule.query.filter_by(id=1).one()
    rule_3 = Rule.query.filter_by(id=3).one()

    assert rule_1.active is True
    assert rule_1.has_assigned_transactions is False

    assert rule_3.active is True
    assert rule_3.has_assigned_transactions is False
