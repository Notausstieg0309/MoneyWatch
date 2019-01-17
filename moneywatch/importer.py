from flask import (Blueprint, flash, g, redirect, render_template, request, url_for, session, current_app)

import re
import os

import moneywatch.utils.functions as utils

import datetime

from flask_babel import gettext

from moneywatch.utils.objects import Rule,Category, Transaction
from moneywatch.utils.plugins import ImportPluginsManager
from moneywatch.utils.exceptions import *

bp = Blueprint('import', __name__)
plugins = ImportPluginsManager(os.path.dirname(os.path.realpath(__file__))+"/import_plugins")

 
@bp.route('/import/', methods=('GET', 'POST'))
def index():
 
   
    if request.method == 'POST':
        error = None
        
        if not "file" in request.files and not "import_data" in session:
            error = gettext("No file uploaded")

        if error is not None:
            flash(error)
        else:
        
            if "file" in request.files:
            
                available_plugins = plugins.resolve_plugins_for_file(request.files['file'])
                session.clear()
                if len(available_plugins) > 0:
                    
                    if len(available_plugins) == 1:
                        items = plugins.parse_file(request.files['file'], available_plugins[0][0])
                        session['import_data'] = create_transactions_from_import(items)

                    else:
                        raise MultiplePluginMatchError(request.files['file'], available_plugins)
                    
                else:
                    raise NoPluginMatchError(request.files['file'])
                

            categories = {}
            
            if len(session.get("import_data",[] )) > 0:
                for type in ("in", "out"):

                    categories[type] = []

                    for category in Category.getRootCategories(type, transactions=False):
                        categories[type].extend(category.getCategoryIdsAndPaths(" > "))

            
            if request.form:
                apply_import_edits(session.get("import_data",[] ), request.form)

                session.modified = True

                if request.form['action'] == "save":
                
                    for transaction in session['import_data']:
                        transaction.save()
                        
                    session.clear()
                    return redirect(url_for('overview.index'))
            

            return render_template('importer/check.html', data=(session.get("import_data",[] )), complete=check_if_items_complete(session.get("import_data",[] )), categories=categories)  
            
        
    return render_template('importer/index.html', extensions = plugins.get_possible_file_extensions())  
    

def create_transactions_from_import(items, check_all=False):
    
    result = []
    
    for item in items:
        trans = Transaction(item)
        exist = trans.exist
        
        if exist and not check_all:
            break
            
        if exist and check_all:
            continue    
            
        result.append(trans)
        
    return result

    
def check_if_items_complete(items):
    
    incomplete = False
    for item in items:
        if not(item.description) or not(item.category_id):
            incomplete = True
            break
            
    return not(incomplete)
    
    
def apply_import_edits(import_data,input_data):

    for index, transaction in enumerate(import_data):
       
        if str(index)+"_description" in input_data:
            transaction.description = input_data[str(index)+"_description"]
        if str(index)+"_category" in input_data:
            transaction.category_id = input_data[str(index)+"_category"]
            
  