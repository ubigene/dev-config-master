import pytest
import _jsonnet
from pathlib import Path
from jsonpath_ng.ext import parse
import json


def trest_native_callbacks():
    def concat(a, b):
        return a + b


    def return_types():
        return {
            'a': [1, 2, 3, None, []],
            'b': 1.0,
            'c': True,
            'd': None,
            'e': {
                'x': 1,
                'y': 2,
                'z': ['foo']
            },
        }

    native_callbacks = {
        'concat': (('a', 'b'), concat),
        'return_types': ((), return_types),
    }

    jsn = Path(__file__).parent.joinpath('test_data').joinpath('test_callbacks.jsonnet')
    assert _jsonnet.evaluate_file(jsn.as_posix(), native_callbacks=native_callbacks) == "true\n"

def get_json_at_path(json_data, path):
    ex = parse(f'$.{path}')
    match = ex.find(json_data)
    if not match:
        raise KeyError(f'Unable to resolve "{path}"')
    return match[0].value

def ref(uri):
    return uri


def test_native_callbacks():

    registry = {}
    ext_codes = {}
    ext_vars = {}

    def expand_file(refname, registry, ext_codes=None, ext_vars=None, native_callbacks=None):
        print("EXPAND_FILE(): ", refname)
        if not ext_codes:
            ext_codes = {}
        
        if not ext_vars:
            ext_vars = {}

        if not native_callbacks:
            native_callbacks = {}

        json_string = _jsonnet.evaluate_file(refname.as_posix(), ext_vars=ext_vars, ext_codes=ext_codes, native_callbacks=native_callbacks)
        
        rv = json.loads(json_string)
        print("RV(): ", rv)

        return rv


    def ref(rel, base):
        # (relative path to file, [subelement path within the file])
        parts = rel.split('#')
        # path to the referred file relative to the file being expanded
        rel_path = parts[0]
        
        # full path to the referred file
        refname = Path(base).parent.joinpath(Path(rel_path)).resolve()

        json_doc = expand_file(refname, registry, ext_codes, ext_vars)

        # check if we need to return a subelement in a file or a whole file
        if len(parts) > 1 and parts[1]:
            value = get_json_at_path(json_doc, parts[1])
        else:
            value = json_doc
        return value


    native_callbacks = {
        'ref': (('rel', 'base'), ref),
    }

    jsn = Path(__file__).parent.joinpath('test_data').joinpath('test_callback_imports.jsonnet')

    rv = json.loads(_jsonnet.evaluate_file(jsn.as_posix(), native_callbacks=native_callbacks))

    expected = {
        "Another JSONPath filter": {
            "description": "description of name field",
            "length": 30,
            "name": "name",
            "type": "string"
        },
        "JSONPath filter": "description of quantity field",
        "array indexing": 10,
        "full file reference": {
            "number": 42,
            "string": "value"
        },
        "key3": "42/meow",
        "key4": "42-meow"
    }
    
    print(json.dumps(rv, indent=4))
    assert rv == expected

    # assert rv == "true\n"




