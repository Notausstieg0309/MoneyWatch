from flask import (
            Blueprint, flash, g, current_app, redirect, render_template, request, url_for
            )

from flask_babel import gettext

from moneywatch.utils.objects import db, Rule, Category, Account
import moneywatch.utils.functions as utils


bp = Blueprint('ruleset', __name__)


@bp.route('/<int:account_id>/ruleset/')
def index(account_id):
    """Show all the rules"""
    account = Account.query.filter_by(id=account_id).one()
    
    rules_in = account.rules_by_type("in")
    rules_out = account.rules_by_type("out")
     
    return render_template('ruleset/index.html', account = account, rules_in=rules_in, rules_out=rules_out)

           
@bp.route('/<int:account_id>/ruleset/add/<string:type>/', methods=('GET', 'POST'))
def add(account_id, type):

    account = Account.query.filter_by(id=account_id).one()
    
    if request.method == 'POST':
        error = None
        
        name = request.form['name'].strip()
        pattern = request.form['pattern']
        description = request.form['description'].strip()
        regular = request.form['regular']
        next_valuta = request.form.get('next_valuta', None)
        next_due = request.form.get('next_date', None)
        
        category_id = request.form.get('category_id', None)
        if not name:
            error = gettext('Rule name is required.')
            
        if not pattern:
            error = gettext('Search pattern is required.')
        if not "category_id" in request.form:
            error = gettext('Category is required.')

        if error is not None:
            flash(error)
               
        else:
            item = {}
            item["type"] = type
            item["name"] = name
            item["pattern"] = pattern
            item["description"] = description
            item["category_id"] = category_id
            item["regular"] = regular
            
            if next_valuta.strip() != "":
                item["next_valuta"] = next_valuta
            else:
                next_valuta = None
            if next_due.strip() != "":
                next_due = utils.get_date_from_string(next_due, "%Y-%m-%d")
            else:
                next_due = None
            
                
            new_rule = Rule(type=type, account_id = account.id, name=name, pattern=pattern, description=description, category_id=category_id, regular=regular, next_valuta=next_valuta, next_due=next_due)
            
            db.session.add(new_rule)
            db.session.commit()
            

       
            return redirect(url_for('ruleset.index', account_id = account.id))
            
    categories = account.categories(type)
    
    if not categories:
        flash(gettext("Unable to create new rules. No categories are available to create rules for. Please create categories first."))
        return redirect(url_for('ruleset.index', account_id = account.id))
        
    return render_template('ruleset/add.html',account=account, type=type, categories=categories)  

    
@bp.route('/ruleset/delete/<int:id>/')
def delete(id):
    
    Rule.query.filter_by(id=id).delete()
    db.session.commit()
    
    return redirect(url_for('ruleset.index'))

    
    
    
@bp.route('/ruleset/change/<int:id>/', methods=('GET', 'POST'))
def change(id):

    rule = Rule.query.filter_by(id=id).one()
    
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
            error = gettext('Name is required.')
        if not pattern:
            error = gettext('Search pattern is required.')
        if not category_id:
            error = gettext('Category is required.')

        if error is not None:
            flash(error)
        else:
            
            rule.name = name
            rule.pattern = pattern
            rule.description = description
            rule.category_id = category_id
            rule.regular = regular

            if regular == "1" or regular == "2":
                rule.next_due = utils.get_date_from_string(next_due,"%Y-%m-%d")
                rule.next_valuta = next_valuta
            else:
                rule.next_due = None
                rule.next_valuta = None
            
            db.session.commit()
            
            return redirect(url_for('ruleset.index', account_id=rule.account_id))
            
    categories=rule.account.categories(rule.type)
    
    return render_template('ruleset/change.html', rule = rule, categories=categories)  
