from flask import (Blueprint, flash, redirect, render_template, request, url_for, session)

import os
import datetime

import moneywatch.utils.functions as utils

from flask_babel import gettext

from moneywatch.utils.objects import db, Transaction, Account
from moneywatch.utils.plugins import ImportPluginsManager
from moneywatch.utils.exceptions import MultipleRuleMatchError, ItemsWithoutAccountError, UnknownAccountError, MultiplePluginMatchError, NoPluginMatchError

from schwifty.exceptions import SchwiftyException

bp = Blueprint('import', __name__)
plugins = ImportPluginsManager(os.path.dirname(os.path.realpath(__file__)) + "/import_plugins")


@bp.route('/import/', methods=('GET', 'POST'))
def index():

    if request.method == 'POST' or ("resume" in request.args and "import_items" in session):
        error = None

        if "file" not in request.files and "import_objects" not in session and "import_items" not in session:
            error = gettext("No file uploaded")

        if error is not None:
            flash(error)
        else:

            if "file" in request.files:

                available_plugins = plugins.resolve_plugins_for_file(request.files['file'])

                session.clear()

                if len(available_plugins) > 0:

                    if len(available_plugins) == 1:
                        items = plugins.parse_file(request.files['file'], available_plugins[0]["name"])

                        session['import_items'] = items
                        session['import_plugin_description'] = available_plugins[0]["description"] or gettext('Import plugin file "%(name)s"', name=available_plugins[0]["_filename"])

                    else:
                        raise MultiplePluginMatchError(request.files['file'], available_plugins)

                else:
                    raise NoPluginMatchError(request.files['file'])



            if "import_items" in session:

                # apply rule id for transactions that raised an MultipleRuleMatchError exception
                if "multiple_rule_match" in session:
                    apply_multiple_rule_match_edits(session['import_items'], request.form)
                    session.pop("multiple_rule_match", None)

                # apply account id for transactions that raised an ItemsWithoutAccountError exception
                elif "no_account_given" in session and "account_id" in request.form:
                    apply_account_id_changes(session["no_account_given"], request.form["account_id"])
                    session.pop("no_account_given", None)

                # unknown account iban is ignored during import
                if "ignore_iban" in request.form:
                    session.pop("account_not_found", None)
                    iban = request.form["ignore_iban"]

                    # remove all related transaction items from import
                    for item in session['import_items'][:]:
                        if item.get("account", None) == iban:
                            session['import_items'].remove(item)

                try:
                    session['import_objects'] = create_transactions_from_import(session['import_items'])
                except UnknownAccountError as e:
                    raise UnknownAccountError(iban=e.iban, item=e.item, plugin_description=session['import_plugin_description'])

                # indicate that session objects where modified inline
                session.modified = True



            if request.form.get('action', None) == "save":
                apply_import_edits(session['import_objects'], request.form)

                account_ids = []

                for transaction in session['import_objects']:

                    if transaction.account_id not in account_ids:
                        account_ids.append(transaction.account_id)

                last_date = session['import_objects'][0].date

                db.session.commit()
                session.clear()

                if len(account_ids) == 1:

                    today = datetime.date.today()
                    if last_date.month == today.month and last_date.year == today.year:
                        return redirect(url_for('overview.overview', account_id=account_ids[0]))
                    else:
                        return redirect(url_for('overview.month_overview', account_id=account_ids[0], year=last_date.year, month=last_date.month))

                return redirect(url_for('overview.index'))

            else:
                # don't save anything
                db.session.rollback()

            categories = {}

            if len(session.get("import_objects", [])) > 0:
                categories = get_categories()

            return render_template('importer/check.html', data=(session.get("import_objects", [])), complete=check_if_items_complete(session.get("import_objects", [])), categories=categories)

    return render_template('importer/index.html', extensions=plugins.get_possible_file_extensions())


@bp.errorhandler(MultipleRuleMatchError)
def handle_multiple_rule_match(error):

    session["multiple_rule_match"] = error.index

    if error.transaction.valuta < 0:
        categories = get_categories()[error.transaction.account_id]["out"]
    else:
        categories = get_categories()[error.transaction.account_id]["in"]

    return render_template('importer/multiple_rule_match.html', transaction=error.transaction, rules=error.rules, index=error.index, categories=categories)


@bp.errorhandler(ItemsWithoutAccountError)
def handle_no_account_given(error):

    accounts = Account.query.all()

    if len(accounts) == 1:
        apply_account_id_changes(error.index_list, accounts[0].id)

        flash(gettext("The file contains transactions that cannot be clearly assigned to an account based on the IBAN. Since only one account is currently created, these transactions were automatically assigned to the account \"%(account_name)s\". In case this is wrong, please create an appropriate account first and then assign the transactions manually to the new account during import.", account_name=accounts[0].name))

        session['import_objects'] = create_transactions_from_import(session['import_items'])
        session.modified = True

        categories = {}

        if len(session.get("import_objects", [])) > 0:
            categories = get_categories()

        return render_template('importer/check.html', data=(session.get("import_objects", [])), complete=check_if_items_complete(session.get("import_objects", [])), categories=categories)

    else:
        session["no_account_given"] = error.index_list

    return render_template('importer/no_account_given.html', accounts=accounts, count_items=len(error.index_list))



@bp.errorhandler(NoPluginMatchError)
def handle_no_plugin_match(error):
    flash(gettext("No suitable import plugin found, that can handle the uploaded file."))
    return redirect(url_for("import.index"))


@bp.errorhandler(SchwiftyException)
def handle_schwifty_exception(error):
    flash(gettext("The given file contains an invalid account IBAN value: %(exception_message)s", exception_message=error))
    return redirect(url_for("import.index"))


@bp.errorhandler(UnknownAccountError)
def handle_unknown_account_error(error):
    transaction = error.item.copy()

    if transaction["valuta"] > 0:
        transaction["type"] = "in"
    elif transaction["valuta"] < 0:
        transaction["type"] = "out"
    else:
        transaction["type"] = "message"

    session["account_not_found"] = 1

    return render_template('importer/unknown_account.html', transaction=transaction, plugin_description=error.plugin_description, iban=error.iban, iban_formatted=utils.format_iban_human(error.iban))


def create_transactions_from_import(items, check_all=False):


    result = []

    accounts = {}

    # the account id of the latest already imported transaction of the given file
    latest_transaction_account_id = None

    # list of item ids which have no account iban
    item_ids_iban_missing = []

    for item in items:

        if "account" in item:

            if not item["account"] in accounts:
                iban = utils.normalize_iban(item["account"])
                account = Account.query.filter_by(iban=iban).one_or_none()
                if account is not None:
                    accounts[item["account"]] = account.id
                else:
                    raise UnknownAccountError(iban, item)

            item["account_id"] = accounts[item["account"]]
            item.pop("account", None)

        trans = Transaction(**item)
        exist = trans.exist

        # if a transaction of the given file already exists, save the account_id to use it for items, that don't have a account iban provided by the import plugin.
        if latest_transaction_account_id is None and "account" not in item and exist:
            latest_transaction_account_id = trans.account_id

        if exist:
            if check_all:
                continue
            else:
                break

        if not trans.account_id:
            item_ids_iban_missing.append(items.index(item))

        result.append(trans)


    if latest_transaction_account_id is None and len(item_ids_iban_missing) > 0:
        raise ItemsWithoutAccountError(item_ids_iban_missing)

    # reverse transaction list to get correct ID order while adding (oldest transaction first instead of newest transaction first)
    # and correct trend calculation based on the previous transaction (within session or already stored in database)
    for item in reversed(result):
        if latest_transaction_account_id is not None and item.account_id is None:
            item.account_id = latest_transaction_account_id

        db.session.add(item)

        try:
            # perform rule matching after adding item to session,
            # so trend calculation is considering previous added
            # items in pending DB session not yet stored
            item.check_rule_matching()
        except MultipleRuleMatchError as e:
            raise MultipleRuleMatchError(e.transaction, e.rules, result.index(item))
    return result


def check_if_items_complete(items):

    for item in items:
        if not item.complete:
            return False

    return True


def apply_import_edits(import_objects, input_data):

    for index, transaction in enumerate(import_objects):

        if transaction.type == "message":
            if input_data.get(str(index) + "_noted", None):
                transaction.description = True

        else:
            if str(index) + "_description" in input_data:
                transaction.description = input_data[str(index) + "_description"]
            if str(index) + "_category" in input_data:
                transaction.category_id = input_data[str(index) + "_category"]


def apply_account_id_changes(item_ids, account_id):

    for item_id in item_ids:
        session['import_items'][item_id]["account_id"] = int(account_id)


def apply_multiple_rule_match_edits(import_objects, input_data):

    item = import_objects[int(input_data["transaction_id"])]

    if input_data["rule_id"] == "NONE":
        item["rule_id"] = False
    else:
        item["rule_id"] = int(input_data["rule_id"])

    if len(input_data["description"]) > 0:
        item["description"] = input_data["description"]
    if "category" in input_data:
        item["category_id"] = int(input_data["category"])


def get_categories():
    categories = {}

    accounts = Account.query.all()

    for account in accounts:
        categories[account.id] = {}

        for type in ("in", "out"):

            categories[account.id][type] = []

            for category in account.categories(type):
                categories[account.id][type].append(category)

    return categories
