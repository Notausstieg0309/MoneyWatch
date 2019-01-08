import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
import moneywatch.utils.functions as utils

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
                
        g.db.row_factory = dict_factory

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))

        
        
        
@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('initialized database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    
    
    
def get_category(id):
    """Get a specific category by id.

    :param id: id of the rule
    :return: the complete category from database.
    :rause 404: if a rule with the given id does not exist
    """

    category = get_db().execute('SELECT * FROM categories  WHERE id = ?', (id, )).fetchone()

    if not category:
        abort(404, "category id {0} does not exist.".format(id))

    return category
 
def get_root_categories(type):
    """Get a specific category by id.

    :param id: id of the rule
    :return: the complete category from database.
    :rause 404: if a rule with the given id does not exist
    """

    categories = get_db().execute('SELECT * FROM categories WHERE type = ? AND parent IS NULL', (type,)).fetchall()

    if not categories:
        categories = None
        
    return categories    

def get_all_categories(type=None):
    """Get a specific category by id.

    :param id: id of the rule
    :return: the complete category from database.
    :rause 404: if a rule with the given id does not exist
    """
    
    categories = None
    if type is None:
        categories = get_db().execute('SELECT * FROM categories').fetchall()
    else:
        categories = get_db().execute('SELECT * FROM categories WHERE type = ?', (type,)).fetchall()

    return categories
 
 
def get_category_childs(type, id=None):
    
    if id:
        return get_db().execute('SELECT * FROM categories WHERE parent = ? AND type = ?', (id,type)).fetchall()
    else:
        return get_root_categories(type)

def delete_category(data):

    db = get_db()
    db.execute('DELETE FROM categories WHERE id = ?', (data["id"], ))
    db.commit()
    

def save_category(data):
    db = get_db()
    
    if data.get("id",None):
        db.execute('UPDATE categories SET name = ?, budget_monthly = ?, parent = ? WHERE id = ?', (data["name"], data.get("budget_monthly",None), data.get("parent", None), data["id"]))
    
    else:
        db.execute('INSERT INTO categories (name, budget_monthly, parent,type) VALUES (?, ?, ? ,?)', (data["name"], data.get("budget_monthly",None), data.get("parent", None), data["type"]))
    
    db.commit()
    

    
    
def get_rule(rule_id):
    """Get a specific rule by id.

    :param id: id of the rule
    :return: the complete rule.
    :rause 404: if a rule with the given id does not exist
    """

    rule = get_db().execute('SELECT i.*, c.name as category_name FROM ruleset i JOIN categories c ON i.category_id = c.id WHERE i.id = ?', (rule_id, )).fetchone()

    return rule
    
    
def get_rules_for_type(type):
    """Get a specific rule by id.

    :param id: id of the rule
    :return: the complete rule.
    :rause 404: if a rule with the given id does not exist
    """

    rules = get_db().execute('SELECT * FROM ruleset WHERE type=?', (type,)).fetchall()

    return rules
    
def get_rules_for_category(category):
    """Get a specific rule by id.

    :param id: id of the rule
    :return: the complete rule.
    :rause 404: if a rule with the given id does not exist
    """

    rules = get_db().execute('SELECT * FROM ruleset WHERE category_id = ?', (category,)).fetchall()

    return rules
    
 
def save_rule(data):

    db = get_db()
    if data.get("id", None):
        db.execute('UPDATE ruleset SET name = ?, pattern = ?, description = ?, category_id = ?, regular = ?, next_days = ?, next_valuta = ? WHERE id = ? ', (data["name"], data["pattern"], data["description"], data["category_id"], data["regular"], utils.get_days_from_date(data["next_due"]), data["next_valuta"], data["id"]))
    else:
        db.execute('INSERT INTO ruleset (name, pattern, description, category_id, type, regular, next_valuta, next_days) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (data["name"], data["pattern"], data["description"], data["category_id"], data["type"], data["regular"], data["next_valuta"], utils.get_days_from_date(data.get("next_due", None)))
            )   
    db.commit()

 
def delete_rule(data):
    db = get_db()
    db.execute('DELETE FROM ruleset WHERE id = ?', (data["id"], ))
    db.commit()
    

def get_transactions(start=None, end=None):

    transactions = None
    
    if start is not None and end is not None:
        transactions = get_db().execute('SELECT * FROM transactions WHERE days >= ? AND days <= ? ORDER BY days ASC', (utils.get_days_from_date(start), utils.get_days_from_date(end))).fetchall()
    elif start is None and end is not None:
        transactions = get_db().execute('SELECT * FROM transactions WHERE days <= ? ORDER BY days ASC', (utils.get_days_from_date(end),)).fetchall()
    elif start is not None and end is None:
        transactions = get_db().execute('SELECT * FROM transactions WHERE  days >= ? ORDER BY days ASC', (utils.get_days_from_date(start),)).fetchall()
    else:
        transactions = get_db().execute('SELECT * FROM transactions ORDER BY days ASC').fetchall()
    
    return transactions


def get_latest_transaction():
    """Get a specific rule by id.

    :param id: id of the rule
    :return: the complete rule.
    :rause 404: if a rule with the given id does not exist
    """

    transaction = get_db().execute('SELECT * FROM transactions ORDER BY id DESC').fetchone()

    return transaction
  
def get_oldest_transaction():
    """Get a specific rule by id.

    :param id: id of the rule
    :return: the complete rule.
    :rause 404: if a rule with the given id does not exist
    """

    transaction = get_db().execute('SELECT * FROM transactions ORDER BY days ASC').fetchone()

    return transaction  
    
def get_transaction_by_date_valuta(date, valuta):
    
    db = get_db()
    
    transaction = db.execute('SELECT * FROM transactions WHERE days = ? AND valuta = ?', (utils.get_days_from_date(date), valuta)).fetchone()
    
    return transaction

 
def get_transactions_by_category(id, start=None, end=None):
    """Get a specific rule by id.

    :param id: id of the rule
    :return: the complete rule.
    :rause 404: if a rule with the given id does not exist
    """
    transactions = None
    
    if start is not None and end is not None:
        transactions = get_db().execute('SELECT * FROM transactions WHERE category_id = ? AND days >= ? AND days <= ? ORDER BY days ASC', (id,start, end)).fetchall()
    elif start is None and end is not None:
        transactions = get_db().execute('SELECT * FROM transactions WHERE category_id = ? AND days <= ? ORDER BY days ASC', (id, end)).fetchall()
    elif start is not None and end is None:
        transactions = get_db().execute('SELECT * FROM transactions WHERE category_id = ? AND days >= ? ORDER BY days ASC' , (id, start)).fetchall()
    else:
        transactions = get_db().execute('SELECT * FROM transactions WHERE category_id = ? ORDER BY days ASC', (id, )).fetchall()

    if transactions is None:
        abort(404, gettext("transactions for category id %(id)d does not exist.", id=id))

    return transactions    
	
def get_transactions_by_rule(id, start=None, end=None):
    """Get all transactions for a specific rule id.

    :param id: id of the rule
    :return: the complete rule.
    :rause 404: if a rule with the given id does not exist
    """
    transactions = None
    
    if start is not None and end is not None:
        transactions = get_db().execute('SELECT * FROM transactions WHERE rule_id = ? AND days >= ? AND days <= ? ORDER BY days DESC', (id,start, end)).fetchall()
    elif start is None and end is not None:
        transactions = get_db().execute('SELECT * FROM transactions WHERE rule_id = ? AND days <= ? ORDER BY days DESC', (id, end)).fetchall()
    elif start is not None and end is None:
        transactions = get_db().execute('SELECT * FROM transactions WHERE rule_id = ? AND days >= ? ORDER BY days DESC' , (id, start)).fetchall()
    else:
        transactions = get_db().execute('SELECT * FROM transactions WHERE rule_id = ? ORDER BY days DESC', (id, )).fetchall()

    if transactions is None:
        abort(404, gettext("transactions for category id %(id)d does not exist.", id=id))

    return transactions    
def get_last_transaction_by_rule(id, end=None):

    """Get all transactions for a specific rule id.

    :param id: id of the rule
    :return: the complete rule.
    :rause 404: if a rule with the given id does not exist
    """
    transaction = None
    
    if end is not None:
        transaction = get_db().execute('SELECT * FROM transactions WHERE rule_id = ? AND days < ? ORDER BY days DESC LIMIT 1', (id, utils.get_days_from_date(end) )).fetchone()
    else:
        transaction = get_db().execute('SELECT * FROM transactions WHERE rule_id = ? ORDER BY days DESC LIMIT 1', (id, )).fetchone()

    return transaction    		
def save_transaction(item):

    db = get_db()

    if item.get("id", None):
        db.execute('UPDATE transactions SET description = ?, category_id = ?, trend = ?, trend_calculated = ? WHERE id = ? ', (item["description"], item["category_id"], item["trend"], item["trend_calculated"], item["id"]))
    else:
        db.execute("INSERT INTO transactions (days, valuta, full_text, description, category_id, rule_id) VALUES (?, ?, ? ,? , ?, ?)",(utils.get_days_from_date(item['date']) ,item['valuta'], item['full_text'], item['description'], item['category_id'], item.get('rule_id', None)))
    db.commit()


    
   