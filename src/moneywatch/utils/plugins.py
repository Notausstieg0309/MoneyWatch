
import os

import moneywatch.utils.functions as functions
from flask_babel import gettext
from typing import KeysView, List, Optional, IO
from werkzeug.datastructures import FileStorage

from moneywatch.utils.typedefs import CheckFunction, ParseFunction, PluginInfoItem, PluginNameItem, RawTransactionItem



class LoadPluginException(Exception):
    pass


class NoParseFunctionException(Exception):
    pass


class NoCreateFunctionException(Exception):
    pass


class UnknownCreatePlugin(Exception):
    pass


class PluginManager:
    def __init__(self, path: str):

        self._plugin_info: dict[str, PluginInfoItem] = {}
        self._file_info: dict[str, str] = {}
        self._path = path
        self._load_plugins()

    def _load_error_str(self, file: str, message: str) -> str:
        return "error while loading plugin: %s => %s" % (file, message)

    def _load_plugins(self):

        def _get_plugin_pathnames(path: str) -> List[str]:
            if path and os.path.exists(path):
                return sorted([
                    path + "/" + f
                    for f in os.listdir(path)
                    if not f.startswith(".") and f.endswith(".py")
                ])
            return []

        self._file_list = _get_plugin_pathnames(self._path)

        self._plugin_info = {}

        for f in self._file_list:

            plugin_info: dict[str, PluginInfoItem] = {}

            plugin_context = {
                "plugin_info": plugin_info,
                "get_date_from_string": functions.get_date_from_string,
                "is_valid_iban": functions.is_valid_iban,
                "normalize_iban": functions.normalize_iban
            }

            try:
                exec(open(f, "r").read(), plugin_context)

            except Exception as e:
                print(self._load_error_str(f, str(e)))
                continue

            for key in plugin_info.keys():
                plugin_info[key]["_filename"] = os.path.basename(f)

            self._plugin_info.update(plugin_info)


class ImportPluginsManager(PluginManager):
    def __init__(self, path: str):

        super().__init__(path)

    def _load_error_str(self, file: str, message: str) -> str:
        return "error while loading import plugin: %s => %s" % (file, message)

    def resolve_plugins_for_file(self, file: FileStorage) -> List[PluginNameItem]:

        result: List[PluginNameItem] = []

        for name, info in self._plugin_info.items():
            check_function: Optional[CheckFunction] = info.get("check_function", None)
            file_extension: Optional[str] = info.get("file_extension", None)

            # check file extension match
            if file_extension is not None and file.filename is not None and not file.filename.lower().endswith(file_extension.strip().lower()):
                continue

            # check if check function exists and matches
            if check_function is not None and hasattr(check_function, '__call__'):
                file.stream.seek(0)
                check_result = check_function(file.stream, file.filename)

                if check_result:
                    result.append({
                        "name": name,
                        "description": info.get("description", None),
                        "_filename": info.get("_filename", None)
                    })

            # if no check function available always select the plugin so the user can decide
            else:
                result.append({
                    "name": name,
                    "description": info.get("description", None),
                    "_filename": info.get("_filename", None)
                })

        return result

    def get_possible_file_extensions(self):
        self._load_plugins()
        result = []

        for plugin in self._plugin_info:
            file_extension: Optional[str] = self._plugin_info[plugin].get("file_extension", None)
            if file_extension is not None and not file_extension.strip().lower() in result:
                result.append(file_extension.strip().lower())
        return result

    def parse_file(self, file: FileStorage, plugin: str) -> List[RawTransactionItem]:

        result: List[RawTransactionItem] = []

        self._load_plugins()

        if plugin in self._plugin_info:
            parse_function: Optional[ParseFunction] = self._plugin_info[plugin].get("parse_function", None)

            if parse_function is not None and hasattr(parse_function, '__call__'):
                file.stream.seek(0)
                result = parse_function(file.stream, file.filename)
            else:
                raise NoParseFunctionException(gettext("The plugin %s has no parse_function implemented or registered").format(plugin))

        result.sort(key=lambda x: x["date"])

        # reverse the list after sort to keep a stable order
        result.reverse()

        return result


    def create_file(self, items: List[RawTransactionItem], fd: IO[bytes], plugin: str) -> str:

        result = None

        self._load_plugins()

        if self.plugin_loaded(plugin):
            create_function = self._plugin_info[plugin].get("create_function", None)

            if create_function is not None and hasattr(create_function, '__call__'):
                items.sort(key=lambda x: x["date"])
                result = create_function(items, fd)
            else:
                raise NoCreateFunctionException(plugin)
        else:
            raise UnknownCreatePlugin(plugin)
        return result


    def plugin_loaded(self, plugin_name: str) -> bool:
        return plugin_name in self._plugin_info


    def is_implemented(self, plugin_name: str, function_name: str) -> bool:
        function_dummy = self._plugin_info[plugin_name].get(function_name, None)
        if function_dummy is not None:
            return True
        return False

    def get_plugin_names(self) -> KeysView[str]:
        return self._plugin_info.keys()
