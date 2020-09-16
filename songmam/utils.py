import importlib
import json
from inspect import iscoroutine
from typing import Callable
from typing import Optional

from parse import parse


def to_json(obj):
    return json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True)
