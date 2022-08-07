# import moneywatch.utils.db as db
import moneywatch.utils.functions as utils
import datetime
import re

from moneywatch.utils.exceptions import MultipleRuleMatchError

from flask import current_app

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import expression as fn
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import event, orm, or_, MetaData
from sqlalchemy.sql import collate, asc
from sqlalchemy.orm import validates


# define explicit naming convention defaults for SQL-Alchemy
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "type_ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


#                                     _
#      /\                            | |
#     /  \   ___ ___ ___  _   _ _ __ | |_
#    / /\ \ / __/ __/ _ \| | | | '_ \| __|
#   / ____ \ (_| (_| (_) | |_| | | | | |_
#  /_/    \_\___\___\___/ \__,_|_| |_|\__|
#


class Account(db.Model):

    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(), unique=True, nullable=False)
    iban = db.Column(db.String(22), unique=True, nullable=False)
    balance = db.Column(db.Float, unique=False, nullable=False)
    color = db.Column(db.String(6), unique=False, nullable=True)
    rules = db.relationship("Rule", back_populates="account", cascade="all, delete, delete-orphan")

    _transactions = db.relationship("Transaction", back_populates="account", cascade="all, delete, delete-orphan")
    _categories = db.relationship("Category", back_populates="account", cascade="all, delete, delete-orphan")


    @validates('iban')
    def validate_name(self, key, value):
        if not utils.is_valid_iban(value):
            raise ValueError("the provided IBAN is not valid")
        return value

    @property
    def oldest_transaction(self):
        return Transaction.query.filter_by(account_id=self.id).order_by(Transaction.date.asc(), Transaction.id.asc()).first() # noqa


    @property
    def latest_transaction(self):
        return Transaction.query.filter_by(account_id=self.id).order_by(Transaction.date.desc(), Transaction.id.desc()).first()


    @property
    def iban_formatted(self):
        return utils.format_iban_human(self.iban)


    @property
    def last_update(self):
        latest_transaction = self.latest_transaction

        if latest_transaction is not None:
            return latest_transaction.date

        return None


    def categories(self, type, start=None, end=None):

        result = Category.query.filter_by(account_id=self.id, type=type, parent_id=None).order_by(Category.id.asc()).all()

        if start is not None or end is not None:
            for item in result:
                item.setTimeframe(start, end)

        return result


    def rules_by_type(self, type, active=True):

        result = Rule.query.filter_by(account_id=self.id, type=type)

        if active is not None:
            result = result.filter_by(active=active)

        result = result.order_by(asc(collate(Rule.name, 'NOCASE')))

        return result.all()


    def non_regular_rules(self, type, start, end):

        result = []

        rules = Rule.query.filter_by(account_id=self.id, type=type).filter(Rule.regular > 1).all()

        for rule in rules:

            if rule.regular and rule.regular > 1 and rule.next_due <= end and rule.next_valuta > 0:

                dates = utils.get_cyclic_dates_for_timerange(rule.next_due, rule.regular, start, end)
                date_result = []
                for date in dates:
                    if date >= start and date >= rule.next_due and (date >= datetime.date.today() or utils.is_same_month(date, datetime.date.today())):
                        date_result.append(date)

                if len(date_result) > 0:
                    result.append((rule, date_result))

        return result


    def transactions(self, start=None, end=None):

        result = Transaction.query.filter_by(account_id=self.id)

        if start is not None and end is not None:
            result = result.filter(Transaction.date.between(start, end))
        elif start is not None:
            result = result.filter(Transaction.date >= start)
        elif end is not None:
            result = result.filter(Transaction.date <= end)

        result = result.order_by(Transaction.date.asc(), Transaction.id.asc())

        return result.all()


    def search_for_transactions(self, term):

        transactions = Transaction.query.filter(Transaction.account_id == self.id).filter(or_(Transaction.description.like('%' + term + '%'), Transaction.full_text.like('%' + term + '%'))).order_by(Transaction.date.desc(), Transaction.id.desc()).all()

        return transactions


    def transactions_by_type(self, type, start=None, end=None):

        result = Transaction.query.filter_by(account_id=self.id, type=type)

        if start is not None and end is not None:
            result = result.filter(Transaction.date.between(start, end))
        elif start is not None:
            result = result.filter(Transaction.date >= start)
        elif end is not None:
            result = result.filter(Transaction.date <= end)

        result = result.order_by(Transaction.date.asc(), Transaction.id.asc())

        return result.all()

#     _____      _
#    / ____|    | |
#   | |     __ _| |_ ___  __ _  ___  _ __ _   _
#   | |    / _` | __/ _ \/ _` |/ _ \| '__| | | |
#   | |___| (_| | ||  __/ (_| | (_) | |  | |_| |
#    \_____\__,_|\__\___|\__, |\___/|_|   \__, |
#                         __/ |            __/ |
#                        |___/            |___/


class Category(db.Model):

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    type = db.Column(db.Enum("in", "out"), unique=False, nullable=False)
    budget_monthly = db.Column(db.Integer, unique=False, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete="CASCADE"), nullable=True)

    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id', ondelete="CASCADE"), server_default="1", nullable=False)
    account = db.relationship("Account", back_populates="_categories")

    _childs = db.relationship("Category",
                              # cascade deletions
                              cascade="all, delete, delete-orphan",

                              # many to one + adjacency list - remote_side
                              # is required to reference the 'remote'
                              # column in the join condition.
                              backref=db.backref("parent", remote_side='Category.id'),
                              )

    rules = db.relationship("Rule", back_populates="category")

    _transactions = db.relationship("Transaction", back_populates="category")


    def __init__(self, start=None, end=None, **kwargs):
        self._cache = {}
        self.setTimeframe(start, end)
        super(Category, self).__init__(**kwargs)


    @orm.reconstructor
    def init_on_load(self):
        self._cache = {}


    def setTimeframe(self, start=None, end=None):
        self._data = {}
        self._data["start"] = start
        self._data["end"] = end


    @property
    def planned_transactions(self):

        if "planned_transactions" not in self._cache:

            result = []

            latest_transaction = self.account.latest_transaction

            latest_transaction_date = datetime.date.today()
            today_date = datetime.date.today()

            if latest_transaction:
                latest_transaction_date = latest_transaction.date

            for rule in self.rules:

                if rule.regular and not rule.next_due > self.end and rule.next_valuta > 0:

                    booked_dates = []
                    planned_dates = []

                    # get already existing transaction dates
                    for transaction in self.transactions:
                        if transaction.rule_id == rule.id:
                            booked_dates.append(transaction.date)

                    # if already transactions available, just calculate from the date of newest transactions
                    if len(booked_dates) > 0:
                        planned_dates = utils.get_cyclic_dates_for_timerange(rule.next_due, rule.regular, max(booked_dates), self.end)
                    else:
                        planned_dates = utils.get_cyclic_dates_for_timerange(rule.next_due, rule.regular, self.start, self.end)

                    current_app.logger.debug("found planned transactions for rule '%s': %s", rule.name, planned_dates)

                    for planned_date in planned_dates:
                        if (
                                # no transaction for the same year/month exists
                                (not utils.is_same_month_in_list(planned_date, booked_dates))

                                and   # noqa: W503,W504

                                # date is older then latest transaction for this account
                                (planned_date.year > latest_transaction_date.year or (planned_date.year == latest_transaction_date.year and planned_date.month >= latest_transaction_date.month))

                                and   # noqa: W503,W504

                                # planned transactions should be listed only for current or future months
                                (planned_date >= today_date or utils.is_same_month(planned_date, today_date))
                        ):

                            overdue = (planned_date <= latest_transaction_date and planned_date < today_date)

                            if self.type == "out":
                                result.append(PlannedTransaction(planned_date, rule.next_valuta * -1, rule.description, rule.id, overdue))
                            else:
                                result.append(PlannedTransaction(planned_date, rule.next_valuta, rule.description, rule.id, overdue))

            result.sort(key=lambda x: x.date)
            self._cache["planned_transactions"] = result

        return self._cache["planned_transactions"]


    @property
    def regular_rules_done(self):

        if "regular_rules_done" not in self._cache:

            result = False

            for transaction in self.transactions:
                if transaction.rule_id is not None:
                    if transaction.rule.regular:
                        result = True
                        break

            if result is True and len(self.planned_transactions) > 0:
                result = False

            self._cache["regular_rules_done"] = result

        return self._cache["regular_rules_done"]


    @property
    def has_overdued_planned_transactions(self):

        result = False

        for category in self.childs:
            if category.has_overdued_planned_transactions:
                result = True
                break

        if result is False:
            for transaction in self.planned_transactions:
                if transaction.overdue:
                    result = True
                    break

        return result


    @property
    def budget(self):

        budget = self.budget_monthly

        if budget is not None and self.type == "out":

            # adapt budget to number of months
            budget *= -1 * utils.get_number_of_months(self.start, self.end)

            budget = round(budget, 2)

        return budget


    @property
    def start(self):

        if hasattr(self, "_data"):
            return self._data.get("start", utils.get_first_day_of_month())
        else:
            return None


    @property
    def end(self):

        if hasattr(self, "_data"):
            return self._data.get("end", utils.get_last_day_of_month())
        else:
            return None


    @property
    def childs(self):

        result = self._childs

        if self.start is not None or self.end is not None:

            for category in result:
                category.setTimeframe(self.start, self.end)

        return result


    @property
    def transactions(self):

        if "transactions" not in self._cache:

            result = Transaction.query.filter_by(category_id=self.id)
            result = result.filter(Transaction.date.between(self.start, self.end))
            result = result.order_by(Transaction.date.asc(), Transaction.id.asc())

            self._cache["transactions"] = result.all()

        return self._cache["transactions"]


    @property
    def transactions_with_childs(self):

        if "transactions_with_childs" not in self._cache:

            result = []

            result.extend(self.transactions)

            for category in self.childs:
                result.extend(category.transactions_with_childs)

            self._cache["transactions_with_childs"] = result

        # resulting transactions are not in the correct sorted order.
        # ordering should be made by the calling function to avoid recursive sorting
        return self._cache["transactions_with_childs"]


    @property
    def transactions_combined(self):

        if "transactions_combined" not in self._cache:

            result = []

            result.extend(self.transactions)
            result.extend(self.planned_transactions)

            result.sort(key=lambda item: item.date)

            self._cache["transactions_combined"] = result

        return self._cache["transactions_combined"]


    def getCategoryPath(self, delimiter):

        if self.parent_id is not None:
            parent = self.parent
            return parent.getCategoryPath(delimiter) + delimiter + self.name
        else:
            return self.name


    def getCategoryIdsAndPaths(self, delimiter):

        result = []

        result.append({"id": self.id, "path": self.getCategoryPath(delimiter)})

        for category in self.childs:
            result.extend(category.getCategoryIdsAndPaths(delimiter))

        return result


    @property
    def valuta(self):

        if "valuta" not in self._cache:

            result = 0.0

            for category in self.childs or []:
                result += category.valuta

            for transaction in self.transactions or []:
                result += transaction.valuta

            self._cache["valuta"] = round(result, 2)

        return self._cache["valuta"]


    @property
    def planned_transactions_valuta(self):

        if "planned_transactions_valuta" not in self._cache:

            result = 0.0

            for category in self.childs or []:
                result += category.planned_transactions_valuta

            for transaction in self.planned_transactions or []:
                result += transaction.valuta

            self._cache["planned_transactions_valuta"] = round(result, 2)

        return self._cache["planned_transactions_valuta"]

    @property
    def planned_valuta(self):

        if "planned_valuta" not in self._cache:

            result = 0
            for transaction in self.transactions or []:
                result += transaction.valuta

            for transaction in self.planned_transactions or []:
                result += transaction.valuta

            for category in self.childs or []:
                result += category.planned_valuta

            if self.budget is not None and not result < self.budget:
                result = self.budget

            self._cache["planned_valuta"] = round(result, 2)

        return self._cache["planned_valuta"]


    def has_sibling_name(self, name):

        res = Category.query.filter_by(type=self.type, parent_id=self.parent_id, name=name).one_or_none()

        if res is not None:
            return True

        return False


#    _____       _
#   |  __ \     | |
#   | |__) |   _| | ___
#   |  _  / | | | |/ _ \
#   | | \ \ |_| | |  __/
#   |_|  \_\__,_|_|\___|
#
#


class Rule(db.Model):
    __tablename__ = 'ruleset'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(100), unique=False, nullable=False)
    pattern = db.Column(db.String(100), unique=False, nullable=False)
    type = db.Column(db.Enum("in", "out"), unique=False, nullable=False)
    start = db.Column(db.Date, unique=False, nullable=True, index=True)
    end = db.Column(db.Date, unique=False, nullable=True, index=True)

    next_due = db.Column(db.Date, unique=False, nullable=True)
    next_valuta = db.Column(db.Float, unique=False, nullable=True)
    regular = db.Column(db.Integer, unique=False, nullable=True)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship("Category", back_populates="rules")

    _transactions = db.relationship("Transaction", back_populates="rule")

    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id', ondelete="CASCADE"), server_default="1", nullable=False)
    account = db.relationship("Account", back_populates="rules")

    __table_args__ = (
        db.UniqueConstraint('name', 'account_id', 'type'),
    )


    def __init__(self, **kwargs):
        self.start = datetime.date.today()
        super(Rule, self).__init__(**kwargs)


    def transactions(self, start=None, end=None):

        result = Transaction.query.filter_by(account_id=self.account_id, rule_id=self.id)

        if start is not None and end is not None:
            result = result.filter(Transaction.date.between(start, end))
        elif start is not None:
            result = result.filter(Transaction.date >= start)
        elif end is not None:
            result = result.filter(Transaction.date <= end)

        result = result.order_by(Transaction.date.asc(), Transaction.id.asc())

        return result.all()


    def latest_transaction(self, before_id=None):
        result = Transaction.query.filter_by(account_id=self.account_id, rule_id=self.id)

        if before_id is not None:
            result = result.filter(Transaction.id < before_id)

        return result.order_by(Transaction.date.desc(), Transaction.id.desc()).first()


    @property
    def oldest_transaction(self):
        result = Transaction.query.filter_by(account_id=self.account_id, rule_id=self.id)

        return result.order_by(Transaction.date.asc(), Transaction.id.asc()).first()


    def update_next_due(self, date, valuta):

        if self.regular:

            next_due = utils.add_months(date, self.regular)

            if self.next_due is not None:
                if next_due <= self.next_due:
                    return

                # do not update when rule next due is in the same month as the calculated one
                if utils.is_same_month(self.next_due, next_due):
                    current_app.logger.debug("skipping next due update for rule '%s', as next due is already in the same month", self.name)
                    return

            current_app.logger.info("update rule '%s' (id: '%s') with next due '%s' and next valuta '%.2f'", self.name, self.id, next_due, valuta)

            self.next_valuta = abs(valuta)
            self.next_due = next_due


    def assign_transaction_ids(self, ids):
        transactions = Transaction.query.filter(Transaction.id.in_(ids)).all()

        for transaction in transactions:
            if not self.match_transaction(transaction):
                continue
            transaction.rule = self
            transaction.category = self.category



    def match_transaction(self, transaction):
        pattern = self.pattern.strip()

        pattern = pattern.replace(" ", r'\s+')

        pattern = r'(?:^\s*|\s+|[^a-z0-9])' + pattern + r'(?:[^a-z0-9]|\s+|\s*$)'

        if transaction.account_id == self.account_id and transaction.type == self.type and re.search(pattern, transaction.full_text, re.IGNORECASE):
            return True
        else:
            return False


    @property
    def has_assigned_transactions(self):
        return self._transactions is not None and len(self._transactions) > 0

    @hybrid_property
    def active(self):
        return self.end is None

    @active.expression
    def active(cls):
        return cls.end == None  # noqa: E711


#    _______                             _   _
#   |__   __|                           | | (_)
#      | |_ __ __ _ _ __  ___  __ _  ___| |_ _  ___  _ __
#      | | '__/ _` | '_ \/ __|/ _` |/ __| __| |/ _ \| '_ \
#      | | | | (_| | | | \__ \ (_| | (__| |_| | (_) | | | |
#      |_|_|  \__,_|_| |_|___/\__,_|\___|\__|_|\___/|_| |_|
#
#

class Transaction(db.Model):

    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True, index=True)

    date = db.Column(db.Date, unique=False, nullable=False, index=True)
    valuta = db.Column(db.Float, unique=False, nullable=False)
    description = db.Column(db.String(100), unique=False, nullable=True)
    full_text = db.Column(db.String(100), unique=False, nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id',), nullable=True, index=True)
    category = db.relationship("Category", back_populates="_transactions")

    rule_id = db.Column(db.Integer, db.ForeignKey('ruleset.id', ondelete="SET NULL"), nullable=True, index=True)
    rule = db.relationship("Rule", back_populates="_transactions")

    trend = db.Column(db.Float, unique=False, nullable=True)

    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id', ondelete="CASCADE"), server_default="1", nullable=False)
    account = db.relationship("Account", back_populates="_transactions")

    @hybrid_property
    def type(self):
        if self.valuta > 0:
            return "in"
        elif self.valuta < 0:
            return "out"
        else:
            return "message"


    @type.expression
    def type(cls):
        return fn.case([(cls.valuta > 0, "in"), (cls.valuta < 0, "out")], else_="message")


    @property
    def complete(self):
        if self.type != "message" and self.description and self.category_id:
            return True
        elif self.type == "message" and self.description is True:
            return True
        return False


    def check_rule_matching(self):
        # if no rule is given (from multiple rule match form), check ruleset...
        if self.type != "message" and self.rule_id is None:

            founded_rules = []

            account = Account.query.filter_by(id=self.account_id).one()

            for rule in account.rules_by_type(self.type):
                if rule.match_transaction(self):
                    founded_rules.append(rule)

            if len(founded_rules) == 1:
                self.rule = founded_rules[0]

            elif len(founded_rules) > 1:
                raise MultipleRuleMatchError(self, founded_rules)

            if self.rule is not None:

                if self.description is None:
                    self.description = self.rule.description if self.rule.description else self.rule.name

                if self.category_id is None:
                    self.category_id = self.rule.category_id

        # if multiple rule match was happened and user selected "None" (value: False)
        if self.rule_id is False:
            self.rule_id = None
            self.rule = None

        # rule is set (manual by multiple rule match form or found by ruleset search)
        elif self.rule is not None:

            # update rule next due
            self.rule.update_next_due(self.date, self.valuta)

            # calculate trend compared to the latest transaction in the database
            self._calculate_trend()


    def _calculate_trend(self):

        if self.rule is None or not self.rule.regular:
            return

        latest_transaction = self.rule.latest_transaction(self.id)

        if latest_transaction is None:
            return

        trend = round(self.valuta - latest_transaction.valuta, 2)
        self.trend = trend if trend != 0 else None

        if self.trend is not None:
            current_app.logger.debug("calculated trend '%.2f' for transaction '%s' (%s) from %s based on last transaction from %s (%.2f)", self.trend, self.description, self.valuta, self.date, latest_transaction.date, latest_transaction.valuta)


    @property
    def is_editable(self):

        now = datetime.date.today()

        if ((now - datetime.timedelta(days=14)) <= self.date <= now):
            return True
        elif utils.is_same_month(self.date, now):
            return True

        return False


    # def __repr__(self):
        # return self.__class__.__name__+"("+str(self._data)+")"



    @staticmethod
    def _normalizeText(text):
        new_text = text

        for char in "/:.\\":
            new_text = new_text.replace(char, " ")

        new_text = ' '.join(new_text.split())

        return new_text.upper()

    @property
    def exist(self):
        transactions = Transaction.query.filter_by(date=self.date, valuta=self.valuta).all()

        for transaction in transactions:
            if transaction:
                if Transaction._normalizeText(transaction.full_text) == Transaction._normalizeText(self.full_text):
                    self.account_id = transaction.account_id
                    return True

        return False


#   _____                 _   _   _                 _ _
#  | ____|_   _____ _ __ | |_| | | | __ _ _ __   __| | | ___ _ __
#  |  _| \ \ / / _ \ '_ \| __| |_| |/ _` | '_ \ / _` | |/ _ \ '__|
#  | |___ \ V /  __/ | | | |_|  _  | (_| | | | | (_| | |  __/ |
#  |_____| \_/ \___|_| |_|\__|_| |_|\__,_|_| |_|\__,_|_|\___|_|
#

@event.listens_for(db.session, 'before_attach')
def handle_before_attach(session, item):

    if isinstance(item, Transaction):

        # update account balance
        account = Account.query.filter_by(id=item.account_id).one()
        account.balance = round(account.balance + item.valuta, 2)


@event.listens_for(db.session, 'before_flush')
def handler_before_flush(session, flush_context, instances):
    if session.deleted:
        for item in session.deleted:

            # when transactions are deleted,
            # check if assigned inactive rules can be deleted as well
            if isinstance(item, Transaction):
                if item.rule is None:
                    continue

                # clear rule binding
                rule = item.rule
                item.rule = None

                # check if rule can be deleted (inactive and no transactions assigned)
                if not rule.has_assigned_transactions and not rule.active:
                    current_app.logger.debug("deleting rule '%s' after last transaction '%s' was deleted and rule is inactive", rule, item)
                    session.delete(rule)


#    _____  _                            _ _______                             _   _
#   |  __ \| |                          | |__   __|                           | | (_)
#   | |__) | | __ _ _ __  _ __   ___  __| |  | |_ __ __ _ _ __  ___  __ _  ___| |_ _  ___  _ __
#   |  ___/| |/ _` | '_ \| '_ \ / _ \/ _` |  | | '__/ _` | '_ \/ __|/ _` |/ __| __| |/ _ \| '_ \
#   | |    | | (_| | | | | | | |  __/ (_| |  | | | | (_| | | | \__ \ (_| | (__| |_| | (_) | | | |
#   |_|    |_|\__,_|_| |_|_| |_|\___|\__,_|  |_|_|  \__,_|_| |_|___/\__,_|\___|\__|_|\___/|_| |_|
#
#

class PlannedTransaction:


    def __init__(self, date, valuta, description, rule_id, overdue):
        self.date = date
        self.valuta = valuta
        self.description = description
        self.rule_id = rule_id
        self.overdue = overdue

    def __repr__(self):
        return "PlannedTransaction(description=%r', valuta=%r, date=%r, rule_id=%r, overdue=%r)" % (self.description, self.valuta, self.date, self.rule_id, self.overdue)

    def __eq__(self, other):
        return repr(self) == repr(other)
