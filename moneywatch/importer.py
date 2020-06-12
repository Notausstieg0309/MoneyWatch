from flask import (Blueprint, flash, g, redirect, render_template, request, url_for, session, current_app)

import re
import os

import moneywatch.utils.functions as utils

import datetime

from flask_babel import gettext

from moneywatch.utils.objects import db, Rule,Category, Transaction, Account
from moneywatch.utils.plugins import ImportPluginsManager
from moneywatch.utils.exceptions import *

bp = Blueprint('import', __name__)
plugins = ImportPluginsManager(os.path.dirname(os.path.realpath(__file__))+"/import_plugins")

 
@bp.route('/import/', methods=('GET', 'POST'))
def index():
 
   
    if request.method == 'POST':
        error = None
        
        if not "file" in request.files and not "import_objects" in session and not "import_items" in session:
            error = gettext("No file uploaded")

        if error is not None:
            flash(error)
        else:
        
            if "file" in request.files:
            
                available_plugins = plugins.resolve_plugins_for_file(request.files['file'])
                
                session.pop("import_objects", None)
                
                if len(available_plugins) > 0:
                    
                    if len(available_plugins) == 1:
                        items = plugins.parse_file(request.files['file'], available_plugins[0][0])
                        session['import_items'] = items
                        session['import_objects'] = create_transactions_from_import(items)

                    else:
                        raise MultiplePluginMatchError(request.files['file'], available_plugins)
                    
                else:
                    raise NoPluginMatchError(request.files['file'])
                
               
                
            if "import_items" in session and "import_objects" not in session:
                
                # apply rule id for transactions that raised an MultipleRuleMatchError exception
                if "multiple_rule_match" in session:
                    apply_multiple_rule_match_edits(session['import_items'], request.form)
                    session.pop("multiple_rule_match", None)
                
                # apply account id for transactions that raised an ItemsWithoutAccountError exception
                elif "no_account_given" in session and "account_id" in request.form:
                    item_ids = session["no_account_given"]
                    
                    for item_id in item_ids:
                        session['import_items'][item_id]["account_id"] = int(request.form["account_id"])
                        
                    session.pop("no_account_given", None)
                    
                
                session['import_objects'] = create_transactions_from_import(session['import_items'])
                session.modified = True
                
            elif "import_objects" in session:
                apply_import_edits(session['import_objects'], request.form)
                session.modified = True

            if request.form['action'] == "save":
            
                # reverse transaction list to get oldest transaction first instead of newest transaction first
                session['import_objects'].reverse()
                
                valutas = {}
                
                
                for transaction in session['import_objects']:
                    
                    if not transaction.account_id in valutas:
                        valutas[transaction.account_id] = 0
                        
                    valutas[transaction.account_id] += transaction.valuta
                    
                    db.session.add(transaction)
                 
                for account_id, valuta in valutas.items():
                    account = Account.query.filter_by(id=account_id).one()
                    account.balance = round(account.balance + valuta, 2)
                    
                db.session.commit()
                
                session.pop("import_objects", None)
                session.pop("import_items", None)
                
                if len(valutas.keys()) == 1:
                    return redirect(url_for('overview.overview', account_id = (list(valutas.keys()))[0] )) 

                return redirect(url_for('overview.index'))

            categories = {}
    
            if len(session.get("import_objects",[] )) > 0:
                categories = get_categories()
                    
            return render_template('importer/check.html', data=(session.get("import_objects",[] )), complete=check_if_items_complete(session.get("import_objects",[] )), categories = categories)  
             
    return render_template('importer/index.html', extensions = plugins.get_possible_file_extensions())  
    
    
@bp.errorhandler(MultipleRuleMatchError)
def handle_multiple_rule_match(error):
    current_app.logger.debug("transaction: %s" , error.transaction)

    session["multiple_rule_match"] = error.transaction.id
    
    if error.transaction.valuta < 0:
        categories = get_categories()[error.transaction.account_id]["out"]
    else:
        categories = get_categories()[error.transaction.account_id]["in"]
        
    return render_template('importer/multiple_rule_match.html', transaction = error.transaction, rules = error.rules, index = error.index, categories = categories)  


@bp.errorhandler(ItemsWithoutAccountError)
def handle_no_account_given(error):
    current_app.logger.debug("index list: %s" , error.index_list)
    
    session["no_account_given"] = error.index_list
    
    accounts = Account.query.all()
        
    return render_template('importer/no_account_given.html', accounts = accounts, count_items = len(error.index_list))  


def create_transactions_from_import(items, check_all=False):
   
    
    result = []
    
    accounts = {}
    
    # the account id of the latest already imported transaction of the given file
    latest_transaction_account_id = None
    
    # list of item ids which have no account iban
    item_ids_iban_missing = []
    
    for item in items:
        try:
            if "account" in item:
               
                if not item["account"] in accounts:
                    iban = utils.normalize_iban(item["account"])
                    account = Account.query.filter_by(iban=iban).one_or_none()
                    if account is not None:
                        accounts[item["account"]] = account.id
                    else:
                        raise UnknownAccountError(iban)
                        
                item["account_id"] = accounts[item["account"]]
                item.pop("account", None)   
            else:
                account_missing = True
   
               
            trans = Transaction(**item)
            exist = trans.exist
            
            # if a transaction of the given file already exists, save the account_id to use it for items, that don't have a account iban provided by the import plugin.
            if latest_transaction_account_id is None and not "account" in item and exist:
                latest_transaction_account_id = trans.account_id
            
            if exist and not check_all:
                break
                
            if exist and check_all:
                continue    
                
            if trans.account_id:
                trans.check_rule_matching()
            else:
                item_ids_iban_missing.append(items.index(item))
            
            result.append(trans)
        except MultipleRuleMatchError as e:
            raise MultipleRuleMatchError(e.transaction, e.rules, items.index(item))
    
    if latest_transaction_account_id is not None:
        for item in result:
            if item.account_id is None:
                item.account_id = latest_transaction_account_id
                item.check_rule_matching()
                
    elif len(item_ids_iban_missing) > 0:       
        raise ItemsWithoutAccountError(item_ids_iban_missing)
        
                
    return result

    
def check_if_items_complete(items):
    
    for item in items:
        if not item.complete:
            return False
        
    return True
    
    
def apply_import_edits(import_objects,input_data):

    for index, transaction in enumerate(import_objects):
       
        if transaction.type == "message":
            current_app.logger.debug("message noted: %s" ,input_data)
            if input_data.get(str(index)+"_noted", None):
                transaction.description = True
        
        else:
            if str(index)+"_description" in input_data:
                transaction.description = input_data[str(index)+"_description"]
            if str(index)+"_category" in input_data:
                transaction.category_id = input_data[str(index)+"_category"]


def apply_multiple_rule_match_edits(import_objects,input_data):

    item = import_objects[int(input_data["transaction_id"])]
    
    if input_data["rule_id"] == "NONE":
        item["rule_id"] = False
    else:
        item["rule_id"] = int(input_data["rule_id"])
        
    if len(input_data["description"]) > 0:
        item["description"] = input_data["description"]   
    if "category_id" in input_data:
        item["category_id"] = int(input_data["category_id"])
             
def get_categories():
    categories = {}  

    accounts = Account.query.all()
    
    for account in accounts:
        categories[account.id] = {}
        
        for type in ("in", "out"):

            categories[account.id][type] = []

            for category in account.categories(type):
                categories[account.id][type].extend(category.getCategoryIdsAndPaths(" > "))
                
    return categories

