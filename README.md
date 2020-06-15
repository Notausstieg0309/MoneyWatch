# MoneyWatch

MoneyWatch is a lightweight web application helps you to monitor your bank account about performed and planned transactions. It helps you to track your earnings/spendings and gives you indication of your current and planned balance. 

You can import your transactions via file import. Currently supported file formats are:
* Targobank CSV
* ING.de CSV

The supported file formats can be easily extended by implementing an own [import plugin](/moneywatch/import_plugins).

Currently the following translations are available:
* English (default)
* German

It is written in [Python 3](https://www.python.org/) and based on [Flask](http://flask.pocoo.org/). It is licensed under [MIT License](/LICENSE)

## Overview

MoneyWatch gives you a quick overview about your overall financial status.

![Screenshot of main overview](screenshots/index.png?raw=true "Screenshot of main overview")

It tracks for each account the planned and already performed transactions.

![Screenshot of account overview](screenshots/overview.png?raw=true "Screenshot of account overview")

The overview shows you what are the maximum planned earnings and spendings (using all your planned budgets) and shows what is your current status.

![](screenshots/balance.png?raw=true "Balance table screenshot")

It indicates planned transactions (formatted as gray italic transaction) based on defined rules for regular transactions. 

![](screenshots/planned_transaction.png?raw=true "Planned transactions")

Categories, which have assigned a maximum planned budget, display and budget indicator in the title bar indicating the percentual amount of already used budget for all underlying transactions.

![](screenshots/budget_indicator.png?raw=true "Budget indicator for categories with a maximum planned amount for spendings.")

Regular transactions can be identified by import rules. For regular transaction, that have always (or sometimes) a varying booking value, the trend indicator (little arrow) shows the difference compared to the original planned value.

![](screenshots/trend_indicator.png?raw=true "Planned transactions")

You can examine the overall history of a regular transaction by showing a historical chart, which shows all values since the last 12 months.

![](screenshots/historical_link.png?raw=true "Link to the historical transaction data")

![](screenshots/historical_chart.png?raw=true "The historical chart of transaction data over the last 12 months")

Regular transactions are expected to be booked on a specific date (based on the last transaction date). When an expected transaction is not booked on that day, you see an overdue indicator (warning sign) for the transaction and all contained categories.

![](screenshots/overdue.png?raw=true "The overdue indicator.")

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

![Screenshot of transaction import](screenshots/imports.png?raw=true "Screenshot of importing new transactions")

## Quickstart Guide

To get quickly started with MoneyWatch, just check out the repo and launch `start_flask_devel.sh` to start the flask server in development mode.

At the first start, it will create a python virual environment, install all dependencies within and initializes the database:

```
$ ./start_flask_devel.sh
-> creating python virtual environment
-> enable virtual environment
-> installing moneywatch in virtual environment
Obtaining file:///opt/moneywatch
Collecting Flask (from moneywatch==0.1)
  Using cached https://files.pythonhosted.org/packages/7f/e7/08578774ed4536d3242b14dacb4696386634607af824ea997202cd0edb4b/Flask-1.0.2-py2.py3-none-any.whl
Collecting Flask-Session (from moneywatch==0.1)
  Using cached https://files.pythonhosted.org/packages/7e/a3/3ba4cec2becb7c4e65dfa95052c7050832c12a1fc8a475ac572842c460bc/Flask_Session-0.3.1-py2.py3-none-any.whl
Collecting Flask-Babel (from moneywatch==0.1)
Collecting itsdangerous>=0.24 (from Flask->moneywatch==0.1)
  Using cached https://files.pythonhosted.org/packages/76/ae/44b03b253d6fade317f32c24d100b3b35c2239807046a4c953c7b89fa49e/itsdangerous-1.1.0-py2.py3-none-any.whl
Collecting Werkzeug>=0.14 (from Flask->moneywatch==0.1)
  Using cached https://files.pythonhosted.org/packages/20/c4/12e3e56473e52375aa29c4764e70d1b8f3efa6682bef8d0aae04fe335243/Werkzeug-0.14.1-py2.py3-none-any.whl
Collecting click>=5.1 (from Flask->moneywatch==0.1)
  Using cached https://files.pythonhosted.org/packages/fa/37/45185cb5abbc30d7257104c434fe0b07e5a195a6847506c074527aa599ec/Click-7.0-py2.py3-none-any.whl
Collecting Jinja2>=2.10 (from Flask->moneywatch==0.1)
  Using cached https://files.pythonhosted.org/packages/7f/ff/ae64bacdfc95f27a016a7bed8e8686763ba4d277a78ca76f32659220a731/Jinja2-2.10-py2.py3-none-any.whl
Collecting Babel>=2.3 (from Flask-Babel->moneywatch==0.1)
  Using cached https://files.pythonhosted.org/packages/b8/ad/c6f60602d3ee3d92fbed87675b6fb6a6f9a38c223343ababdb44ba201f10/Babel-2.6.0-py2.py3-none-any.whl
Collecting MarkupSafe>=0.23 (from Jinja2>=2.10->Flask->moneywatch==0.1)
Collecting pytz>=0a (from Babel>=2.3->Flask-Babel->moneywatch==0.1)
  Downloading https://files.pythonhosted.org/packages/61/28/1d3920e4d1d50b19bc5d24398a7cd85cc7b9a75a490570d5a30c57622d34/pytz-2018.9-py2.py3-none-any.whl (510kB)
    100% |████████████████████████████████| 512kB 111kB/s
Installing collected packages: itsdangerous, Werkzeug, click, MarkupSafe, Jinja2, Flask, Flask-Session, pytz, Babel, Flask-Babel, moneywatch
  Running setup.py develop for moneywatch
Successfully installed Babel-2.6.0 Flask-1.0.2 Flask-Babel-0.12.2 Flask-Session-0.3.1 Jinja2-2.10 MarkupSafe-1.1.0 Werkzeug-0.14.1 click-7.0 itsdangerous-1.1.0 moneywatch pytz-2018.9
You are using pip version 7.1.2, however version 18.1 is available.
You should consider upgrading via the 'pip install --upgrade pip' command.
-> initializing SQLite database
initialized database.
-> starting flask webserver on port 1234
 * Serving Flask app "moneywatch" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://0.0.0.0:1234/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 292-414-762
```

You can stop the server by pressing CTRL+C.

After the first run, the startup is faster:

```
$ ./start_flask_devel.sh
-> enable virtual environment
-> starting flask webserver on port 1234
 * Serving Flask app "moneywatch" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://0.0.0.0:1234/ (Press CTRL+C to quit)
 * Restarting with stat
```

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
 

