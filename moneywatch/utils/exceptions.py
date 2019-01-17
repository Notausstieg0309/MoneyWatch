class MultipleRuleMatchError(Exception):
    def __init__(self,  transaction, rules):

        super().__init__()

        self.transaction = transaction
        self.rules = rules
   
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
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.type = kwargs.get("type",None)
        self.rules = kwargs.get("id", None)

        