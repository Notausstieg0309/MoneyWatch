from flask import (Blueprint, flash, redirect, render_template, request, url_for, abort, session)

from flask_babel import gettext

from moneywatch.utils.objects import db, Rule, Account, Transaction
import moneywatch.utils.functions as utils
import re

bp = Blueprint('ruleset', __name__)


@bp.route('/<int:account_id>/ruleset/')
def index(account_id):
    """Show all the rules"""
    account = Account.query.filter_by(id=account_id).one()

    rules_in = account.rules_by_type("in")
    rules_out = account.rules_by_type("out")

    return render_template('ruleset/index.html', account=account, rules_in=rules_in, rules_out=rules_out)


@bp.route('/<int:account_id>/ruleset/add/<string:rule_type>/', methods=('GET', 'POST'))
def add(account_id, rule_type):

    account = Account.query.filter_by(id=account_id).one_or_none()

    transaction = None

    if "import_objects" in session and "import_id" in request.args:
        try:
            index = int(request.args["import_id"])
        except ValueError:
            index = None

        if index is not None:
            transaction = session["import_objects"][index]
    elif "transaction_id" in request.args:
        try:
            index = int(request.args["transaction_id"])
        except ValueError:
            index = None

        if index is not None:
            transaction = Transaction.query.filter_by(id=index).one_or_none()

    if account is None:
        abort(404, "account not found")

    categories = account.categories(rule_type)

    if not categories:
        flash(gettext("Unable to create new rules. No categories are available to create rules for. Please create categories first."))
        return redirect(url_for('ruleset.index', account_id=account.id))

    if request.method != 'POST':
        return render_template('ruleset/add.html', account=account, rule_type=rule_type, categories=categories, transaction=transaction)

    name = request.form['name'].strip()
    pattern = request.form['pattern']
    description = request.form['description'].strip()
    regular = request.form['regular']
    next_valuta = request.form.get('next_valuta', None)
    next_due = request.form.get('next_date', None)
    category_id = request.form.get('category_id', None)

    valid_pattern = True

    errors = []

    if not name:
        errors.append(gettext('Rule name is required.'))

    if not pattern:
        errors.append(gettext('Search pattern is required.'))

    if not category_id:
        errors.append(gettext('Category is required.'))

    try:
        re.compile(pattern)
    except re.error:
        valid_pattern = False
        errors.append(gettext("Invalid search pattern. The given search pattern is not a valid regular expression"))

    if valid_pattern and transaction is not None:
        tmp_rule = Rule(account_id=account.id, type=rule_type, pattern=pattern)
        if not tmp_rule.match_transaction(transaction):
            errors.append(gettext("Entered pattern does not matched the selected transaction you want to create this rule for."))


    if next_due.strip() != "":
        next_due = utils.get_date_from_string(next_due, "%Y-%m-%d")
    else:
        next_due = None

    if next_valuta.strip() == "":
        next_valuta = None

    matched_transactions = []
    selected_transaction_ids = request.form.getlist("matched_transactions")

    if len(errors) != 0:
        for error in errors:
            flash(error)

    else:
        item = {}

        item["type"] = rule_type
        item["name"] = name
        item["pattern"] = pattern
        item["description"] = description
        item["category_id"] = category_id
        item["account_id"] = account.id
        item["regular"] = regular

        item["next_due"] = next_due
        item["next_valuta"] = next_valuta

        new_rule = Rule(**item)




        if request.form.get("check_historical", None) == "on" and valid_pattern:

            for transaction in account.transactions_by_type(rule_type):
                if new_rule.match_transaction(transaction):
                    matched_transactions.append(transaction)

        if request.form['action'] == "save":

            db.session.add(new_rule)
            db.session.commit()

            if request.form.get("check_historical", None) == "on" and len(selected_transaction_ids) > 0:
                new_rule.assign_transaction_ids(selected_transaction_ids)
                db.session.commit()

            if "import_objects" in session and "import_id" in request.args:
                return redirect(url_for('import.index', resume=1))
            elif "transaction_id" in request.args and transaction is not None:
                return redirect(url_for('transactions.edit', id=transaction.id))

            return redirect(url_for('ruleset.index', account_id=account.id))

    if request.form.get("check_historical", None) == "on":
        return render_template('ruleset/check.html', account=account, rule_type=rule_type, categories=categories, matched_transactions=matched_transactions, selected_transaction_ids=selected_transaction_ids, transaction=transaction)
    else:
        return render_template('ruleset/add.html', account=account, rule_type=rule_type, categories=categories, transaction=transaction)




@bp.route('/ruleset/delete/<int:id>/')
def delete(id):

    rule = Rule.query.filter_by(id=id).one_or_none()

    if rule is not None:

        # preserve account ID for redirection back to the ruleset overview
        account_id = rule.account_id

        # delete the rule
        db.session.delete(rule)
        db.session.commit()

        return redirect(url_for('ruleset.index', account_id=account_id))

    else:
        abort(404, "rule not found")


@bp.route('/ruleset/change/<int:id>/', methods=('GET', 'POST'))
def change(id):

    rule = Rule.query.filter_by(id=id).one()
    errors = []

    if request.method == 'POST':
        error = None

        name = request.form['name'].strip()
        pattern = request.form['pattern']
        description = request.form['description'].strip()
        category_id = request.form['category_id']
        regular = request.form['regular']
        next_due = request.form['next_due']
        next_valuta = request.form['next_valuta']

        if not name:
            errors.append(gettext('Name is required.'))
        if not pattern:
            errors.append(gettext('Search pattern is required.'))
        if not category_id:
            errors.append(gettext('Category is required.'))

        try:
            re.compile(pattern)
        except re.error:
            errors.append(gettext("Invalid search pattern. The given search pattern is not a valid regular expression"))

        if len(errors) > 0:
            for error in errors:
                flash(error)

        else:

            rule.name = name
            rule.pattern = pattern
            rule.description = description
            rule.category_id = category_id
            rule.regular = regular

            if regular is not None and regular != "0":
                rule.next_due = utils.get_date_from_string(next_due, "%Y-%m-%d")
                rule.next_valuta = next_valuta
            else:
                rule.next_due = None
                rule.next_valuta = None

            db.session.commit()

            return redirect(url_for('ruleset.index', account_id=rule.account_id))

    categories = rule.account.categories(rule.type)

    return render_template('ruleset/change.html', rule=rule, categories=categories)
