from tests.tcp_test_client import TcpTestClient
import signal
import logging
from tests import TEST_CONFIG
import time
import sys
import os
import pathlib
from threading import Thread
from typing import Callable, Optional, Any
import typing
import types
import ast
from tests.utils.logging import TEST_LOGGER


BBC_SERVER_DIR = pathlib.Path(__file__).parent.parent / "src"

sys.path.insert(0, os.path.join(BBC_SERVER_DIR))
sys.path.insert(0, os.path.join(pathlib.Path(__file__).parent.parent))

import bbc_server
from bbc_server.exceptions import InvalidPackageTypeException, InvalidBodyException
from bbc_server.packages import Decoder, PackageParsingExceptionPackage
from bbc_server._typing import BBCPackage


def is_optional_type(tp: Any):
    origin = typing.get_origin(tp)
    args = typing.get_args(tp)
    return origin is typing.Union and type(None) in args

def get_inner_type_of_optional(tp: Any):
    if is_optional_type(tp):
        return next(arg for arg in typing.get_args(tp) if arg is not type(None))
    return tp


class InteractiveTestClient(TcpTestClient):

    def __init__(self, ip, port, listener_delay: float = 0.5, filter_function: Optional[Callable] = None):
        super().__init__(ip, port)
        self.listener_delay = listener_delay
        self.filter_function = filter_function

    def make_interactive(self):
        signal.signal(signal.SIGINT, self._stop)
        self._listener_thread = Thread(target=self._listen_to_packages)
        self._listener_thread.start()
        self._package_input_loop()

    def _listen_to_packages(self):
        while self._is_running:
            while pkg := self.read_package():
                if self.filter_function:
                    pkg = self.filter_function(pkg)
                if pkg:
                    TEST_LOGGER.debug(pkg)
            time.sleep(self.listener_delay)

    def _generate_pkg_string(self):
        package_str = "raw string input [-1]; "
        packages = bbc_server.packages.PACKAGE_DICT
        for idx, package in enumerate(packages.keys()):
            package_str += f"{package} [{idx}]; "
        return package_str

    def _package_input_loop(self):
        packages = bbc_server.packages.PACKAGE_DICT
        while True:
            print("Please select from the list of packages:")
            print(self._generate_pkg_string())
            selection = int(input("Type number to select: "))
            if selection == -1:
                self.send_string(input("raw string input: "))
                continue
            package_class = list(packages.values())[selection]
            cls_parameters = {}
            hints = typing.get_type_hints(package_class.__init__)

            for key, parameter in package_class.JSON_PARAM_MAP.items():
                param_type = hints[parameter]
                if is_optional_type(param_type):
                    param_type = get_inner_type_of_optional(param_type)
                    param_optional = True
                else:
                    param_optional = False
                if isinstance(param_type, types.GenericAlias) and "dict" in str(param_type):
                    # handle dict inputs
                    cls_parameters[parameter] = dict(ast.literal_eval(input(f"{key} (as raw dict): ")))
                else:
                    param_in = input(f"{key}: ")
                    cls_parameters[parameter] = self._cast_objects(param_in, param_type, param_optional)

            # create package
            package = package_class(**cls_parameters)
            self.send_package(package)

    def _stop(self, signum, frame):
        self._is_running = False
        self._listener_thread.join()

    def _cast_objects(self, value: str, target_type: Any, optional: bool = False):
        if optional and (value == "" or value == "None"):
            return
        if target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        elif target_type == bool:
            return bool(value)
        elif target_type == str:
            return value


def main():

    IP = str(TEST_CONFIG.get("test_server", "IP")).strip()
    PORT = int(TEST_CONFIG.get("test_server", "PORT").strip())
    client = InteractiveTestClient(IP, PORT)
    client.make_interactive()


if __name__ == "__main__":
    main()