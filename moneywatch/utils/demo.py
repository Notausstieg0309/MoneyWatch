from moneywatch.utils.objects import db, Account, Category, Rule, Transaction
from moneywatch.utils.functions import demo_date
import datetime

#
#  _____ _
# |_   _| |
#   | | | |_ ___ _ __ ___  ___
#   | | | __/ _ \ '_ ` _ \/ __|
#  _| |_| ||  __/ | | | | \__ \
# |_____|\__\___|_| |_| |_|___/
# =============================
#

# the default account (identified by "id" value) which will be used for transaction imports, if no "account" was given explicitly in Transaction() items
ACCOUNT_DEFAULT = 1


ACCOUNTS = [
    {"id": 1, "name": "Checking account", "iban": "DE99123456781000987654", "balance": 2038.45, "color": "bbdefb"},
    {"id": 2, "name": "Savings account", "iban": "DE99123456781000543210", "balance": 0, "color": "fff9c4"},
    {"id": 3, "name": "Credit line", "iban": "DE99002198761000003456", "balance": -1050.98, "color": "ffcdd2"}
]

CATEGORIES = [

    # Checking account
    # ================

    # Deposits
    {"id": 1, "name": "Salary", "type": "in"},
    {"id": 2, "name": "Cash Deposit", "type": "in"},
    {"id": 3, "name": "Other Revenue", "type": "in"},

    # Withdrawals
    {"id": 4, "name": "Fixed Costs", "type": "out"},
    {"id": 5, "name": "Variable Costs", "type": "out"},
    {"id": 6, "name": "Appartment", "type": "out", "parent_id": 4},
    {"id": 7, "name": "Savings", "type": "out", "parent_id": 4},
    {"id": 8, "name": "Hobbies", "type": "out", "parent_id": 4},
    {"id": 9, "name": "Food", "type": "out", "budget_monthly": 250, "parent_id": 4},
    {"id": 10, "name": "Communication", "type": "out", "parent_id": 4},
    {"id": 11, "name": "Mobility", "type": "out", "parent_id": 4},
    {"id": 12, "name": "Gas", "type": "out", "budget_monthly": 200, "parent_id": 11},
    {"id": 13, "name": "Insurances", "type": "out", "parent_id": 4},
    {"id": 14, "name": "Cash Withdrawals", "type": "out", "budget_monthly": 200, "parent_id": 5},

    # Savings account
    # ================

    # Deposits
    {"id": 15, "account_id": 2, "name": "Planned Savings", "type": "in"},
    {"id": 16, "account_id": 2, "name": "Unplanned Savings", "type": "in"},

    # Withdrawals
    {"id": 17, "account_id": 2, "name": "Withdrawals", "type": "out"},

    # Credit line
    # ===========

    # Deposits
    {"id": 18, "account_id": 3, "name": "Planned Savings", "type": "in"},
    {"id": 19, "account_id": 3, "name": "Unplanned Savings", "type": "in"},

    # Withdrawals
    {"id": 20, "account_id": 3, "name": "Withdrawals", "type": "out"},
]

RULESET = [

    # Checking account
    # ================

    # Deposits
    {"name": "Salary", "description": "Salary", "pattern": "FOOBAR INC. SALARY", "type": "in", "regular": 1, "category_id": 1},

    # Withdrawals
    {"name": "Appartment Rent", "description": "Rent", "pattern": "Living LLC Apartment Rent", "type": "out", "regular": 1, "category_id": 6},
    {"name": "Health Insurance", "description": "Health Insurance", "pattern": "YourInsurance LLC contract 3483-39432 JON DOE", "type": "out", "regular": 1, "category_id": 13},
    {"name": "Mobile Contract", "description": "Mobile Account", "pattern": "MOBILE ACCOUNT 491232345", "type": "out", "regular": 1, "category_id": 10},
    {"name": "LIDL", "description": "LIDL", "pattern": "LIDL", "type": "out", "category_id": 9},
    {"name": "Fitness Club", "description": "Fitness Club", "pattern": "ULTRAFIT MEMBERSHIP JON DOE", "type": "out", "regular": 1, "category_id": 8},
    {"name": "Pension", "description": "Pension", "pattern": "YourInsurance LLC. contract 3483-33789 JON DOE", "type": "out", "regular": 1, "category_id": 7},
    {"name": "Car Leasing", "description": "Car Leasing", "pattern": "YourCar INC. LEASING CONTR 43392847", "type": "out", "regular": 1, "category_id": 11},
    {"name": "Gas (TankOmat)", "description": "Gas (TankOmat)", "pattern": "TankOmat", "type": "out", "category_id": 12},
    {"name": "DSL Internet", "description": "DSL Fixed Line", "pattern": "FIXED LINE ACCOUNT 4914546345", "type": "out", "regular": 1, "category_id": 10},
    {"name": "Electricity", "description": "Electricity", "pattern": "GreenPower Corporated account no. 4732939", "type": "out", "regular": 1, "category_id": 6},
    {"name": "ALDI", "description": "ALDI", "pattern": "ALDI SAYS THANK YOU", "type": "out", "category_id": 9},
    {"name": "ATM Cash Withdrawal", "description": "Cash Withdrawal", "pattern": "ATM CASH WITHDRAWAL", "type": "out", "category_id": 14},
    {"name": "Car Insurance", "description": "Car Insurance", "pattern": "YourInsurance LLC. contract 3345-456434 JON DOE", "type": "out", "regular": 3, "category_id": 13},
    {"name": "Car Tax", "description": "Car Taxes", "pattern": "CAR TAX JOHN DOE", "type": "out", "regular": 1, "category_id": 11},
    {"name": "Deposit for Savings account", "description": "Savings account", "pattern": "TRANSFER SAVINGS ACCOUNT", "type": "out", "regular": 1, "category_id": 7},
    {"name": "Deposit for Credit line", "description": "Credit line", "pattern": "TRANSFER CREDIT LINE", "type": "out", "regular": 1, "category_id": 7},

    # Savings account
    # ================

    # Deposits
    {"account_id": 2, "name": "Deposit from checking account", "description": "Deposit checking account", "pattern": "TRANSFER SAVINGS ACCOUNT", "type": "in", "regular": 1, "category_id": 15},


    # Savings account
    # ================

    # Deposits
    {"account_id": 3, "name": "Deposit from checking account", "description": "Deposit checking account", "pattern": "TRANSFER CREDIT LINE", "type": "in", "regular": 1, "category_id": 18},


]


TRANSACTIONS = [

    # Checking account
    # ================

    # Accident Insurance
    {"date": demo_date(1), "valuta": -38.89, "full_text": "SEPA DIRECT DEBIT YourInsurance LLC contract 3483-39432 JON DOE %d %Y // %d-%m-%Y/00:51 0 50584600 701528545289964875"},
    {"date": demo_date(1, 1), "valuta": -35.36, "full_text": "SEPA DIRECT DEBIT YourInsurance LLC contract 3483-39432 JON DOE %d %Y // %d-%m-%Y/00:51 0 50584600 701528545289964875"},
    {"date": demo_date(1, 2), "valuta": -35.36, "full_text": "SEPA DIRECT DEBIT YourInsurance LLC contract 3483-39432 JON DOE %d %Y // %d-%m-%Y/00:51 0 50584600 701528545289964875"},
    {"date": demo_date(1, 3), "valuta": -35.36, "full_text": "SEPA DIRECT DEBIT YourInsurance LLC contract 3483-39432 JON DOE %d %Y // %d-%m-%Y/00:51 0 50584600 701528545289964875"},
    {"date": demo_date(1, 4), "valuta": -35.36, "full_text": "SEPA DIRECT DEBIT YourInsurance LLC contract 3483-39432 JON DOE %d %Y // %d-%m-%Y/00:51 0 50584600 701528545289964875"},
    {"date": demo_date(1, 5), "valuta": -31.33, "full_text": "SEPA DIRECT DEBIT YourInsurance LLC contract 3483-39432 JON DOE %d %Y // %d-%m-%Y/00:51 0 50584600 701528545289964875"},
    {"date": demo_date(1, 6), "valuta": -31.33, "full_text": "SEPA DIRECT DEBIT YourInsurance LLC contract 3483-39432 JON DOE %d %Y // %d-%m-%Y/00:51 0 50584600 701528545289964875"},
    {"date": demo_date(1, 7), "valuta": -29.98, "full_text": "SEPA DIRECT DEBIT YourInsurance LLC contract 3483-39432 JON DOE %d %Y // %d-%m-%Y/00:51 0 50584600 701528545289964875"},
    {"date": demo_date(1, 8), "valuta": -29.98, "full_text": "SEPA DIRECT DEBIT YourInsurance LLC contract 3483-39432 JON DOE %d %Y // %d-%m-%Y/00:51 0 50584600 701528545289964875"},
    {"date": demo_date(1, 9), "valuta": -29.98, "full_text": "SEPA DIRECT DEBIT YourInsurance LLC contract 3483-39432 JON DOE %d %Y // %d-%m-%Y/00:51 0 50584600 701528545289964875"},
    {"date": demo_date(1, 10), "valuta": -29.98, "full_text": "SEPA DIRECT DEBIT YourInsurance LLC contract 3483-39432 JON DOE %d %Y // %d-%m-%Y/00:51 0 50584600 701528545289964875"},


    # ALDI
    {"date": demo_date(2), "valuta": -56.32, "full_text": "SEPA DIRECT DEBIT ALDI SAYS THANK YOU FOR YOUR PURCHASE %d-%m-%Y SEPA // %d-%m-%Y/13:15 0 58066845 878965452266887875"},
    {"date": demo_date(18), "valuta": -64.65, "full_text": "SEPA DIRECT DEBIT ALDI SAYS THANK YOU FOR YOUR PURCHASE %d-%m-%Y SEPA // %d-%m-%Y/13:15 0 58066845 878965452266887875"},
    {"date": demo_date(25), "valuta": -35.48, "full_text": "SEPA DIRECT DEBIT ALDI SAYS THANK YOU FOR YOUR PURCHASE %d-%m-%Y SEPA // %d-%m-%Y/13:15 0 58066845 878965452266887875"},
    {"date": demo_date(10, 1), "valuta": -48.34, "full_text": "SEPA DIRECT DEBIT ALDI SAYS THANK YOU FOR YOUR PURCHASE %d-%m-%Y SEPA // %d-%m-%Y/13:15 0 58066845 878965452266887875"},
    {"date": demo_date(22, 1), "valuta": -67.65, "full_text": "SEPA DIRECT DEBIT ALDI SAYS THANK YOU FOR YOUR PURCHASE %d-%m-%Y SEPA // %d-%m-%Y/13:15 0 58066845 878965452266887875"},

    # LIDL
    {"date": demo_date(7), "valuta": -15.32, "full_text": "SEPA DIRECT DEBIT LIDL %d-%m-%Y SEPA // %d-%m-%Y/16:33 0 58066845 878965452266887875"},
    {"date": demo_date(21), "valuta": -23.48, "full_text": "SEPA DIRECT DEBIT LIDL %d-%m-%Y SEPA // %d-%m-%Y/16:33 0 58066845 878965452266887875"},
    {"date": demo_date(4, 1), "valuta": -24.78, "full_text": "SEPA DIRECT DEBIT LIDL %d-%m-%Y SEPA // %d-%m-%Y/16:33 0 58066845 878965452266887875"},
    {"date": demo_date(19, 1), "valuta": -14.96, "full_text": "SEPA DIRECT DEBIT LIDL %d-%m-%Y SEPA // %d-%m-%Y/16:33 0 58066845 878965452266887875"},

    # Fitness Club
    {"date": demo_date(17), "valuta": -19.99, "full_text": "SEPA DIRECT DEBIT ULTRAFIT MEMBERSHIP JON DOE // %d-%m-%Y/02:15 0 58066845 8488955454566"},
    {"date": demo_date(17, 1), "valuta": -19.99, "full_text": "SEPA DIRECT DEBIT ULTRAFIT MEMBERSHIP JON DOE // %d-%m-%Y/02:15 0 58066845 8488955454566"},

    # Electricity
    {"date": demo_date(10), "valuta": -42.0, "full_text": "SEPA DIRECT DEBIT GreenPower Corporated account no. 4732939 // %d-%m-%Y/02:15 0 88785454 98554535456"},
    {"date": demo_date(10, 1), "valuta": -42.0, "full_text": "SEPA DIRECT DEBIT GreenPower Corporated account no. 4732939 // %d-%m-%Y/02:15 0 88785454 98554535456"},

    # Cash Withdrawals
    {"date": demo_date(4), "valuta": -100.0, "full_text": "ATM CASH WITHDRAWAL 4587-878-845868 // %d-%m-%Y/13:15 0 9855455 88966452"},
    {"date": demo_date(16), "valuta": -50.0, "full_text": "ATM CASH WITHDRAWAL 4587-878-845868 // %d-%m-%Y/13:15 0 9855455 88966452"},
    {"date": demo_date(23), "valuta": -70.0, "full_text": "ATM CASH WITHDRAWAL 4587-878-845868 // %d-%m-%Y/13:15 0 9855455 88966452"},

    # Gas
    {"date": demo_date(5), "valuta": -38.49, "full_text": "SEPA DIRECT DEBIT TankOmat // %d-%m-%Y/17:34 0 9855455 88966452"},
    {"date": demo_date(18), "valuta": -30.74, "full_text": "SEPA DIRECT DEBIT TankOmat // %d-%m-%Y/17:34 0 9855455 88966452"},
    {"date": demo_date(26), "valuta": -42.67, "full_text": "SEPA DIRECT DEBIT TankOmat // %d-%m-%Y/17:34 0 9855455 88966452"},
    {"date": demo_date(3, 1), "valuta": -60.89, "full_text": "SEPA DIRECT DEBIT TankOmat // %d-%m-%Y/17:34 0 9855455 88966452"},
    {"date": demo_date(19, 1), "valuta": -23.48, "full_text": "SEPA DIRECT DEBIT TankOmat // %d-%m-%Y/17:34 0 9855455 88966452"},
    {"date": demo_date(21, 1), "valuta": -52.67, "full_text": "SEPA DIRECT DEBIT TankOmat // %d-%m-%Y/17:34 0 9855455 88966452"},

    # DSL Fixed Line
    {"date": demo_date(12), "valuta": -34.48, "full_text": "SEPA DIRECT DEBIT COMM UTD FIXED LINE ACCOUNT 4914546345 REFERENCE NO 54878654 // %d-%m-%Y/16:33 0 58066845 878965452266887875"},
    {"date": demo_date(12, 1), "valuta": -34.48, "full_text": "SEPA DIRECT DEBIT COMM UTD FIXED LINE ACCOUNT 4914546345 REFERENCE NO 54878654 // %d-%m-%Y/16:33 0 58066845 878965452266887875"},

    # Car Leasing
    {"date": demo_date(12), "valuta": -112.0, "full_text": "SEPA DIRECT DEBIT YourCar INC. LEASING CONTR 43392847 JON DOE // %d-%m-%Y/01:15 0 58066845 878965452266887875"},
    {"date": demo_date(12, 1), "valuta": -112.0, "full_text": "SEPA DIRECT DEBIT YourCar INC. LEASING CONTR 43392847 JON DOE // %d-%m-%Y/01:15 0 58066845 878965452266887875"},

    # Apartment Rent
    {"date": demo_date(18), "valuta": -448.0, "full_text": "TRANSFER Living LLC Apartment Rent JON DOE"},
    {"date": demo_date(18, 1), "valuta": -448.0, "full_text": "TRANSFER Living LLC Apartment Rent JON DOE"},

    # Salary
    {"date": demo_date(17), "valuta": 1910.25, "full_text": "FOOBAR INC. SALARY CONTRACT 8486652584"},
    {"date": demo_date(17, 1), "valuta": 1859.58, "full_text": "FOOBAR INC. SALARY CONTRACT 8486652584"},

    # Mobile Account
    {"date": demo_date(20), "valuta": -37.74, "full_text": "SEPA DIRECT DEBIT COMM UTD MOBILE ACCOUNT 491232345 BILL NO. 876999645-884"},
    {"date": demo_date(20, 1), "valuta": -37.74, "full_text": "SEPA DIRECT DEBIT COMM UTD MOBILE ACCOUNT 491232345 BILL NO. 876999645-884"},

    # Pension
    {"date": demo_date(20), "valuta": -101.1, "full_text": "SEPA DIRECT DEBIT YourInsurance LLC. contract 3483-33789 JON DOE BILL NO. 876999645-884"},
    {"date": demo_date(20, 1), "valuta": -101.1, "full_text": "SEPA DIRECT DEBIT YourInsurance LLC. contract 3483-33789 JON DOE BILL NO. 876999645-884"},

    # Car Insurance (used for special transaction indication)
    {"date": demo_date(-1), "valuta": -138.47, "full_text": "SEPA DIRECT DEBIT YourInsurance LLC. contract 3345-456434 JON DOE BILL NO. 87699345-884"},
    {"date": demo_date(-1, 3), "valuta": -138.47, "full_text": "SEPA DIRECT DEBIT YourInsurance LLC. contract 3345-456434 JON DOE BILL NO. 87699342-884"},
    {"date": demo_date(-1, 6), "valuta": -138.47, "full_text": "SEPA DIRECT DEBIT YourInsurance LLC. contract 3345-456434 JON DOE BILL NO. 87699342-884"},
    {"date": demo_date(-1, 9), "valuta": -138.47, "full_text": "SEPA DIRECT DEBIT YourInsurance LLC. contract 3345-456434 JON DOE BILL NO. 87699342-884"},

    # Car Tax (used for overdue indication)
    {"date": demo_date(1, 1), "valuta": -108.45, "full_text": "SEPA DIRECT CAR TAX JOHN DOE %d-%m-%Y BILL NO. 87699342-884"},
    {"date": demo_date(1, 2), "valuta": -108.45, "full_text": "SEPA DIRECT CAR TAX JOHN DOE %d-%m-%Y BILL NO. 87699342-884"},
    {"date": demo_date(1, 3), "valuta": -108.45, "full_text": "SEPA DIRECT CAR TAX JOHN DOE %d-%m-%Y BILL NO. 87699342-884"},

    # Transfer for savings account
    {"date": demo_date(18), "valuta": -100.0, "full_text": "SEPA TRANSFER SAVINGS ACCOUNT // %d-%m-%Y/13:15 0 9855455 88966452"},
    {"date": demo_date(18, 2), "valuta": -100.0, "full_text": "SEPA TRANSFER SAVINGS ACCOUNT // %d-%m-%Y/13:15 0 9855455 88966452"},
    {"date": demo_date(18, 3), "valuta": -100.0, "full_text": "SEPA TRANSFER SAVINGS ACCOUNT // %d-%m-%Y/13:15 0 9855455 88966452"},

    # Transfer for credit line
    {"date": demo_date(20), "valuta": -100.0, "full_text": "SEPA TRANSFER CREDIT LINE // %d-%m-%Y/13:15 0 9855455 88966452"},
    {"date": demo_date(20, 2), "valuta": -100.0, "full_text": "SEPA TRANSFER CREDIT LINE // %d-%m-%Y/13:15 0 9855455 88966452"},
    {"date": demo_date(20, 3), "valuta": -100.0, "full_text": "SEPA TRANSFER CREDIT LINE // %d-%m-%Y/13:15 0 9855455 88966452"},

    # non-regular transactions
    {"date": demo_date(5), "valuta": -19.99, "description": "Amazon - iPad Cover", "category_id": 5, "full_text": "SEPA DIRECT DEBIT AMAZON PAYMENTS ORDER 4587-878-845868 SEPA // %d-%m-%Y/13:15 0 9855455 88966452"},
    {"date": demo_date(15), "valuta": -43.89, "description": "Sushi Restaurant", "category_id": 5, "full_text": "SEPA DIRECT DEBIT SUSHI PALAST THANKS FOR YOUR VISIT SEPA // %d-%m-%Y/13:15 0 9855455 88966452"},
    {"date": demo_date(21), "valuta": 70.0, "description": "ATM Cash Deposit", "category_id": 2, "full_text": "ATM CASH DEPOSIT // %d-%m-%Y/13:15 0 9855455 88966452"},

    # messages
    {"date": demo_date(1), "valuta": 0, "description": "1", "full_text": "FOR AGREED DISPOSITION CREDITS UP TO EUR 1 000 00: 9 49% P A OVER EUR 1 000 00: 11 49% P A (FOR THE ENTIRE CLAIM) SPECIAL INTEREST RATE FOR TOLERATED OVERHAUL: 14 50% P A"},
    {"date": demo_date(15), "valuta": 0, "description": "1", "full_text": "INTEREST RATE CHANGE: FOR AGREED DISPOSITION CREDITS, FOLLOWING TARGET RATES APPLY: UP TO 1 000 00 EUR: 9 49% P A OVER 1 000 00 EUR: 11 49% P A (FOR THE ENTIRE CLAIM) TARGET INTEREST RATE FOR TOLERATED OVERDRAFT P A: 14 50% P A"},
    {"date": demo_date(-1, 1), "valuta": 0, "description": "1", "full_text": "CAPITAL INCOME TAX NO CAPITAL INCOME TAX APPLIED"},

    # Savings account
    # ================

    # Deposits

    # Transfer to Savings account
    {"account_id": 2, "date": demo_date(19), "valuta": 100.0, "full_text": "SEPA TRANSFER SAVINGS ACCOUNT // %d-%m-%Y/13:15 0 9855455 88966452"},
    {"account_id": 2, "date": demo_date(19, 1), "valuta": 100.0, "full_text": "SEPA TRANSFER SAVINGS ACCOUNT // %d-%m-%Y/13:15 0 9855455 88966452"},
    {"account_id": 2, "date": demo_date(19, 2), "valuta": 100.0, "full_text": "SEPA TRANSFER SAVINGS ACCOUNT // %d-%m-%Y/13:15 0 9855455 88966452"},


    # Credit line
    # ================

    # Deposits

    # Transfer to Savings account
    {"account_id": 3, "date": demo_date(21), "valuta": 100.0, "full_text": "SEPA TRANSFER CREDIT LINE // %d-%m-%Y/13:15 0 9855455 88966452"},
    {"account_id": 3, "date": demo_date(21, 1), "valuta": 100.0, "full_text": "SEPA TRANSFER CREDIT LINE // %d-%m-%Y/13:15 0 9855455 88966452"},
    {"account_id": 3, "date": demo_date(21, 2), "valuta": 100.0, "full_text": "SEPA TRANSFER CREDIT LINE // %d-%m-%Y/13:15 0 9855455 88966452"},

]


#  ______                _   _
# |  ____|              | | (_)
# | |__ _   _ _ __   ___| |_ _  ___  _ __  ___
# |  __| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
# | |  | |_| | | | | (__| |_| | (_) | | | \__ \
# |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
# =============================================
#


def create_items(items, cls, additional_values=None):
    print("creating %s() items..." % cls.__name__)

    for item in items:
        if additional_values is not None:
            tmp = additional_values.copy()
            tmp.update(item)
            item = tmp

        db.session.add(cls(**item))


def create_transactions(items, offset=None):

    print("creating transactions...")

    items.sort(key=lambda x: x["date"])

    today = datetime.date.today()

    if offset is not None:
        today -= datetime.timedelta(days=offset)

    importer_items = []

    for item in items:
        item["full_text"] = item["date"].strftime(item["full_text"])

        if item["date"] < today:
            if "account_id" not in item:
                item["account_id"] = ACCOUNT_DEFAULT
            item = Transaction(**item)
            item.check_rule_matching()
            db.session.add(item)
        else:
            resolve_account_iban(item)
            importer_items.append(item)

    return importer_items


def resolve_account_iban(item):

    account_id = ACCOUNT_DEFAULT

    if "account_id" in item:
        account_id = item["account_id"]
        item.pop("account_id", None)

    for account in ACCOUNTS:
        if account["id"] == account_id:
            item["account"] = account["iban"]


def create_demo_db(offset):
    print("dropping existing database...")
    db.drop_all()

    print("create new db scheme...")
    db.create_all()

    create_items(ACCOUNTS, Account)
    create_items(CATEGORIES, Category, {"account_id": ACCOUNT_DEFAULT})
    create_items(RULESET, Rule, {"account_id": ACCOUNT_DEFAULT})

    db.session.commit()

    items = create_transactions(TRANSACTIONS, offset)

    db.session.commit()

    return items
