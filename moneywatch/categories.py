from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)

from flask_babel import gettext

from moneywatch.utils.objects import Category

bp = Blueprint('categories', __name__)


@bp.route('/categories/')
def index():
    """Show all the rules"""

    categories_in = Category.getRootCategories("in")
    categories_out = Category.getRootCategories("out")

    return render_template('categories/index.html', categories_in=categories_in, categories_out=categories_out)


@bp.route('/categories/add/<string:type>/', methods=('GET', 'POST'))
def add(type):

    parent = None 
    path = None
    
    if "parent" in request.args:
        parent = request.args["parent"]
        
    if request.method == 'POST':
        error = None
        name = request.form['name']
        budget_monthly = 0
        
        if not name:
            error = gettext('Name is required.')
            
        if isinstance(budget_monthly, str) and not budget_monthly.isdigit():
            error = gettext('The budget must be given as numeric value.')
            
        if parent:
            if Category(parent).child_name_exists(name):
                error = gettext("The name '%{name}s' already exists on this level", name=name)
                    
        if error is not None:
            flash(error)
        else:
            if "budget_monthly" in request.form:
                budget_monthly = request.form['budget_monthly']
                
            if not budget_monthly:
                budget_monthly = 0
            
            item = {}
            item["type"] = type
            item["name"] = name
            item["parent"] = parent
            item["budget_monthly"] = budget_monthly
            
            new_category = Category(item)
            new_category.save()

            return redirect(url_for('categories.index'))
  
    return render_template('categories/add.html', type=type, parent=parent, path = path)  
    
@bp.route('/categories/delete/<int:id>/') 
def delete(id):

    item = Category(id)
    
    item.delete()
   
    return redirect(url_for('categories.index'))
    
    
@bp.route('/categories/change/<string:type>/<int:id>/', methods=('GET', 'POST')) 
def change(type, id):
    
    current_category = Category(id)
    
    if request.method == 'POST':
        error = None
        
        name = request.form['name'].strip()
        parent = request.form['parent']
        
        budget_monthly = 0
        
        if "budget_monthly" in request.form:
            budget_monthly = request.form['budget_monthly']
            
        if "parent" in request.form:
            parent = request.form['parent']

        if parent == "0":
            parent = None
        
        if not budget_monthly:
            budget_monthly = 0
            
        if not name:
            error = gettext('Name is required.')
            
        if budget_monthly and not budget_monthly.isdigit():
            error = gettext('The budget must be given as numeric value.')

        if current_category.name != name and current_category.sibling_name_exists(name):
            error = gettext("The name '%{name}s' already exists on this level", name=name)
                
        if error is not None:
            flash(error)
        else:
            current_category.name = name
            current_category.budget_monthly = budget_monthly
            current_category.parent_id = parent
            
            current_category.save()
            
            return redirect(url_for('categories.index'))
            
    categories=Category.getRootCategories(type)

    return render_template('categories/change.html', type=type, category=current_category, categories=categories)  
    
    

    


