import moneywatch.utils.db as db
import moneywatch.utils.functions as utils
import datetime
import re

from moneywatch.utils.exceptions import *

from flask import current_app

class Rule:

    def __new__(cls, data):
        if isinstance(data, int):
            item = db.get_rule(data)

            if item is not None:
                new = super(Rule, cls).__new__(cls)
                new._data = item
                return new
            else:
                raise NoSuchItemError("Rule", data)
                
        elif isinstance(data, dict):
        
            if "name" not in data or "pattern" not in data or "description" not in data or "category_id" not in data or "regular" not in data:
                raise ValueError
                
            new = super(Rule, cls).__new__(cls)
            new._data = data
            return new
        else:
            raise TypeError

    def __init__(self, data, **kwargs):
    
        if not hasattr(self, '_data'): # data is already set by __new__()
            self._data = data.copy()

    @property
    def name(self):
        return self._data.get("name", None)
        
    @name.setter
    def name(self, value):
        self._data["name"] = value
        
    @property
    def pattern(self):
        return self._data.get("pattern", None)
        
    @pattern.setter
    def pattern(self, value):
        self._data["pattern"] = value        

    @property
    def description(self):
        return self._data.get("description", None)
        
    @description.setter
    def description(self, value):
        self._data["description"] = value        
        
    @property
    def category_id(self):
        return self._data.get("category_id", None)
        
    @category_id.setter
    def category_id(self, value):
        self._data["category_id"] = int(value)
        
    @property
    def regular(self):
        return self._data.get("regular", None)
        
    @regular.setter
    def regular(self, value):
        self._data["regular"] = int(value)
        
    @property
    def next_due(self):
        return self._data["next_due"]
        
    @next_due.setter
    def next_due(self, value):
        self._data["next_due"] = value

    @property
    def next_valuta(self):
        return self._data.get("next_valuta", None)
        
    @next_valuta.setter
    def next_valuta(self, value):
        if value:
            self._data["next_valuta"] = abs(float(value))
        else:
            self._data["next_valuta"] = 0
        

    # read only properties   
    @property
    def id(self):
        return self._data.get("id",None)
    
    @property
    def type(self):
        return self._data.get("type", None)
     
    @property
    def category(self):
        return Category(self.category_id, transactions=False, subcategories=False)
        

    def last_transaction(self, before=None):
        result = db.get_last_transaction_by_rule(self.id, before)
        
        if result is not None:
            result = Transaction(result)
        return result
    
    def saveByTransaction(self, date, valuta):
    
        if self.regular:
            last_transaction = self.last_transaction()
            if last_transaction and last_transaction.date < date:
            
                next_due = utils.add_months(date, self.regular)
                
                current_app.logger.info("update rule '%s' (id: '%s') with next due '%s' and next valuta '%s'", self.name, self.id, next_due, valuta)
                
                self.next_valuta = valuta
                self.next_due = next_due
                self.save()
        
    def save(self):
        return db.save_rule(self._data)
        
    def delete(self):
        return db.delete_rule(self.id)
        
    def matchTransaction(self, transaction):
        if re.search(self.pattern, transaction.full_text, re.IGNORECASE):
            return True
        else:
            return False
     
    @staticmethod       
    def getRulesByType(type, **kwargs):
        result = []
        for rule in db.get_rules_for_type(type):
            result.append(Rule(rule, **kwargs))
            
        return result
        
    @staticmethod    
    def getRulesByCategory(category, **kwargs):
        result = []
        for rule in db.get_rules_for_category(category.id):
            try:
                result.append(Rule(rule, **kwargs))
            except ValueError:
                print("unable to find rule", rule)

            
        return result
        
    def __repr__(self):
        return self.__class__.__name__+"("+str(self._data)+")"
    
class Transaction:

    def __new__(cls, data):
    
        if isinstance(data, int):
            item = db.get_transaction(data)

            if item is not None:
            
                new = super(Transaction, cls).__new__(cls)
                new._data = item
                
                return new
                
            else:
                raise NoSuchItemError("Transaction", data)
                
        elif isinstance(data, dict):      
            if data.get("full_text", None) is None or data.get("valuta") is None or data.get("date", None) is None:
                raise ValueError
                
            new = super(Transaction, cls).__new__(cls)
            new._data = data
            return new
        else:
            raise TypeError

    def __init__(self, data, **kwargs):
    
        if not hasattr(self, '_data'): # data is already set by __new__()
            self._data = data.copy()
            
        self._cache = {}
        
        # apply ruleset if transaction is new
        if self._data.get('rule_id', None) is None and self.id is None:
        
            founded_rules = []
            
            for rule in Rule.getRulesByType(self.type):
                if rule.matchTransaction(self):
                    founded_rules.append(rule)
                    
            if len(founded_rules) == 1:
                self.rule_id = founded_rules[0].id
            elif len(founded_rules) > 1:
                raise MultipleRuleMatchError(self,founded_rules)
            
            if self.description is None and self._data.get('rule_id', None) is not None:
                self.description = self.rule.description
            
            if self.category_id is None and self._data.get('rule_id', None) is not None:
                self.category_id = self.rule.category_id
        

    
    # read/write-able properties
    @property
    def category_id(self):
        return self._data.get("category_id", None)
        
    @category_id.setter
    def category_id(self, value):
        self._data["category_id"] = value
        
    @property
    def rule_id(self):
        return self._data.get("rule_id", None)
        
    @rule_id.setter
    def rule_id(self, value):
        self._data["rule_id"] = value  
        
    @property
    def description(self):
        return self._data.get("description", None)
        
    @description.setter
    def description(self, value):
        self._data["description"] = value     
        

    # read only properties
    @property
    def full_text(self):
        return self._data.get("full_text", None)
        
    @property
    def id(self):
        return self._data.get("id",None)
    
    @property
    def type(self):
        return "in" if self.valuta > 0 else "out"
    
    @property
    def valuta(self):
       return self._data.get("valuta", None)
    
    @property
    def trend(self):
       
        if self._data["trend_calculated"]:
            return self._data["trend"]
        else:
        
            self._data["trend"] = None
            if self.rule_id is not None:
                rule = None
                try:
                    rule = self.rule 
                except ValueError:
                    pass
               
                if rule and rule.regular:
                    last_transaction = rule.last_transaction(self.date)
               
                    if last_transaction is not None:
                    
                        self._data["trend"] = self.valuta - last_transaction.valuta 
                        current_app.logger.debug("calculated trend '%s' for transaction '%s' (%s) from %s" , self._data["trend"], self.description, self.valuta, self.date)
                        
                self._data["trend_calculated"] = 1
                self.save()

            return self._data["trend"]
        
    
    @property
    def date(self):
             
        return self._data.get("date", None)
            
    @property
    def rule(self):
    
        if "rule_id" in self._data:
            rule = None
            try:
                rule = Rule(self._data["rule_id"])
            except NoSuchItemError:
                pass
            return rule
            
        else:
            return None
           
            
    
    def __repr__(self):
        return self.__class__.__name__+"("+str(self._data)+")"
    
	
    def save(self):
    
        rule = self.rule
        
        if rule is not None:
            rule.saveByTransaction(self.date,self.valuta)
            
        db.save_transaction(self._data)
       
	
    @property
    def category(self):
        return Transaction._getCategory(self.category_id)
    @staticmethod 

    def _getCategory(id):
        return Category(id) 
        
    @staticmethod 
    def _normalizeText(text):
        new_text = text
        for char in "/:.\\":
            new_text.replace(char, " ")
            
        ' '.join(new_text.split())
        
        return new_text.upper()
    
    @property   
    def exist(self):
        transaction = db.get_transaction_by_date_valuta(self.date, self.valuta)
        
        if transaction:
            if Transaction._normalizeText(transaction["full_text"]) == Transaction._normalizeText(self.full_text):
                return True
                
        return False
        
    
    @staticmethod   
    def getTransactions(start=None,end=None):

        result = []
        
        for transaction in db.get_transactions(start,end):
            result.append(Transaction(transaction))
        
        return result       
        
    @staticmethod   
    def getOldestTransaction():
        result = db.get_oldest_transaction()
        if result is not None:
            return Transaction(result)
        else:
            return None
        
 
    @staticmethod   
    def getNewestTransaction():
        result = db.get_latest_transaction()
        if result is not None:
            return Transaction(result)
        else:
            return None
        
class PlannedTransaction:

    def __init__(self, date, valuta, description, rule_id):
        self.date = date
        self.valuta = valuta
        self.description = description
        self.rule_id = rule_id
          
    def __repr__(self):
        return self.description+" ("+str(self.valuta)+" €)"
         
    
class Category:
    def __init__(self,data, **kwargs):
      
    
        if isinstance(data, (int,str)):
            self._data = self._data = db.get_category(data)
        elif isinstance(data, dict):            
            self._data = data.copy()

        self._kwargs = kwargs.copy()
        self._cache = {}
        

    @property      
    def planned_transactions(self):
       
        if "planned_transactions" in self._cache:
            return self._cache["planned_transactions"]
            
        else:
            result = []
            current_app.logger.debug("calculate planned transactions for category '%s' (start: %s, end: %s)", self.name, self.start, self.end)
            for rule in Rule.getRulesByCategory(self) or []:

                    if rule.regular and not rule.next_due > self.end:

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
                        
                        for day in planned_dates:
                            if not utils.is_same_month_in_list(day, booked_dates):
                                if self.type == "out":
                                    result.append(PlannedTransaction(day, rule.next_valuta * -1, rule.description, rule.id))
                                else:
                                    result.append(PlannedTransaction(day, rule.next_valuta, rule.description, rule.id))
              
            result.sort(key=lambda x: x.date)   
            self._cache["planned_transactions"] = result
            return result
                    
    
    def save(self):
        db.save_category(self._data)

    
    def delete(self):
    
        if self.id:
            for category in self.childs:
                category.delete()
             
            db.delete_category(self.id)
            
   
    @property                    
    def name(self):
        return self._data.get("name",None)
   
    @name.setter                    
    def name(self, value):
        self._data["name"] = str(value).strip()
    
    @property                    
    def parent_id(self):
        return self._data.get("parent",None)
   
    @parent_id.setter                    
    def parent_id(self, value):
        if value is None:
            self._data["parent"] = None
        else:
            self._data["parent"] = int(value)
    

    @property       
    def parent(self):

        if self.parent_id: 
            return Category(self.parent_id)
        else:
            return None
        
    
    @property
    def budget(self):
    
        budget = self._data.get('budget_monthly', 0)
        
        budget = float(0 if isinstance(budget,str) and budget.strip() == "" else budget)      

        if budget > 0 and self.type == "out":
        
            # adapt budget to number of months
            budget *=  -1 * utils.get_number_of_months(self.start,self.end)
        
        return budget
   
    @property                    
    def budget_monthly(self):
        return self._data.get('budget_monthly', 0)
        
    @budget_monthly.setter                    
    def budget_monthly(self, value):
        self._data['budget_monthly'] = abs(float(value))

        
    @property                    
    def id(self):
        return self._data.get("id",None)
        
    @property                    
    def type(self):
        return self._data.get("type",None)
    
    @property                    
    def start(self):
        return self._kwargs.get("start", utils.get_first_day_of_month())

    @property                    
    def end(self):
        return self._kwargs.get("end", utils.get_last_day_of_month())
        
    @property
    def childs(self):
      
        if "childs" in self._cache:
            return self._cache["childs"]
        else:
            result = []
            for category in db.get_category_childs(self.type, self.id) or []:
                result.append(Category(category,  **self._kwargs))
            self._cache["childs"] = result
            return result
        
    @property
    def transactions(self):
       
        if "transactions" in self._cache:
            return self._cache["transactions"]
        else:
            result = []
            
            for transaction in db.get_transactions_by_category(self.id, start=self.start, end=self.end) or []:              
                result.append(Transaction(transaction))
            
            self._cache["transactions"] = result
            return result
        
    def getCategoryPath(self, delimiter):
    
        if "path" in self._cache:
            return self._cache["path"]
        else:
            if self.parent_id is not None:
                parent = self.parent
                self._cache["path"] = parent.getCategoryPath(delimiter) + delimiter + self.name
            else:
                self._cache["path"] = self.name
                
            return self._cache["path"]
            

    def getCategoryIdsAndPaths(self, delimiter):
    

        result = []
        
        result.append( (self.id, self.getCategoryPath(delimiter)) )
        
        for category in self.childs:
            result.extend( category.getCategoryIdsAndPaths(delimiter) )
        
        return result
        
    @property
    def valuta(self):
    
        if "valuta" in self._cache:
            return self._cache["valuta"]
        else:

            result = 0.0
            
            for category in self.childs:
                result += category.valuta
                
            for transaction in self.transactions:
                result += transaction.valuta
            self._cache["valuta"] = result
            return result

    
    @property
    def planned_valuta(self):
       
            
            
        if "planned_valuta" in self._cache:
            
            return self._cache["planned_valuta"]
        else:
             
            result = 0
            for transaction in self.transactions:
                result += transaction.valuta 
                
            for transaction in self.planned_transactions:
                result += transaction.valuta 
            
            for category in self.childs:
                result += category.planned_valuta
            
            if self.budget != 0 and not result < self.budget:        
                result = self.budget
                
            self._cache["planned_valuta"] = result
           
            return result

    @property
    def on_target(self):

        result = True
               
        for category in self._categories or []:
            if not category.on_target:
                result = False
                
        if not result:
            return False
        
        if self.budget != 0 and self.planned_valuta < self.budget:        
            result = False
            
        return result
    
    def child_name_exists(self,name):
    
        for category in self.childs:
            if category.name == name:
                return True
        return False
        
    def sibling_name_exists(self,name):
    
        siblings = db.get_category_childs(self.type,self.parent_id)
        
        for category in siblings:
            if category["name"] == name:
                return True
        return False
        
    
    def __repr__(self):
        return self.__class__.__name__+"("+str(self._data)+"|"+str(self._kwargs)+")"
        
    @staticmethod       
    def getRootCategories(type, **kwargs):

        result = []
        for category in db.get_root_categories(type):
            result.append(Category(category, **kwargs))
            
        return result
    