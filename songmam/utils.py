import importlib
import json
from inspect import iscoroutine
from typing import Callable
from typing import Optional

from parse import parse


def to_json(obj):
    return json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True)

def dynamic_call(function_path: str, *args, fallback: Optional[Callable] = None, **kwargs):
    parsed = parse("{import_path}:{function_name}", function_path)
    import_path = parsed['import_path']
    function_name = parsed['function_name']

    try:
        module = importlib.import_module(f"{import_path}")
        function = getattr(module, function_name)
        ret = function(*args, **kwargs)
        if iscoroutine(ret):
            await ret
    except ModuleNotFoundError as e:
        if fallback:
            ret = fallback(*args, **kwargs)
            if iscoroutine(ret):
                await ret
        else:
            raise e