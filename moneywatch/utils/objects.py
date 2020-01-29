# import moneywatch.utils.db as db
import moneywatch.utils.functions as utils
import datetime
import re

from moneywatch.utils.exceptions import *

from flask import current_app

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import expression as fn
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import orm

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
   
    #valuta = db.Column(db.Float, unique=False, nullable=False)
    name = db.Column(db.String(100), unique=False, nullable=False)
    type = db.Column(db.String(3), unique=False, nullable=False)
    budget_monthly = db.Column(db.Integer, unique=False, nullable=True)    
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    
    _childs = db.relationship("Category",
                        # cascade deletions
                        cascade="all",

                        # many to one + adjacency list - remote_side
                        # is required to reference the 'remote' 
                        # column in the join condition.
                        backref=db.backref("parent", remote_side='Category.id'),

                        # children will be represented as a dictionary
                        # on the "name" attribute.
                        #collection_class=db.attribute_mapped_collection('name'),
                )
    

    
    rules = db.relationship("Rule")
   
   
    def __init__(self, start=None, end=None, **kwargs):

        self.setTimeframe(start, end)
        super(Category, self).__init__(**kwargs)
       

    def setTimeframe(self, start=None, end=None):
        self._data = {}
        self._data["start"] = start
        self._data["end"] = end
        


    @property      
    def planned_transactions(self):
       
       
        result = []
        
        # if self._kwargs.get("planned_transactions", True):
            # current_app.logger.debug("calculate planned transactions for category '%s' (start: %s, end: %s)", self.name, self.start, self.end)
        # else: # no planned transactions needed (=> overview shows historical data older than current month)
            # current_app.logger.debug("skip calculation of planned transactions for category '%s' (start: %s, end: %s)", self.name, self.start, self.end)
            # self._cache["planned_transactions"] = result
            # return result
            
        newest_transaction = Transaction.getNewestTransaction()

        latest_transaction_date = datetime.date.today()

        if newest_transaction:
            latest_transaction_date = newest_transaction.date

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
        #self._cache["planned_transactions"] = result
        return result

    # @property
    # def rules(self):
        
        # if "rules" in self._cache:
            # return self._cache["rules"]  
        # else:
            # rules = Rule.getRulesByCategory(self)
            # self._cache["rules"] = rules
            # return rules
            
    @hybrid_property
    def has_regular_rules(self):
 
        result = False
        
        for rule in self.rules:
            if rule.regular:
                result = True
                break
        
        
        return result
            
    # @property
    # def has_overdued_planned_transactions(self):
    
        # if "has_overdued_planned_transactions" in self._cache:
            # return self._cache["has_overdued_planned_transactions"]
        # else:

            # result = False
            
            # for category in self.childs:
                # if category.has_overdued_planned_transactions:
                    # result = True

            # for transaction in self.planned_transactions:
               # if transaction.overdue:
                    # result = True
                
            # self._cache["has_overdued_planned_transactions"] = result
            
            # return result
    
    
    # def save(self):
        # db.save_category(self._data)

    
    # def delete(self):
    
        # if self.id:
            # for category in self.childs:
                # category.delete()
             
            # db.delete_category(self.id)
            
   
    # @property                    
    # def name(self):
        # return self._data.get("name",None)
   
    # @name.setter                    
    # def name(self, value):
        # self._data["name"] = str(value).strip()
    



        
    
    @hybrid_property
    def budget(self):
    
        budget = self.budget_monthly
        
        if budget > 0 and self.type == "out":
        
            # adapt budget to number of months
            budget *=  -1 * utils.get_number_of_months(self.start, self.end)
        
        return budget
   
    
    @property                    
    def start(self):
        return self._data.get("start", utils.get_first_day_of_month())

    @property                    
    def end(self):
        return self._data.get("end", utils.get_last_day_of_month())
        
    @hybrid_property
    def childs(self):
      
        result = self._childs
      
        for category in result:
            category.setTimeframe(self.start, self.end)
                
        return result
        
               
    @property
    def transactions(self):
       
        result = Transaction.query.filter_by(category_id=self.id).filter(Transaction.date.between(self.start, self.end)).all()
      
        return result
            
    
    @hybrid_method
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
        
    @hybrid_property
    def valuta(self):
    
        result = 0.0
        
        for category in self.childs or []:
            result += category.valuta
            
        for transaction in self.transactions or []:
            result += transaction.valuta
        
        return result
        
    @hybrid_property
    def planned_transactions_valuta(self):
    

        result = 0.0
        
        for category in self.childs or []:
            result += category.planned_transactions_valuta

        for transaction in self.planned_transactions or []:
            result += transaction.valuta
            
       
        return result
    
    @hybrid_property
    def planned_valuta(self):
        

        result = 0
        for transaction in self.transactions or []:
            result += transaction.valuta 
            
        for transaction in self.planned_transactions or []:
            result += transaction.valuta 
        
        for category in self.childs or []:
            result += category.planned_valuta
        
        if self.budget != 0 and not result < self.budget:        
            result = self.budget
            
      
       
        return result

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
    type = db.Column(db.String(3), unique=False, nullable=False)
    
    next_due = db.Column(db.Date, unique=False, nullable=True)
    next_valuta = db.Column(db.Float, unique=False, nullable=True)
    regular = db.Column(db.Integer, unique=False, nullable=True)
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship("Category")
    
    transactions = db.relationship("Transaction")
    
    
    
    # def __init__(self, data, **kwargs):
        # if isinstance(data, int):
            # item = db.get_rule(data)

            # if item is not None:                
                # self._data = item.copy()
            # else:
                # raise NoSuchItemError("Rule", data)
                
        # elif isinstance(data, dict):
        
            # if "name" not in data or "pattern" not in data or "description" not in data or "category_id" not in data or "regular" not in data:
                # raise ValueError
            
            # self._data = data.copy()
            
        # else:
            # raise TypeError
            
        
    # @property
    # def name(self):
        # return self._data.get("name", None)
        
    # @name.setter
    # def name(self, value):
        # self._data["name"] = value
        
    # @property
    # def pattern(self):
        # return self._data.get("pattern", None)
        
    # @pattern.setter
    # def pattern(self, value):
        # self._data["pattern"] = value        

    # @property
    # def description(self):
        # return self._data.get("description", None)
        
    # @description.setter
    # def description(self, value):
        # self._data["description"] = value        
        
    # @property
    # def category_id(self):
        # return self._data.get("category_id", None)
        
    # @category_id.setter
    # def category_id(self, value):
        # self._data["category_id"] = int(value)
        
    # @property
    # def regular(self):
        # return self._data.get("regular", None)
        
    # @regular.setter
    # def regular(self, value):
        # self._data["regular"] = int(value)
        
    # @property
    # def next_due(self):
        # return self._data["next_due"]
        
    # @next_due.setter
    # def next_due(self, value):
        # self._data["next_due"] = value

    # @property
    # def next_valuta(self):
        # return self._data.get("next_valuta", None)
        
    # @next_valuta.setter
    # def next_valuta(self, value):
        # if value:
            # self._data["next_valuta"] = abs(float(value))
        # else:
            # self._data["next_valuta"] = 0
        

    # # read only properties   
    # @property
    # def id(self):
        # return self._data.get("id",None)
    
    # @property
    # def type(self):
        # return self._data.get("type", None)
     
    # @property
    # def category(self):
        # return Category(self.category_id, transactions=False, subcategories=False)
    
    # def getTransactions(self, start=None, end=None, limit=None, reversed=False):

        # result = []
        
        # if reversed:
            # for transaction in db.get_transactions_by_rule_reversed(self.id, start, end, limit) or []:
                # result.append(Transaction(transaction))
        # else:
            # for transaction in db.get_transactions_by_rule(self.id, start, end, limit) or []:
                # result.append(Transaction(transaction))
        # return result


    # def last_transaction(self, before=None):
        # result = db.get_last_transaction_by_rule(self.id, before)
        
        # if result is not None:
            # result = Transaction(result)
        # return result
    
    # def updateNextDue(self, date, valuta):
    
        # if self.regular:
            # last_transaction = self.last_transaction()
            # if last_transaction is None or (last_transaction is not None and last_transaction.date < date):
            
                # next_due = utils.add_months(date, self.regular)
                
                # current_app.logger.info("update rule '%s' (id: '%s') with next due '%s' and next valuta '%s'", self.name, self.id, next_due, valuta)
                
                # self.next_valuta = valuta
                # self.next_due = next_due
                # self.save()
        
   
        
    def matchTransaction(self, transaction):
        if re.search(self.pattern, transaction.full_text, re.IGNORECASE):
            return True
        else:
            return False
     
    @staticmethod       
    def getRulesByType(type, **kwargs):
    
        result = Rule.query.filter_by(type=type).all()
            
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
    
    id = db.Column(db.Integer, primary_key=True)
   
    date = db.Column(db.Date, unique=False, nullable=False)
    valuta = db.Column(db.Float, unique=False, nullable=False)
    description = db.Column(db.String(100), unique=False, nullable=False)
    full_text = db.Column(db.String(100), unique=False, nullable=False)
   
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    category = db.relationship("Category")
    
    rule_id = db.Column(db.Integer, db.ForeignKey('ruleset.id'), nullable=True)
    rule = db.relationship("Rule")
    
    trend = db.Column(db.Float, unique=False, nullable=True)
    trend_calculated = db.Column(db.Boolean, unique=False, nullable=True, default=False)
   
    
    def __init__(self, **kwargs):

        # if multiple match occurs and user selects "None" (value: False)
        if kwargs.get('rule_id', None) == False:
            kwargs.pop('rule_id', None)
            
        super(Transaction, self).__init__(**kwargs)
        
        if self.type != "message" and self.rule_id is None and self.id is None:
        
            founded_rules = []
            
            for rule in Rule.getRulesByType(self.type):
                if rule.matchTransaction(self):
                    founded_rules.append(rule)
                    
            if len(founded_rules) == 1:
                self.rule_id = founded_rules[0].id
            elif len(founded_rules) > 1:
                raise MultipleRuleMatchError(self._data,founded_rules)
            
            if self.rule_id is not None:
                
                if self.description is None:
                    self.description = founded_rules[0].description
                
                if self.category_id is None:
                    self.category_id = founded_rules[0].category_id
            
    # def __init__(self, data, **kwargs):
    
        # if isinstance(data, int):
            # item = db.get_transaction(data)
            
            # if item is not None:
                # self._data = item.copy()
            # else:
                # raise NoSuchItemError("Transaction", data)   
                
        # elif isinstance(data, dict):      
            # if data.get("full_text", None) is None or data.get("valuta") is None or data.get("date", None) is None:
                # raise ValueError
                
            # self._data = data.copy()
        # else:
            # raise TypeError
     
            
        # self._cache = {}
        
        # # apply ruleset if transaction is new
        # if self.type != "message" and self._data.get('rule_id', None) is None and self._data.get("id", None) is None:
        
            # founded_rules = []
            
            # for rule in Rule.getRulesByType(self.type):
                # if rule.matchTransaction(self):
                    # founded_rules.append(rule)
                    
            # if len(founded_rules) == 1:
                # self.rule_id = founded_rules[0].id
            # elif len(founded_rules) > 1:
                # raise MultipleRuleMatchError(self._data,founded_rules)
            
            # if self.description is None and self._data.get('rule_id', None) is not None:
                # self.description = self.rule.description
            
            # if self.category_id is None and self._data.get('rule_id', None) is not None:
                # self.category_id = self.rule.category_id
        
        # # if multiple match occurs and user selects "None" (value: False)
        # if self._data.get('rule_id', None) == False:
            # self._data.pop('rule_id', None)
    
  
    
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
            
    

    
    # @property
    # def trend(self):
       
        # if self._data["trend_calculated"]:
            # return self._data["trend"]
        # else:
        
            # self._data["trend"] = None
            # if self.rule_id is not None:
                # rule = None
                # try:
                    # rule = self.rule 
                # except ValueError:
                    # pass
               
                # if rule and rule.regular:
                    # last_transaction = rule.last_transaction(self.date)
               
                    # if last_transaction is not None:
                    
                        # self._data["trend"] = self.valuta - last_transaction.valuta 
                        # current_app.logger.debug("calculated trend '%s' for transaction '%s' (%s) from %s" , self._data["trend"], self.description, self.valuta, self.date)
                        
                # self._data["trend_calculated"] = 1
                # self.save()

            # return self._data["trend"]
        
   
    
    
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
         

