class MultipleRuleMatchError(Exception):
    def __init__(self,  transaction, rules, index = None):

        super().__init__()

        self.transaction = transaction
        self.rules = rules
        self.index = index
   
class MultiplePluginMatchError(Exception):
    def __init__(self, file, plugins):

        super().__init__()

        self.file = file
        self.plugins = plugins 
        
class NoPluginMatchError(Exception):
    def __init__(self, file):

        super().__init__()

        self.file = file
        
class NoSuchItemError(Exception):
    def __init__(self, type, data):

        super().__init__()
        self.type = type
        self.data = data

class UnknownAccountError(Exception):
    def __init__(self, iban):

        super().__init__()

        self.iban = iban        
        
class TransactionsWithoutAccountError(Exception):
    def __init__(self, transactions):

        super().__init__()
        self.transactions = transactions