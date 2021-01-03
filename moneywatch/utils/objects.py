# import moneywatch.utils.db as db
import moneywatch.utils.functions as utils
import datetime
import re

from moneywatch.utils.exceptions import MultipleRuleMatchError

from flask import current_app

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import expression as fn
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import event, orm, or_
from sqlalchemy.sql import collate, asc


db = SQLAlchemy()


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
    rules = db.relationship("Rule")


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
            date = latest_transaction.date
            now = datetime.date.today()
            delta = date - now
            return delta

        return None

    def categories(self, type, start=None, end=None):

        result = Category.query.filter_by(account_id=self.id, type=type, parent_id=None).order_by(Category.id.asc()).all()

        if start is not None or end is not None:
            for item in result:
                item.setTimeframe(start, end)

        return result

    def rules_by_type(self, type):

        result = Rule.query.filter_by(account_id=self.id, type=type).order_by(asc(collate(Rule.name, 'NOCASE'))).all()

        return result



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

        result = Transaction.query.filter_by(account_id=self.id)

        if type == "in":
            result = result.filter(Transaction.valuta > 0)
        elif type == "out":
            result = result.filter(Transaction.valuta < 0)
        else:
            result = result.filter(Transaction.valuta == 0)

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
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)

    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id', name="fk_categories_account"), server_default="1", nullable=False)
    account = db.relationship("Account")

    _childs = db.relationship("Category",
                              # cascade deletions
                              cascade="all",

                              # many to one + adjacency list - remote_side
                              # is required to reference the 'remote'
                              # column in the join condition.
                              backref=db.backref("parent", remote_side='Category.id'),
                              )

    rules = db.relationship("Rule")


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

            result = None

            for category in self.childs:
                if category.regular_rules_done is True:
                    result = True
                elif category.regular_rules_done is False:
                    result = False
                    break

            if result is None or result is True:
                for transaction in self.transactions:
                    if transaction.rule_id is not None:
                        if transaction.rule.regular:
                            result = True
                            break

                if result and len(self.planned_transactions) > 0:
                    result = False

            self._cache["regular_rules_done"] = result

        return self._cache["regular_rules_done"]

    @property
    def has_overdued_planned_transactions(self):

        result = False

        for category in self.childs:
            if category.has_overdued_planned_transactions:
                result = True

        for transaction in self.planned_transactions:
            if transaction.overdue:
                result = True

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

    @property
    def on_target(self):

        if self.budget != 0 and self.planned_valuta < self.budget:
            return False

        for category in self.childs or []:
            if not category.on_target:
                return False

        return True


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
    # active = db.Column(db.Boolean, server_default=True, nullable=False)

    next_due = db.Column(db.Date, unique=False, nullable=True)
    next_valuta = db.Column(db.Float, unique=False, nullable=True)
    regular = db.Column(db.Integer, unique=False, nullable=True)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship("Category")

    transactions = db.relationship("Transaction")

    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id', name="fk_rules_account"), server_default="1", nullable=False)
    account = db.relationship("Account")


    def getTransactions(self, start=None, end=None):

        result = Transaction.query.filter_by(account_id=self.account_id, rule_id=self.id)


        if start is not None and end is not None:
            result = result.filter(Transaction.date.between(start, end))
        elif start is not None:
            result = result.filter(Transaction.date >= start)
        elif end is not None:
            result = result.filter(Transaction.date <= end)

        result = result.order_by(Transaction.date.asc(), Transaction.id.asc())

        return result.all()


    def latest_transaction(self, before=None):
        result = Transaction.query.filter_by(account_id=self.account_id, rule_id=self.id)

        if before is not None:
            result = result.filter(Transaction.date <= before)

        return result.order_by(Transaction.date.desc(), Transaction.id.desc()).first()


    @property
    def oldest_transaction(self):
        result = Transaction.query.filter_by(account_id=self.account_id, rule_id=self.id)

        return result.order_by(Transaction.date.asc(), Transaction.id.asc()).first()


    def update_next_due(self, date, valuta):

        if self.regular:
            latest_transaction = self.latest_transaction()

            if latest_transaction is None or (latest_transaction is not None and latest_transaction.date < date):

                next_due = utils.add_months(date, self.regular)

                current_app.logger.info("update rule '%s' (id: '%s') with next due '%s' and next valuta '%s'", self.name, self.id, next_due, valuta)

                self.next_valuta = abs(valuta)
                self.next_due = next_due


    def assign_transaction_ids(self, ids):
        transactions = Transaction.query.filter(Transaction.id.in_(ids)).all()

        for transaction in transactions:
            transaction.rule_id = self.id
            transaction.category_id = self.category_id


    def match_transaction(self, transaction):
        pattern = self.pattern.strip()

        pattern = pattern.replace(" ", r'\s+')

        pattern = r'(?:^\s*|\s+)' + pattern + r'(?:\s+|\s*$)'

        if re.search(pattern, transaction.full_text, re.IGNORECASE):
            return True
        else:
            return False


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
    description = db.Column(db.String(100), unique=False, nullable=False)
    full_text = db.Column(db.String(100), unique=False, nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True, index=True)
    category = db.relationship("Category")

    rule_id = db.Column(db.Integer, db.ForeignKey('ruleset.id'), nullable=True, index=True)
    rule = db.relationship("Rule")

    trend = db.Column(db.Float, unique=False, nullable=True)

    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id', name="fk_transactions_account"), server_default="1", nullable=False)
    account = db.relationship("Account")


    @hybrid_property
    def type(self):
        if self.valuta > 0:
            return "in"
        elif self.valuta < 0:
            return "out"
        else:
            return "message"


    @type.expression
    def type_expr(self):
        return fn.case([(self.valuta > 0, "in"), (self.valuta < 0, "out")], else_="message")


    @property
    def complete(self):
        if self.valuta != 0 and self.description and self.category_id:
            return True
        elif self.valuta == 0 and self.description is True:
            return True
        return False

    def check_rule_matching(self):

        if self.type != "message" and self.rule_id is None and self.id is None:

            founded_rules = []

            account = Account.query.filter_by(id=self.account_id).one()

            for rule in account.rules_by_type(self.type):
                if rule.match_transaction(self):
                    founded_rules.append(rule)

            if len(founded_rules) == 1:
                self.rule_id = founded_rules[0].id

            elif len(founded_rules) > 1:
                raise MultipleRuleMatchError(self, founded_rules)

            if self.rule_id is not None:

                if self.description is None:
                    self.description = founded_rules[0].description

                if self.category_id is None:
                    self.category_id = founded_rules[0].category_id

                # calculate trend compared to the latest transaction in the database
                if founded_rules[0].regular:

                    latest_transaction = founded_rules[0].latest_transaction(self.date)

                    if latest_transaction is not None:
                        trend = round(self.valuta - latest_transaction.valuta, 2)
                        self.trend = trend if trend != 0 else None
                        if self.trend is not None:
                            current_app.logger.debug("calculated trend '%s' for transaction '%s' (%s) from %s", self.trend, self.description, self.valuta, self.date)


        # if multiple match occurs and user selects "None" (value: False)
        if self.rule_id is False:
            self.rule_id = None


    @property
    def is_editable(self):

        now = datetime.date.today()

        if (now - datetime.timedelta(days=14) <= self.date <= now) or utils.is_same_month(self.date, now):
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





@event.listens_for(db.session, 'before_attach')
def handle_before_attach(session, item):

    if isinstance(item, Transaction):

        # update account balance
        account = Account.query.filter_by(id=item.account_id).one()
        account.balance = round(account.balance + item.valuta, 2)

        if item.rule_id is not None:
            rule = Rule.query.filter_by(id=item.rule_id).one_or_none()

            if rule is not None:
                # update rule next due date/valuta
                rule.update_next_due(item.date, item.valuta)


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
        return self.description + " (" + str(self.valuta) + " € at " + str(self.date) + ")"
