class MultipleRuleMatchError(Exception):
    def __init__(self, transaction, rules, index=None):

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


class UnknownAccountError(Exception):
    def __init__(self, iban):

        super().__init__()

        self.iban = iban


class ItemsWithoutAccountError(Exception):
    def __init__(self, index_list):

        super().__init__()
        self.index_list = index_list
