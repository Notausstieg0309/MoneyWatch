# MoneyWatch

MoneyWatch is a lightweight web application helps you to monitor your bank account about performed and planned transactions. It helps you to track your earnings/spendings and gives you indication of your current and planned balance. 

You can import your transactions via file import. Currently supported file formats are:
* Targobank CSV

The supported file formats can be easily extended by implementing an own [import plugin](/moneywatch/import_plugins).

Currently the following translations are available:
* English (default)
* German

It is written in [Python 3](https://www.python.org/) and based on [Flask](http://flask.pocoo.org/). It is licensed under [MIT License](/LICENSE)

## Overview

MoneyWatch gives you a quick overview about your planned and already performed transactions.

![Screenshot of main overview](screenshots/overview.png?raw=true "Screenshot of main overview")

The overview shows you what are the maximum planned earnings and spendings (using all your planned budgets) and shows what is your current status.

![](screenshots/balance.png?raw=true "Balance table screenshot")

It indicates planned transactions (formatted as gray italic transaction) based on defined rules for regular transactions. 

![](screenshots/planned_transaction.png?raw=true "Planned transactions")

Regular transactions can be identified by import rules. For regular transaction, that have always (or sometimes) a varying booking value, the trend indicator shows the difference compared to the original planned value.

![](screenshots/trend_indicator.png?raw=true "Planned transactions")

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
    if name.startswith("CHK_191"):
        return True
    return False
```

It is called with the filestream `stream` ("stream" property from [FileStorage](http://werkzeug.pocoo.org/docs/0.14/datastructures/#werkzeug.datastructures.FileStorage) class), so you can read the file to verify if it contains a expected structure. As second parameter, the filename `name` is given, so you can also check, if the filename matches specific criterias.

If the given file can be handled by the plugin, the check function should return `True`, otherwise `False`.

### parse function

The parse function will be called, if your plugin is selected to import the file. So no we must parse the file and return all transaction, that are available in the file.

The parse function is called with the same arguments as the parse function.


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
            
            if re.match(r"^\d\d\.\d\d\.\d\d\d\d$", date): # german format
                result_item['date'] = get_date_from_string(columns[0], '%d.%m.%Y')
            elif re.match(r"^\d\d\/\d\d\/\d\d\d\d$", date): # american format
                result_item['date'] = get_date_from_string(columns[0], '%m/%d/%Y')
                
            result_item['full_text'] = full_text
            result_item['valuta'] = float(valuta)
            
            if result_item['valuta'] != 0:
                result.append(result_item)

    return result
```

The parse function must return a list of dicts ordered by the date ascending (oldest transaction first, newest transaction at last):

```python
[
    {'date': datetime.date(2018, 12, 21), 'valuta': -37.99, 'full_text': 'SEPA DIRECT DEBIT PayPal SHOES24 ONLINE SHOP'},
    {'date': datetime.date(2018, 12, 21), 'valuta': 150.0, 'full_text': 'CASH DEPOSIT VIA COUNTER 150 EUR'},
    {'date': datetime.date(2019, 01, 01), 'valuta': -37.89, 'full_text': 'SEPA DIRECT DEBIT YourInsurance LLC. contract 3483-39432 JON DOE 2018/12/01 BOOKING REFERENCE NO. 123-2345-678'},
    
    ...
]
```

### check function

The plugin now registers the two functions via a global plugin_info dict.

```python
plugin_info["targobank_csv"] = { "description": "Targobank CSV",
                                 "parse_function": parse_csv,
                                 "check_function": check_csv,
                                 "file_extension": ".csv"
                               }
 ```
The plugin_info can be registered using an internal identifier and deploying a dict wich contains a short description for the user, the two functions and optionally the file_extension it supports.
 

