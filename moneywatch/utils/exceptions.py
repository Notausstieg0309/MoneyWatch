class MultipleRuleMatchError(Exception):
    def __init__(self,  transaction, rules):

        super().__init__()

        self.transaction = transaction
        self.rules = rules
   
        
class NoSuchItemError(Exception):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        