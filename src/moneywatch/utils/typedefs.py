from datetime import date
from typing_extensions import TypedDict, NotRequired
from typing import Callable, Optional, List, IO


class RawTransactionItem(TypedDict):
    date: date
    valuta: float
    account: NotRequired[str]
    full_text: str


class FullTransactionItem(RawTransactionItem):
    account_id: int
    category_id: int
    description: str


class DemoTransactionItem(RawTransactionItem):
    account_id: NotRequired[int]
    category_id: NotRequired[int]
    description: NotRequired[str]


CheckFunction = Callable[[IO[bytes], Optional[str]], bool]
ParseFunction = Callable[[IO[bytes], Optional[str]], List[RawTransactionItem]]
CreateFunction = Callable[[List[RawTransactionItem], IO[bytes]], str]


class PluginInfoItem(TypedDict):
    check_function: CheckFunction
    parse_function: ParseFunction
    create_function: NotRequired[CreateFunction]
    description: str
    file_extension: str
    _filename: str


class PluginNameItem(TypedDict):
    name: str
    description: str
    _filename: str
