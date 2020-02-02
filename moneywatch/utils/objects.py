# import moneywatch.utils.db as db
import moneywatch.utils.functions as utils
import datetime
import re

from moneywatch.utils.exceptions import *

from flask import current_app

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import expression as fn
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import event, orm
from sqlalchemy.sql import collate, asc

db = SQLAlchemy()




#     _____      _                              
#    / ____|    | |                             
#   | |     __ _| |_ ___  __ _  ___  _ __ _   _ 
#   | |    / _` | __/ _ \/ _` |/ _ \| '__| | | |
#   | |___| (_| | ||  __/ (_| | (_) | |  | |_| |
#    \_____\__,_|\__\___|\__, |\___/|_|   \__, |
#                         __/ |            __/ |
#                        |___/            |___/ 

class Category(db.Model):

    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    type = db.Column(db.Enum("in", "out"), unique=False, nullable=False)
    budget_monthly = db.Column(db.Integer, unique=False, nullable=True)    
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    
    _childs = db.relationship("Category",
                        # cascade deletions
                        cascade="all",

                        # many to one + adjacency list - remote_side
                        # is required to reference the 'remote' 
                        # column in the join condition.
                        backref=db.backref("parent", remote_side='Category.id'),

                )
    

    
    rules = db.relationship("Rule")
   
   
    def __init__(self, start=None, end=None, **kwargs):
        self._cache = {}
        self.setTimeframe(start, end)
        super(Category, self).__init__(**kwargs)
    
    @orm.reconstructor
    def init_on_load(self):
        self._cache = {}

    def setTimeframe(self, start=None, end=None):
        self._data = {}
        self._data["start"] = start
        self._data["end"] = end
        


    @property      
    def planned_transactions(self):
       
        if not "planned_transactions" in self._cache:
        
            result = []
               
            latest_transaction = self.account.latest_transaction

            latest_transaction_date = datetime.date.today()

            if latest_transaction:
                latest_transaction_date = latest_transaction.date

            for rule in self.rules:

                    if rule.regular and not rule.next_due > self.end and rule.next_valuta > 0:

                        booked_dates = []
                        planned_dates = []
                        
                        # get already existing transaction dates
                        for transaction in self.transactions:
                            if transaction.rule_id == rule.id:
                                booked_dates.append(transaction.date)
                         
                        # if already transactions available, just calculate from the date of newest transactions
                        if len(booked_dates) > 0:
                            planned_dates = utils.get_cyclic_dates_for_timerange(rule.next_due, rule.regular, max(booked_dates), self.end)
                        else:
                            planned_dates = utils.get_cyclic_dates_for_timerange(rule.next_due, rule.regular, self.start, self.end)
                        
                        current_app.logger.debug("found planned transactions for rule '%s': %s", rule.name, planned_dates)
                        
                        for date in planned_dates:
                            if (
                                    # no transaction for the same year/month exists
                                    (not utils.is_same_month_in_list(date, booked_dates)) and  
                                    
                                    # date is older then latest transaction for this rule
                                    (date.year > latest_transaction_date.year or 
                                        (date.year == latest_transaction_date.year and 
                                         date.month >= latest_transaction_date.month)
                                    ) and
                                    
                                    # planned transactions should be listed only for current or future months not
                                    (date >= datetime.date.today() or utils.is_same_month(date, datetime.date.today()))  
                               ):
                                if self.type == "out":
                                    result.append(PlannedTransaction(date, rule.next_valuta * -1, rule.description, rule.id))
                                else:
                                    result.append(PlannedTransaction(date, rule.next_valuta, rule.description, rule.id))
              
            result.sort(key=lambda x: x.date)   
            self._cache["planned_transactions"] = result
            
        return self._cache["planned_transactions"]


    @property
    def has_regular_rules(self):
 
        if not "has_regular_rules" in self._cache:
            
            result = False
            
            for rule in self.rules:
                if rule.regular:
                    result = True
                    break
            
            self._cache["has_regular_rules"] = result
            
        return self._cache["has_regular_rules"]      
            
    @property
    def has_overdued_planned_transactions(self):
    
        result = False
        
        for category in self.childs:
            if category.has_overdued_planned_transactions:
                result = True

        for transaction in self.planned_transactions:
           if transaction.overdue:
                result = True
            
        return result

    
    
    @property
    def budget(self):
    
        budget = self.budget_monthly
        
        if budget is not None and self.type == "out":
        
            # adapt budget to number of months
            budget *=  -1 * utils.get_number_of_months(self.start, self.end)
        
        return budget
   
    
    @property                    
    def start(self):
        return self._data.get("start", utils.get_first_day_of_month())

    @property                    
    def end(self):
        return self._data.get("end", utils.get_last_day_of_month())
        
    @property
    def childs(self):
      
        result = self._childs
      
        for category in result:
            category.setTimeframe(self.start, self.end)
                
        return result
        
               
    @property
    def transactions(self):

        if not "transactions" in self._cache:
        
            self._cache["transactions"] =  Transaction.query.filter_by(category_id=self.id).filter(Transaction.date.between(self.start, self.end)).all()
      
        return self._cache["transactions"]
            
    

    def getCategoryPath(self, delimiter):
    
        if self.parent_id is not None:
            parent = self.parent
            return parent.getCategoryPath(delimiter) + delimiter + self.name
        else:
            return self.name
                
 
    def getCategoryIdsAndPaths(self, delimiter):
    
        result = []
        
        result.append( (self.id, self.getCategoryPath(delimiter)) )
        
        for category in self.childs:
            result.extend( category.getCategoryIdsAndPaths(delimiter) )
        
        return result
        
    @property
    def valuta(self):
    
        if not "valuta" in self._cache:
            
            result = 0.0
            
            for category in self.childs or []:
                result += category.valuta
                
            for transaction in self.transactions or []:
                result += transaction.valuta
            
            self._cache["valuta"] =  result
            
        return self._cache["valuta"]
        
    @property
    def planned_transactions_valuta(self):
    
        if not "planned_transactions_valuta" in self._cache:
        
            result = 0.0
            
            for category in self.childs or []:
                result += category.planned_transactions_valuta

            for transaction in self.planned_transactions or []:
                result += transaction.valuta
                
            self._cache["planned_transactions_valuta"] = result
            
        return self._cache["planned_transactions_valuta"]
    
    @property
    def planned_valuta(self):
        
        if not "planned_valuta" in self._cache:
        
            result = 0
            for transaction in self.transactions or []:
                result += transaction.valuta 
                
            for transaction in self.planned_transactions or []:
                result += transaction.valuta 
            
            for category in self.childs or []:
                result += category.planned_valuta
            
            if self.budget is not None and not result < self.budget:        
                result = self.budget
                
            self._cache["planned_valuta"] = result
            
        return self._cache["planned_valuta"]

    @property
    def on_target(self):

        result = True
               
        for category in self.childs or []:
            if not category.on_target:
                result = False
                
        if not result:
            return False
        
        if self.budget != 0 and self.planned_valuta < self.budget:        
            result = False
            
        return result
    
   
    
    # def __repr__(self):
        # return self.__class__.__name__+"("+str(self._data)+"|"+str(self._kwargs)+")"
        
    @staticmethod       
    def getRootCategories(type, start=None, end=None):

        result = Category.query.filter_by(type=type, parent_id=None).all()
        
        for item in result:
            item.setTimeframe(start, end)
            
        return result
    

#    _____       _      
#   |  __ \     | |     
#   | |__) |   _| | ___ 
#   |  _  / | | | |/ _ \
#   | | \ \ |_| | |  __/
#   |_|  \_\__,_|_|\___|
#                       
#  


    

class Rule(db.Model):
    __tablename__ = 'ruleset'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(100), unique=False, nullable=False)
    pattern = db.Column(db.String(100), unique=False, nullable=False)
    regular = db.Column(db.Integer, unique=False, nullable=True)
    type = db.Column(db.Enum("in", "out"), unique=False, nullable=False)
    
    next_due = db.Column(db.Date, unique=False, nullable=True)
    next_valuta = db.Column(db.Float, unique=False, nullable=True)
    regular = db.Column(db.Integer, unique=False, nullable=True)
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship("Category")
    
    transactions = db.relationship("Transaction")
    
    def getTransactions(self, start=None, end=None, limit=None, reversed=False):

        result = Transaction.query.filter_by(rule_id=self.id)
        
    
        if start is not None and end is not None:
            result = result.filter(Transaction.date.between(start, end))
        elif start is not None:
            result = result.filter(Transaction.date >= start)
        elif end is not None:
            result = result.filter(Transaction.date <= end)
       
        if reversed:
            result = result.order_by(Transaction.date.desc())
        else:
            result = result.order_by(Transaction.date.asc())

        if limit is not None:
            result = result.limit(limit)
         
        if reversed:
            result = result.all()
            result.reverse()
            return result
            
        return result.all()

    def last_transaction(self, before=None):
        result = Transaction.query.filter_by(rule_id=self.id)
        
        if before is not None:
            result = result.filter(Transaction.date <= before)
        
        return result.order_by(Transaction.id.desc()).first()
        
    def updateNextDue(self, date, valuta):
                
        if self.regular:
            last_transaction = self.last_transaction()
            
            if last_transaction is None or (last_transaction is not None and last_transaction.date < date):
              
                next_due = utils.add_months(date, self.regular)
                
                current_app.logger.info("update rule '%s' (id: '%s') with next due '%s' and next valuta '%s'", self.name, self.id, next_due, valuta)
                
                self.next_valuta = valuta
                self.next_due = next_due
               
        
   
        
    def matchTransaction(self, transaction):
        if re.search(self.pattern, transaction.full_text, re.IGNORECASE):
            return True
        else:
            return False
     
    @staticmethod       
    def getRulesByType(type, **kwargs):
    
        result = Rule.query.filter_by(type=type).order_by(asc(collate(Rule.name, 'NOCASE'))).all()
            
        return result
        
    # @staticmethod    
    # def getRulesByCategory(category, **kwargs):
        # result = []
        # for rule in db.get_rules_for_category(category.id):
            # try:
                # result.append(Rule(rule, **kwargs))
            # except NoSuchItemError(type, id):
                # pass

        # return result
    
    @staticmethod
    def getNonMonthlyRegularRulesForTimeframe(type, start, end, **kwargs):
        result = []
        
        rules = Rule.query.filter_by(type=type).filter(Rule.regular > 1).all()
        
        for rule in rules:
            
            if rule.regular and rule.regular > 1 and rule.next_due <= end and rule.next_valuta > 0:
                
                dates = utils.get_cyclic_dates_for_timerange(rule.next_due, rule.regular, start, end)
                date_result = []
                for date in dates:
                    if date >= start and date >= rule.next_due and (date >= datetime.date.today() or utils.is_same_month(date, datetime.date.today())):
                        date_result.append(date)
                
                if len(date_result) > 0:
                    result.append( (rule, date_result) )
                    
        return result
    
        
    # def __repr__(self):
        # return self.__class__.__name__+"("+str(self._data)+")"
   

   
#    _______                             _   _             
#   |__   __|                           | | (_)            
#      | |_ __ __ _ _ __  ___  __ _  ___| |_ _  ___  _ __  
#      | | '__/ _` | '_ \/ __|/ _` |/ __| __| |/ _ \| '_ \ 
#      | | | | (_| | | | \__ \ (_| | (__| |_| | (_) | | | |
#      |_|_|  \__,_|_| |_|___/\__,_|\___|\__|_|\___/|_| |_|
#                                                          
#  

class Transaction(db.Model):

    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True, index=True)
   
    date = db.Column(db.Date, unique=False, nullable=False)
    valuta = db.Column(db.Float, unique=False, nullable=False)
    description = db.Column(db.String(100), unique=False, nullable=False)
    full_text = db.Column(db.String(100), unique=False, nullable=False)
   
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True, index=True)
    category = db.relationship("Category")
    
    rule_id = db.Column(db.Integer, db.ForeignKey('ruleset.id'), nullable=True, index=True)
    rule = db.relationship("Rule")
    
    trend = db.Column(db.Float, unique=False, nullable=True)
   
    
    
    @hybrid_property
    def type(self):
        if self.valuta > 0:
            return "in"
        elif self.valuta < 0:
            return "out"
        else:
            return "message"
          
          
    @type.expression
    def type(cls):
        return fn.case([ (cls.valuta > 0, "in"), (cls.valuta < 0, "out") ], else_="message")
            
            
    @property
    def complete(self):
        if self.valuta != 0 and self.description and self.category_id:
            return True
        elif self.valuta == 0 and self.description == True:
            return True
        return False
           
    def check_rule_matching(self):
    
        if self.type != "message" and self.rule_id is None and self.id is None:
        
            founded_rules = []
            
            for rule in Rule.getRulesByType(self.type):
                if rule.matchTransaction(self):
                    founded_rules.append(rule)
                    
            if len(founded_rules) == 1:
                self.rule_id = founded_rules[0].id
                
            elif len(founded_rules) > 1:
                raise MultipleRuleMatchError(self,founded_rules)
            
            if self.rule_id is not None:
                
                if self.description is None:
                    self.description = founded_rules[0].description
                
                if self.category_id is None:
                    self.category_id = founded_rules[0].category_id
                    
        # if multiple match occurs and user selects "None" (value: False)
        if self.rule_id == False:
            self.rule_id = None

    
    @property
    def is_editable(self):
        
        now = datetime.date.today()
        
        if (now - datetime.timedelta(days=14) <= self.date <= now) or utils.is_same_month(self.date, now):
            return True
            
        return False
    
    
    # def __repr__(self):
        # return self.__class__.__name__+"("+str(self._data)+")"
    
	
        
    @staticmethod 
    def _normalizeText(text):
        new_text = text
        for char in "/:.\\":
            new_text.replace(char, " ")
            
        ' '.join(new_text.split())
        
        return new_text.upper()
    
    @property   
    def exist(self):
        transactions = Transaction.query.filter_by(date=self.date, valuta=self.valuta).all()
        
        for transaction in transactions:
            if transaction:
                if Transaction._normalizeText(transaction.full_text) == Transaction._normalizeText(self.full_text):
                    return True
                    
        return False
        
    @staticmethod   
    def getTransactions(start=None,end=None):

        result = []
        
        if start is not None and end is not None:
            result = Transaction.query.filter(Transaction.date.between(start, end)).all()
        elif start is not None:
            result = Transaction.query.filter(Transaction.date >= start).all()
        elif end is not None:
            result = Transaction.query.filter(Transaction.date <= end).all()  
        else:
            result = Transaction.query.all()
     
        return result       
    
    @staticmethod   
    def getTransactionsByType(type, start=None,end=None):

        result = []
        
        if start is not None and end is not None:
            result = Transaction.query.filter(Transaction.type==type).filter(Transaction.date.between(start, end)).all()
        elif start is not None:
            result = Transaction.query.filter(Transaction.type==type).filter(Transaction.date >= start).all()
        elif end is not None:
            result = Transaction.query.filter(Transaction.type==type).filter(Transaction.date <= end).all()  
        else:
            result = Transaction.query.filter(Transaction.type==type).all()
     
        return result       
    
    @staticmethod   
    def getOldestTransaction():
        return Transaction.query.order_by(Transaction.date.asc()).first()
        
 
    @staticmethod   
    def getNewestTransaction():
          return Transaction.query.order_by(Transaction.date.desc()).first()
        

@event.listens_for(db.session, 'before_attach')
def handle_before_insert(session, item):

    if isinstance(item, Transaction):  
        if item.rule_id is not None:
            rule = Rule.query.filter_by(id=item.rule_id).one_or_none()
            if rule is not None:
                
                # update rule next due date/valuta
                rule.updateNextDue(item.date, item.valuta)
        
                # calculate trend compared to the latest transaction in the database
                last_transaction = rule.last_transaction(item.date)
                if last_transaction is not None:
                    trend = item.valuta - last_transaction.valuta
                    item.trend = trend if trend != 0 else None
                    current_app.logger.debug("calculated trend '%s' for transaction '%s' (%s) from %s" , item.trend, item.description, item.valuta, item.date)

        
    
  
#    _____  _                            _ _______                             _   _             
#   |  __ \| |                          | |__   __|                           | | (_)            
#   | |__) | | __ _ _ __  _ __   ___  __| |  | |_ __ __ _ _ __  ___  __ _  ___| |_ _  ___  _ __  
#   |  ___/| |/ _` | '_ \| '_ \ / _ \/ _` |  | | '__/ _` | '_ \/ __|/ _` |/ __| __| |/ _ \| '_ \ 
#   | |    | | (_| | | | | | | |  __/ (_| |  | | | | (_| | | | \__ \ (_| | (__| |_| | (_) | | | |
#   |_|    |_|\__,_|_| |_|_| |_|\___|\__,_|  |_|_|  \__,_|_| |_|___/\__,_|\___|\__|_|\___/|_| |_|
#                                                                                                
#      

class PlannedTransaction:


    def __init__(self, date, valuta, description, rule_id):
        self.date = date
        self.valuta = valuta
        self.description = description
        self.rule_id = rule_id
    
    @property
    def overdue(self):
        return (self.date <= Transaction.getNewestTransaction().date and self.date < datetime.date.today())
    
    def __repr__(self):
        return self.description+" ("+str(self.valuta)+" €)"
         

