import json
from enum import Enum


def to_json(obj):
    return json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True)

class AutoName(Enum):
    """
    https://docs.python.org/3/library/enum.html#using-automatic-values
    """
    def _generate_next_value_(name, start, count, last_values):
        return name

class AutoNameLower(Enum):
    """
    https://docs.python.org/3/library/enum.html#using-automatic-values
    """
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()
