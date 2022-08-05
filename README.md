# MoneyWatch

MoneyWatch is a lightweight web application helps you to monitor your bank account about performed and planned transactions. It helps you to track your earnings/spendings and gives you indication of your current and planned balance.

You can import your transactions via file import. Currently supported file formats are:
* Targobank CSV
* ING.de CSV

The supported file formats can be easily extended by implementing an own [import plugin](/src/moneywatch/import_plugins).

Currently the following translations are available:
* English (default)
* German

It is written in [Python 3](https://www.python.org/) and based on [Flask](http://flask.pocoo.org/). It is licensed under [MIT License](/LICENSE)

## Overview

MoneyWatch gives you a quick overview about your overall financial status.

![Screenshot of main overview](screenshots/index.png?raw=true "Screenshot of main overview")

It tracks for each account the planned and already performed transactions.

![Screenshot of account overview](screenshots/overview.png?raw=true "Screenshot of account overview")

The overview shows you what are the maximum planned deposits and withdrawals (using all your planned budgets) and shows your current account status.

![](screenshots/balance.png?raw=true "Balance table screenshot")

To get an idea how the net change would look like when all planned transactions would be done, click on the "Current" column to see the net change including all pending transactions.

![](screenshots/balance_link.png?raw=true "Link to switch current balance view")

![](screenshots/balance_clicked.png?raw=true "Balance view including all pending transactions valutas")

Each category indicates planned transactions (formatted as gray italic transaction) based on defined rules for regular transactions.

![](screenshots/planned_transaction.png?raw=true "Planned transactions")

Categories, which have assigned a maximum planned budget, displays a budget indicator in the title bar indicating the percentual amount of already used budget for all underlying transactions.

![](screenshots/budget_indicator.png?raw=true "Budget indicator for categories with a maximum planned amount for spendings.")

Regular transactions can be identified by import rules. For regular transaction, that have always (or sometimes) a varying booking value, the trend indicator (little arrow) shows the difference compared to the original planned value.

![](screenshots/trend_indicator.png?raw=true "Planned transactions")

You can examine the overall history of a regular transaction by showing a historical chart, which shows all values since the last 12 months.

![](screenshots/historical_link.png?raw=true "Link to the historical transaction data")

![](screenshots/historical_chart.png?raw=true "The historical chart of transaction data over the last 12 months")

Regular transactions are expected to be booked on a specific date (based on the last transaction date). When an expected transaction is not booked on that day, you see an overdue indicator (warning sign) for the transaction and all contained categories.

![](screenshots/overdue.png?raw=true "The overdue indicator.")

Depending on your bank, your account statement can contain important messages, during import you must acknowledge these messages.

![](screenshots/messages_import.png?raw=true "Acknowledge of messages during import")

In the overview you can see, that the current month contains messages due to the message indication.

![](screenshots/messages_button.png?raw=true "Indication for messages that were imported for the current month")

You can view these message by clicking on the indication.

![](screenshots/messages_modal.png?raw=true "List of messages")

All regular transactions that are not planned every month (quarterly/semiannual/annual transactions) will be shown in particular when they are due for current month.

![](screenshots/particular_transactions.png?raw=true "Particular transactions")

## Transactions

You can list all transactions and search for particular transactions.

![](screenshots/transactions.png?raw=true "List of all transactions.")

## Categories

Transactions needed to be categorized. You can create categories with more subcategories. For spending categories, you can define a monthly budget which will be used to calculate the overall monthly spendings.

![Screenshot of categories](screenshots/categories.png?raw=true "Screenshot of categories")

## Ruleset

You can define rules, that are used to match transactions during import and assign these transactions automatically to a category and provide a default short description.

A rule has a search pattern defined, which will be checked against the full booking text of a transaction to identify matching transactions. A rule can define if transactions will happen on a regular basis (monthly, quartly, half-year or every year). Based on this MoneyWatch calculate planned transactions for the future

![Screenshot of ruleset](screenshots/ruleset.png?raw=true "Screenshot of ruleset")
![Screenshot of rule edit view](screenshots/rule_edit.png?raw=true "Screenshot of rule edit viewt")

## Importing transactions

Transactions can be imported using a file based import. During import, the transaction will be checked against the defined ruleset to automatically identify and assign transactions to specific categories and provide a initial short description. The assignment and short descriptions can be overwritten during import.

Transactions, which are not covered by any rule, must be assigned manually.

![Screenshot of file upload](screenshots/import_fileupload.png?raw=true "Screenshot of file upload")
![Screenshot of transaction import](screenshots/imports.png?raw=true "Screenshot of importing new transactions")

If a found transaction is not covered by a rule, you can easily create a rule based on the imported transaction by clicking on "Create Rule".

![Screenshot of 'Create Rule' button during import](screenshots/import_create_rule.png?raw=true "Screenshot of 'Create Rule' button during import")

You can then enter the rule name and the search pattern based on the related transaction details shown above.

![Screenshot of creating a rule during import](screenshots/import_save_rule.png?raw=true "Screenshot of creating a rule during import")

After saving the rule, you will be redirected back to the import, where the selected transaction now is identified by the newly created rule.

## Quickstart Guide

To get quickly started with MoneyWatch, just check out the repo and launch `start_flask_devel.sh` to start the flask server in development mode.

At the first start, it will create a python virual environment, install all dependencies within and initializes the database:

```
$ ./start_flask_devel.sh
./start_flask_devel.sh
-> creating python virtual environment
-> enable virtual environment
-> installing moneywatch in virtual environment
Obtaining file:///opt/moneywatch
Collecting Flask (from moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/f2/28/2a03252dfb9ebf377f40fba6a7841b47083260bf8bd8e737b0c6952df83f/Flask-1.1.2-py2.py3-none-any.whl (94kB)
    100% |████████████████████████████████| 98kB 415kB/s
Collecting Flask-Session (from moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/32/6a/c1cf600a14b98347a35b1142bb5f2674f356c261a6de4a36c88fc8a47620/Flask_Session-0.3.2-py2.py3-none-any.whl
Collecting Flask-Babel (from moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/ab/3e/02331179ffab8b79e0383606a028b6a60fb1b4419b84935edd43223406a0/Flask_Babel-2.0.0-py3-none-any.whl
Collecting Flask-SQLAlchemy (from moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/af/4b/3dd83c3e2c6e3034b804d971952e0120606506f153990cc56d2d33173b72/Flask_SQLAlchemy-2.4.4-py2.py3-none-any.whl
Collecting Flask-Migrate (from moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/e5/64/c75f173ba5420f5174be6f04dfa8d8250d4808c12a9cd781e84c0b31684f/Flask_Migrate-2.5.3-py2.py3-none-any.whl
Collecting Werkzeug>=0.15 (from Flask->moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/cc/94/5f7079a0e00bd6863ef8f1da638721e9da21e5bacee597595b318f71d62e/Werkzeug-1.0.1-py2.py3-none-any.whl (298kB)
    100% |████████████████████████████████| 299kB 168kB/s
Collecting Jinja2>=2.10.1 (from Flask->moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/30/9e/f663a2aa66a09d838042ae1a2c5659828bb9b41ea3a6efa20a20fd92b121/Jinja2-2.11.2-py2.py3-none-any.whl (125kB)
    100% |████████████████████████████████| 126kB 367kB/s
Collecting click>=5.1 (from Flask->moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/d2/3d/fa76db83bf75c4f8d338c2fd15c8d33fdd7ad23a9b5e57eb6c5de26b430e/click-7.1.2-py2.py3-none-any.whl (82kB)
    100% |████████████████████████████████| 86kB 335kB/s
Collecting itsdangerous>=0.24 (from Flask->moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/76/ae/44b03b253d6fade317f32c24d100b3b35c2239807046a4c953c7b89fa49e/itsdangerous-1.1.0-py2.py3-none-any.whl
Collecting cachelib (from Flask-Session->moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/e6/fc/9c5571cf72ac3ea64ad5cd9d704c1000452cb483a6a3233357d8f3da6991/cachelib-0.1.1-py3-none-any.whl
Collecting Babel>=2.3 (from Flask-Babel->moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/dd/a5/81076e10b5ef74493cf08a8e419e61b64324c9c55db4aa7f89c0240c4873/Babel-2.9.0-py2.py3-none-any.whl (8.8MB)
    100% |████████████████████████████████| 8.8MB 7.0kB/s
Collecting pytz (from Flask-Babel->moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/12/f8/ff09af6ff61a3efaad5f61ba5facdf17e7722c4393f7d8a66674d2dbd29f/pytz-2020.4-py2.py3-none-any.whl (509kB)
    100% |████████████████████████████████| 512kB 128kB/s
Collecting SQLAlchemy>=0.8.0 (from Flask-SQLAlchemy->moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/69/ef/6d18860e18db68b8f25e0d268635f2f8cefa7a1cbf6d9d9f90214555a364/SQLAlchemy-1.3.20.tar.gz (6.3MB)
    100% |████████████████████████████████| 6.3MB 10kB/s
Collecting alembic>=0.7 (from Flask-Migrate->moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/12/aa/c261dfd7f4ba6ce4701846a2689a46e2a172e012171de4378fc2926e3bf0/alembic-1.4.3-py2.py3-none-any.whl (159kB)
    100% |████████████████████████████████| 163kB 286kB/s
Collecting MarkupSafe>=0.23 (from Jinja2>=2.10.1->Flask->moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/b9/2e/64db92e53b86efccfaea71321f597fa2e1b2bd3853d8ce658568f7a13094/MarkupSafe-1.1.1.tar.gz
Collecting python-dateutil (from alembic>=0.7->Flask-Migrate->moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/d4/70/d60450c3dd48ef87586924207ae8907090de0b306af2bce5d134d78615cb/python_dateutil-2.8.1-py2.py3-none-any.whl (227kB)
    100% |████████████████████████████████| 229kB 211kB/s
Collecting python-editor>=0.3 (from alembic>=0.7->Flask-Migrate->moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/c6/d3/201fc3abe391bbae6606e6f1d598c15d367033332bd54352b12f35513717/python_editor-1.0.4-py3-none-any.whl
Collecting Mako (from alembic>=0.7->Flask-Migrate->moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/a6/37/0e706200d22172eb8fa17d68a7ae22dec7631a0a92266634fb518a88a5b2/Mako-1.1.3-py2.py3-none-any.whl (75kB)
    100% |████████████████████████████████| 77kB 506kB/s
Collecting six>=1.5 (from python-dateutil->alembic>=0.7->Flask-Migrate->moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/ee/ff/48bde5c0f013094d729fe4b0316ba2a24774b3ff1c52d924a8a4cb04078a/six-1.15.0-py2.py3-none-any.whl
Installing collected packages: Werkzeug, MarkupSafe, Jinja2, click, itsdangerous, Flask, cachelib, Flask-Session, pytz, Babel, Flask-Babel, SQLAlchemy, Flask-SQLAlchemy, six, python-dateutil, python-editor, Mako, alembic, Flask-Migrate, moneywatch
  Running setup.py install for MarkupSafe
  Running setup.py install for SQLAlchemy
  Running setup.py develop for moneywatch
Successfully installed Babel-2.9.0 Flask-1.1.2 Flask-Babel-2.0.0 Flask-Migrate-2.5.3 Flask-SQLAlchemy-2.4.4 Flask-Session-0.3.2 Jinja2-2.11.2 Mako-1.1.3 MarkupSafe-1.1.1 SQLAlchemy-1.3.20 Werkzeug-1.0.1 alembic-1.4.3 cachelib-0.1.1 click-7.1.2 itsdangerous-1.1.0 moneywatch python-dateutil-2.8.1 python-editor-1.0.4 pytz-2020.4 six-1.15.0
You are using pip version 7.1.2, however version 20.2.4 is available.
You should consider upgrading via the 'pip install --upgrade pip' command.
-> updating database
[2020-11-15 12:52:17,587] DEBUG in cache_buster: computing cache-busting values for static resources...
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 8a1bd376774f, Initial migration
INFO  [alembic.runtime.migration] Running upgrade 8a1bd376774f -> 07f9fee4d16a, change category_id can be NULL
INFO  [alembic.runtime.migration] Running upgrade 07f9fee4d16a -> a2487f80fe2c, remove trend_calculated from transactions table
INFO  [alembic.runtime.migration] Running upgrade a2487f80fe2c -> 2f7b1d0b3c37, add accounts table
INFO  [alembic.runtime.migration] Running upgrade 2f7b1d0b3c37 -> a025f3a71951, add color column to accounts table
INFO  [alembic.runtime.migration] Running upgrade a025f3a71951 -> aaf2ea3a2ce8, add index to date column
-> starting flask webserver on port 1234
 * Serving Flask app "moneywatch" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://0.0.0.0:1234/ (Press CTRL+C to quit)
```

You can stop the server by pressing CTRL+C.


## Import Plugin Mechanism

As every bank has its own export format for account transactions, MoneyWatch uses a import plugin mechanism, so it is possible to implement other file formats quite easily.

A import plugin implements 3 important components:

* check function
* parse function
* register the plugin

Just look at the  [import plugins directory](moneywatch/import_plugins "Directory of all import plugins") to get an idea how it works.

### check function

The function will be called before the actual import takes place. It is used to determine, if the given file can be handled by the plugin or not.

```python
def check_csv(stream, name):
    if name.startswith("CHK_"):
        return True
    return False
```

It is called with the filestream `stream` ("stream" property from [FileStorage](http://werkzeug.pocoo.org/docs/0.14/datastructures/#werkzeug.datastructures.FileStorage) class), so you can read the file to verify if it contains a expected structure. As second parameter, the filename `name` is given, so you can also check, if the filename matches specific criterias.

If the given file can be handled by the plugin, the check function should return `True`, otherwise `False`.

### parse function

The parse function will be called, if your plugin is selected to import the file. So now we must parse the file and return all transactions, that are available in the file.

The parse function is called with the same arguments as the parse function. The only difference is the return value of the function. Instead of a boolean True/False, we now must return a list of dicts containing all transactions of the file.


```python
def parse_csv(stream, name):

    items = stream.read().decode("latin-1").split('\r\n')

    result = []

    for item in items:

        if item.strip():
            result_item = {}

            columns = re.split('?;"', item)

            date = columns[0]
            full_text = columns[1]
            valuta = columns[2]
            account = columns[5]

            if re.match(r"^\d\d\.\d\d\.\d\d\d\d$", date): # european format (dd.mm.yyyy)
                result_item['date'] = get_date_from_string(columns[0], '%d.%m.%Y')
            elif re.match(r"^\d\d\/\d\d\/\d\d\d\d$", date): # american format (mm/dd/yyyy)
                result_item['date'] = get_date_from_string(columns[0], '%m/%d/%Y')

            result_item['full_text'] = full_text
            result_item['valuta'] = float(valuta)
            result_item['account'] = account

            if result_item['valuta'] != 0:
                result.append(result_item)

    return result
```

The parse function must return a list of dicts ordered by the date ascending (oldest transaction first, newest transaction at last):

```python
[
    {'date': datetime.date(2018, 12, 21), 'valuta': -37.99, 'account': 'DE99123456781000987654', 'full_text': 'SEPA DIRECT DEBIT PayPal SHOES24 ONLINE SHOP'},
    {'date': datetime.date(2018, 12, 21), 'valuta': 150.0, 'account': 'DE99123456781000987654', 'full_text': 'CASH DEPOSIT VIA COUNTER 150 EUR'},
    {'date': datetime.date(2019, 1, 1), 'valuta': -37.89, 'account': 'DE99123456781000987654', 'full_text': 'SEPA DIRECT DEBIT YourInsurance LLC. contract 3483-39432 JON DOE 2018/12/01 BOOKING REFERENCE NO. 123-2345-678'},

    ...
]
```
The dict for one transaction item must use the following keys with their corresponding values:

| Key             | Necessary    |  Example                          | Description
| :--------------:|:------------:|-----------------------------------|------------------
| `date`          | mandatory    | `datetime.date(2018, 12, 21)`     | A `datetime.date()` object representing the date of the transaction. |
| `valuta`        | mandatory    | `-37.99` / `150.0`                | The amount of money for this particular transaction as a numeric float value, that was moved.<br/><br/>For incoming transactions, the value must be positive (>0). For outgoing transaction, the value must be negative (<0).<br/><br/> However, if the transaction is more like a message rather than a transaction, the valuta `0` should be used. In this case, it will be displayed as a notification and the user must take note of.
| `full_text`     | mandatory    | `"SEPA DIRECT DEBIT PayPal SHOES24 ONLINE SHOP"` | The complete booking text of the transaction as string.
| `account`       | *optional*   | `"DE99123456781000987654"`        | The IBAN (in formatted or normalized form) of the related account for which the import should be done. If the account IBAN is available, the transaction will be straight mapped to the corresponding account (incl. ruleset/categories) in MoneyWatch. This ensures a smooth processing.<br/><br/>If the IBAN is not available, MoneyWatch tries to autodetect the account in case a transaction from the file already exists in the database. If not, the user will be prompted to decide to which account these transactions should  be imported.

### register the plugin

The plugin now registers the two functions via a global plugin_info dict.

```python
plugin_info["targobank_csv"] = { "description": "Targobank CSV",
                                 "parse_function": parse_csv,
                                 "check_function": check_csv,
                                 "file_extension": ".csv"
                               }
 ```
The plugin_info can be registered using an internal identifier and deploying a dict wich contains a short description for the user, the two functions and optionally the file_extension it supports.


