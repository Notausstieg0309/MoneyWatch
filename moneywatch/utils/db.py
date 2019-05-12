import sqlite3
import click
import datetime

from flask import current_app, g
from flask.cli import with_appcontext

import moneywatch.utils.functions as utils


#   _____                           _ 
#  / ____|                         | |
# | |  __  ___ _ __   ___ _ __ __ _| |
# | | |_ |/ _ \ '_ \ / _ \ '__/ _` | |
# | |__| |  __/ | | |  __/ | | (_| | |
#  \_____|\___|_| |_|\___|_|  \__,_|_|
#                                    
# ====================================

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

 
def convert_date_to_days(data, source, dest):
    if data is None:
        return
        
    if dest in data and isinstance(data[dest], (int, str)):
        return
    elif source in data and isinstance(data[source], datetime.date):
        data[dest] = utils.get_days_from_date(data[source])
        del data[source]
 
def convert_days_to_date(data, source, dest):
    if data is None:
        return
    
    if dest in data and isinstance(data[dest], datetime.date):
        return
    elif source in data and isinstance(data[source], (int, str)):
        data[dest] = utils.get_date_from_days(data[source])
        del data[source]
        
        
#   _____      _                        _           
#  / ____|    | |                      (_)          
# | |     __ _| |_ ___  __ _  ___  _ __ _  ___  ___ 
# | |    / _` | __/ _ \/ _` |/ _ \| '__| |/ _ \/ __|
# | |___| (_| | ||  __/ (_| | (_) | |  | |  __/\__ \
#  \_____\__,_|\__\___|\__, |\___/|_|  |_|\___||___/
#                       __/ |                       
# ==================== |___/ =======================     
    
def get_category(id):
    """Get a specific category by id.

    :param int id: numeric id of the rule
    :return: the complete category data as dict from database. If not exists, None will be returned
    :rtype: dict or None
    """
    
    current_app.logger.debug("requesting category from database by id '%s'", id)
    
    category = get_db().execute('SELECT * FROM categories WHERE id = ?', (id, )).fetchone()

    return category
 
def get_root_categories(type):
    """Get all root categories (categories with no parents)

    :param type: the type of the categories to query ("in" or "out") as string.
    :return: A list of categories as dict, that have no parents or None if no categories exist.
    :rtype: list(dict) or None
    """
    
    current_app.logger.debug("requesting root categories from database by type '%s'", type)
    
    categories = get_db().execute('SELECT * FROM categories WHERE type = ? AND parent IS NULL', (type,)).fetchall()
        
    return categories    

def get_all_categories(type=None):
    """Query all categories from database.

    :param str type: the category type as string ("in" or "out") 
    :return: a list of all categories as dict or None if no categories exist.
    :rtype: list(dict) or None
    """
    
    current_app.logger.debug("requesting all categories from database by type '%s'", type)
    
    categories = None
    if type is None:
        categories = get_db().execute('SELECT * FROM categories').fetchall()
    else:
        categories = get_db().execute('SELECT * FROM categories WHERE type = ?', (type,)).fetchall()

    return categories
 
 
def get_category_childs(type, id=None):
    """Query all child categories from database for a specific parent category id .

    :param int id: numeric id of the parent category or None to get all root categories
    :return: a list of all childs of the category as dicts
    :rtype: list(dict) or None
    """ 
    
    current_app.logger.debug("requesting child categories from database by type '%s' and id '%s'", type, id)
    
    if id is not None:
        return get_db().execute('SELECT * FROM categories WHERE parent = ? AND type = ?', (id,type)).fetchall()
    else:
        return get_root_categories(type)

        
def delete_category(id):
    """Deletes a category from the database by their numeric id.

    :param int id: numeric id of the category to be delete
    """ 
    
    current_app.logger.debug("delete category from database by id '%s'", id)
    
    db = get_db()
    db.execute('DELETE FROM categories WHERE id = ?', (id, ))
    db.commit()
    

  
def save_category(data):
    """Saves a category to the database.

    :param dict data: the category data as dict.
    """  
    
    current_app.logger.debug("save category to database: %s", data)
    
    db = get_db()
    
    if data.get("id",None) is not None:
        db.execute('UPDATE categories SET name = ?, budget_monthly = ?, parent = ? WHERE id = ?', (data["name"], data.get("budget_monthly",0), data.get("parent", None), data["id"]))
    
    else: # no id, so let's insert it as a new category
        db.execute('INSERT INTO categories (name, budget_monthly, parent,type) VALUES (?, ?, ? ,?)', (data["name"], data.get("budget_monthly",0), data.get("parent", None), data["type"]))
    
    db.commit()
    

#  _____       _           
# |  __ \     | |          
# | |__) |   _| | ___  ___ 
# |  _  / | | | |/ _ \/ __|
# | | \ \ |_| | |  __/\__ \
# |_|  \_\__,_|_|\___||___/
#
# =========================                           
    
def get_rule(id):
    """Get a specific rule by their numeric id.

    :param int id: numeric id of the rule
    :return: the complete rule data as a dict or None if the id does not exist.
    :rtype: dict or None
    """
    
    current_app.logger.debug("requesting rule from database by id '%s'", id)
    
    rule = get_db().execute('SELECT i.*, c.name as category_name FROM ruleset i JOIN categories c ON i.category_id = c.id WHERE i.id = ?', (id, )).fetchone()
    
    convert_days_to_date(rule, "next_days", "next_due")
    
    return rule
    
    
def get_rules_for_type(type):
    """Get all rules by type.

    :param str type: the type as string ("in" or "out").
    :return: a list of all rules of the given type as a list of dicts or None if no rules exist for the given type.
    :rtype: list(dict) or None
    """
    
    current_app.logger.debug("requesting rules from database by type '%s'", type)
    
    rules = get_db().execute('SELECT * FROM ruleset WHERE type=?', (type,)).fetchall()
    
    for rule in rules or []:
        convert_days_to_date(rule, "next_days", "next_due")
    
    return rules
    
def get_rules_for_category(category_id):
    """Get all rules that are configured for a specific category id

    :param int category_id: the category id as int
    :return: a list of all rules that are configured with the given category id as a list of dicts or None if no rules exist, that have this category id set.
    :rtype: list(dict) or None
    """

    current_app.logger.debug("requesting rules from database by category id '%s'", category_id)
        
    rules = get_db().execute('SELECT * FROM ruleset WHERE category_id = ?', (category_id,)).fetchall()
    
    for rule in rules or []:
        convert_days_to_date(rule, "next_days", "next_due")
        
    return rules
    
 
def save_rule(data):
    """Save a rule to the database

    :param dict data: the rule data as a dict
    """
    
    current_app.logger.debug("save rule to database: %s", data)
    
    db = get_db()
    
    convert_date_to_days(data, "next_due", "next_days")
    
    if data.get("id", None) is not None:
        db.execute('UPDATE ruleset SET name = ?, pattern = ?, description = ?, category_id = ?, regular = ?, next_days = ?, next_valuta = ? WHERE id = ? ',
                   (data["name"], data["pattern"], data["description"], data["category_id"], data["regular"], data.get("next_days", None), data.get("next_valuta", None), data["id"])
                  )
   
    else: # no id exist, so let's create a new rule
        db.execute('INSERT INTO ruleset (name, pattern, description, category_id, type, regular, next_valuta, next_days) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (data["name"], data["pattern"], data["description"], data["category_id"], data["type"], data["regular"], data.get("next_valuta", None), data.get("next_days", None))
                    )   
    db.commit()

 
def delete_rule(id):
    """Deletes a rule from the database by their numeric id.

    :param int id: numeric id of the rule to be delete
    """ 
    
    current_app.logger.debug("delete rule from database by id '%s'", id)  
    
    db = get_db()
    db.execute('DELETE FROM ruleset WHERE id = ?', (id, ))
    db.commit()
    
#  _______                             _   _                 
# |__   __|                           | | (_)                
#    | |_ __ __ _ _ __  ___  __ _  ___| |_ _  ___  _ __  ___ 
#    | | '__/ _` | '_ \/ __|/ _` |/ __| __| |/ _ \| '_ \/ __|
#    | | | | (_| | | | \__ \ (_| | (__| |_| | (_) | | | \__ \
#    |_|_|  \__,_|_| |_|___/\__,_|\___|\__|_|\___/|_| |_|___/
#   
# ===========================================================    

def get_transaction(id):
    """Get a specific transaction by id.

    :param id: id of the transaction
    :return: the data of the transaction as a dict or None if no transaction exists with this id.
    :rtype: dict or None
    """

    transaction = get_db().execute('SELECT * FROM transactions WHERE id = ?', (id, )).fetchone()
    
    convert_days_to_date(transaction, "days", "date")
    
    return transaction
    
def get_transactions(start=None, end=None):
    """Get all transaction from the database. Optionally filter within a specific start or/and end date.

    :param date start: a optional start date to get only transactions that are newer or equal to this date.
    :param date end: a optional end date to get only transactions that are older or equal to this date.
    :return: a list of all transactions that are available within the given timeframe as a list of dicts.
    :rtype: list(dict) or None
    """
    
    transactions = None
    
    if start is not None and end is not None:
        transactions = get_db().execute('SELECT * FROM transactions WHERE days >= ? AND days <= ? ORDER BY days ASC', (utils.get_days_from_date(start), utils.get_days_from_date(end))).fetchall()
    elif start is None and end is not None:
        transactions = get_db().execute('SELECT * FROM transactions WHERE days <= ? ORDER BY days ASC', (utils.get_days_from_date(end),)).fetchall()
    elif start is not None and end is None:
        transactions = get_db().execute('SELECT * FROM transactions WHERE  days >= ? ORDER BY days ASC', (utils.get_days_from_date(start),)).fetchall()
    else:
        transactions = get_db().execute('SELECT * FROM transactions ORDER BY days ASC').fetchall()

    for transaction in transactions or []:
        convert_days_to_date(transaction, "days", "date")
    
    return transactions


def get_latest_transaction():
    """Get the newest overall transaction from the database.

    :return: the data of the newest transaction as a dict or None if no transactions exist.
    :rtype: dict or None
    """
    
    transaction = get_db().execute('SELECT * FROM transactions ORDER BY id DESC').fetchone()
    
    convert_days_to_date(transaction, "days", "date")
    
    return transaction
  
def get_oldest_transaction():
    """Get the oldest overall transaction from the database.
    
    :return: the data of the newest transaction as a dict or None if no transactions exist.
    :rtype: dict or None
    """
    
    transaction = get_db().execute('SELECT * FROM transactions ORDER BY days ASC').fetchone()
    
    convert_days_to_date(transaction, "days", "date")
    
    return transaction  
    
def get_transaction_by_date_valuta(date, valuta):
    """Get a transaction with the same date and valuta.

    :param date date: the date to search for
    :param float valuta: the valuta to search for
    :return: a transaction as dict that matches the given date and valuta, otherwise None if no such transaction exist in the database.
    :rtype: dict or None
    """   
    
    db = get_db()
    
    transactions = db.execute('SELECT * FROM transactions WHERE days = ? AND valuta = ?', (utils.get_days_from_date(date), valuta)).fetchall()
    
    for transaction in transactions:
        convert_days_to_date(transaction, "days", "date")
    
    return transactions

 
def get_transactions_by_category(category_id, start=None, end=None):
    """Get all transaction for a specific category id from the database. Optionally filter within a specific start or/and end date.

    :param int category_id: a optional start date to get only transactions that are newer or equal to this date.
    :param date start: a optional start date to get only transactions that are newer or equal to this date.
    :param date end: a optional end date to get only transactions that are older or equal to this date.
    :return: a list of all transactions for the given category id that are available within the given timeframe as a list of dicts.
    :rtype: list(dict) or None
    """   
    
    transactions = None
    
    if start is not None and end is not None:
        transactions = get_db().execute('SELECT * FROM transactions WHERE category_id = ? AND days >= ? AND days <= ? ORDER BY days ASC', (category_id, utils.get_days_from_date(start), utils.get_days_from_date(end))).fetchall()
    elif start is None and end is not None:
        transactions = get_db().execute('SELECT * FROM transactions WHERE category_id = ? AND days <= ? ORDER BY days ASC', (category_id, utils.get_days_from_date(end))).fetchall()
    elif start is not None and end is None:
        transactions = get_db().execute('SELECT * FROM transactions WHERE category_id = ? AND days >= ? ORDER BY days ASC' , (category_id, utils.get_days_from_date(start))).fetchall()
    else:
        transactions = get_db().execute('SELECT * FROM transactions WHERE category_id = ? ORDER BY days ASC', (category_id, )).fetchall()
    
    for transaction in transactions or []:
        convert_days_to_date(transaction, "days", "date")
    
    return transactions    

def get_transactions_by_rule(rule_id, start=None, end=None, limit=None):
    """Get all transaction that are matched by a specific rule id from the database. Optionally filter within a specific start or/and end date.

    :param int rule_id: the rule id based on the transactions should be filtered.
    :param date start: a optional start date to get only transactions that are newer or equal to this date.
    :param date end: a optional end date to get only transactions that are older or equal to this date.
    :return: a list of all transactions for the given category id that are available within the given timeframe as a list of dicts.
    :rtype: list(dict) or None
    """   
    
    transactions = None
	
    limit = ("LIMIT %d" % limit) if limit is not None else ""
	
    if start is not None and end is not None:
        transactions = get_db().execute('SELECT * FROM transactions WHERE rule_id = ? AND days >= ? AND days <= ? ORDER BY days ASC %s' % limit, (rule_id, utils.get_days_from_date(start), utils.get_days_from_date(end))).fetchall()
    elif start is None and end is not None:
        transactions = get_db().execute('SELECT * FROM transactions WHERE rule_id = ? AND days <= ? ORDER BY days ASC %s' % limit, (rule_id, utils.get_days_from_date(end))).fetchall()
    elif start is not None and end is None:
        transactions = get_db().execute(("SELECT * FROM transactions WHERE rule_id = ? AND days >= ? ORDER BY days ASC %s" % limit), (rule_id, utils.get_days_from_date(start))).fetchall()
    else:
        transactions = get_db().execute('SELECT * FROM transactions WHERE rule_id = ? ORDER BY days ASC %s' % limit, (rule_id, )).fetchall()
    
    for transaction in transactions or []:
        convert_days_to_date(transaction, "days", "date")
    
    return transactions 	
	
def get_transactions_by_rule_reversed(rule_id, start=None, end=None, limit=None):
    """Get all transaction that are matched by a specific rule id from the database. Optionally filter within a specific start or/and end date.

    :param int rule_id: the rule id based on the transactions should be filtered.
    :param date start: a optional start date to get only transactions that are newer or equal to this date.
    :param date end: a optional end date to get only transactions that are older or equal to this date.
    :return: a list of all transactions for the given category id that are available within the given timeframe as a list of dicts.
    :rtype: list(dict) or None
    """   
    
    transactions = None
	
    limit = ("LIMIT %d" % limit) if limit is not None else ""
	
    if start is not None and end is not None:
        transactions = get_db().execute('SELECT * FROM (SELECT * FROM transactions WHERE rule_id = ? AND days >= ? AND days <= ? ORDER BY days DESC %s) ORDER BY days ASC' % limit, (rule_id, utils.get_days_from_date(start), utils.get_days_from_date(end))).fetchall()
    elif start is None and end is not None:
        transactions = get_db().execute('SELECT * FROM (SELECT * FROM transactions WHERE rule_id = ? AND days <= ? ORDER BY days DESC %s) ORDER BY days ASC' % limit, (rule_id, utils.get_days_from_date(end))).fetchall()
    elif start is not None and end is None:
        transactions = get_db().execute('SELECT * FROM (SELECT * FROM transactions WHERE rule_id = ? AND days >= ? ORDER BY days DESC %s) ORDER BY days ASC' % limit, (rule_id, utils.get_days_from_date(start))).fetchall()
    else:
        transactions = get_db().execute('SELECT * FROM (SELECT * FROM transactions WHERE rule_id = ? ORDER BY days DESC %s) ORDER BY days ASC' % limit, (rule_id, )).fetchall()
    
    for transaction in transactions or []:
        convert_days_to_date(transaction, "days", "date")
    
    return transactions 
    
def get_last_transaction_by_rule(rule_id, end=None):
    """Get the latest transaction for a specific rule id from the database.
    :param int rule_id: the rule id to get the latest transaction for.
    :param date end: a optional end date to get only the latest transactions before this date.
    :return: the data of the newest transaction as a dict or None if no transaction can be found.
    :rtype: dict or None
    """
    
    transaction = None
    
    if end is not None:
        transaction = get_db().execute('SELECT * FROM transactions WHERE rule_id = ? AND days < ? ORDER BY days DESC LIMIT 1', (rule_id, utils.get_days_from_date(end) )).fetchone()
    else:
        transaction = get_db().execute('SELECT * FROM transactions WHERE rule_id = ? ORDER BY days DESC LIMIT 1', (rule_id, )).fetchone()

    convert_days_to_date(transaction, "days", "date")
        
    return transaction  
    

    
def save_transaction(item):
    """Save a transaction to the database

    :param dict data: the rule data as a dict
    """
    
    db = get_db()
    
    convert_date_to_days(item, "date", "days")
    
    if item.get("id", None):
        db.execute('UPDATE transactions SET description = ?, category_id = ?, trend = ?, trend_calculated = ? WHERE id = ? ', (item["description"], item["category_id"], item["trend"], item["trend_calculated"], item["id"]))
    else: # no id exist, so let's create a new transaction
        db.execute("INSERT INTO transactions (days, valuta, full_text, description, category_id, rule_id) VALUES (?, ?, ? ,? , ?, ?)",(item['days'] ,item['valuta'], item['full_text'], item['description'], item['category_id'], item.get('rule_id', None)))
    
    db.commit()