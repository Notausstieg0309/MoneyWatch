from flask import (Blueprint, flash, redirect, render_template, request, url_for)

from flask_babel import gettext

from moneywatch.utils.objects import db, Category, Account

bp = Blueprint('categories', __name__)


@bp.route('/<int:account_id>/categories/')
def index(account_id):
    """Show all the rules"""

    account = Account.query.filter_by(id=account_id).one()

    categories_in = account.categories("in")
    categories_out = account.categories("out")

    return render_template('categories/index.html', account=account, categories_in=categories_in, categories_out=categories_out)


@bp.route('/<int:account_id>/categories/add/<string:type>/', methods=('GET', 'POST'))
def add(account_id, type):

    parent = None
    path = None
    account = Account.query.filter_by(id=account_id).one()

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
            if db.session.query(Category.id).filter_by(name=name, parent_id=parent).scalar() is not None:
                error = gettext("The name '%(name)s' already exists on this level", name=name)

        if error is not None:
            flash(error)
        else:
            if "budget_monthly" in request.form:
                budget_monthly = request.form['budget_monthly']

            if not budget_monthly:
                budget_monthly = None

            item = {}
            item["type"] = type
            item["name"] = name
            item["parent"] = parent
            item["budget_monthly"] = budget_monthly

            new_category = Category(type=type, account_id=account.id, name=name, parent_id=parent, budget_monthly=budget_monthly)
            db.session.add(new_category)
            db.session.commit()


            return redirect(url_for('categories.index', account_id=account.id))

    return render_template('categories/add.html', type=type, parent=parent, path=path)


@bp.route('/categories/delete/<int:id>/')
def delete(id):

    account_id = Category.query.filter_by(id=id).one().account_id

    Category.query.filter_by(id=id).delete()
    db.session.commit()

    return redirect(url_for('categories.index', account_id=account_id))


@bp.route('/categories/change/<string:type>/<int:id>/', methods=('GET', 'POST'))
def change(type, id):

    current_category = Category.query.filter_by(id=id, type=type).one()

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
            budget_monthly = None

        if not name:
            error = gettext('Name is required.')

        if budget_monthly and not budget_monthly.isdigit():
            error = gettext('The budget must be given as numeric value.')

        if current_category.name != name and current_category.has_sibling_name(name):
            error = gettext("The name '%(name)s' already exists on this level", name=name)

        if error is not None:
            flash(error)
        else:
            current_category.name = name
            current_category.budget_monthly = budget_monthly
            current_category.parent_id = parent

            db.session.commit()

            return redirect(url_for('categories.index', account_id=current_category.account_id))

    categories = current_category.account.categories(type)

    return render_template('categories/change.html', type=type, category=current_category, categories=categories)
