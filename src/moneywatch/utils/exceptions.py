from __future__ import annotations

from typing import List, Optional

from werkzeug.datastructures import FileStorage

# needed to avoid cyclic imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from moneywatch.utils.objects import Rule, Transaction


class MultipleRuleMatchError(Exception):
    def __init__(self, transaction: 'Transaction', rules: 'List[Rule]', index=None):

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
    def __init__(self, file: FileStorage):

        super().__init__()

        self.file = file


class UnknownAccountError(Exception):

    def __init__(self, iban: str, item: dict, plugin_description: Optional[str] = None):

        super().__init__()

        self.iban = iban
        self.item = item
        self.plugin_description = plugin_description


class ItemsWithoutAccountError(Exception):
    def __init__(self, index_list):

        super().__init__()
        self.index_list = index_list
