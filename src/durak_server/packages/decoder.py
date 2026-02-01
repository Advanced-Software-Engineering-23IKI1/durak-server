from bbc_server.packages import PACKAGE_DICT
from bbc_server._typing import BBCPackage
from bbc_server.exceptions import InvalidPackageTypeException, InvalidBodyException
import json


def deserialize(input_str: str) -> BBCPackage:
    # 1. check for valid JSON
    try:
        parsed_dict = json.loads(input_str)
    except (json.JSONDecodeError, TypeError) as e:
        raise e

    # 2. check for valid type
    if package_type := parsed_dict.get("type"):
        if  not (package_class := PACKAGE_DICT.get(package_type)):
            raise InvalidPackageTypeException
    else:
        raise InvalidPackageTypeException

    # 3. check body content
    try:
        param_dict = {package_class.JSON_PARAM_MAP[key]: value for key, value in parsed_dict["body"].items()}
        return package_class(**param_dict)
    except (KeyError, TypeError, ValueError) as e:
        raise InvalidBodyException(str(e))

