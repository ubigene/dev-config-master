import pytest
import json
from textwrap import dedent
from expand_file import ESMExpander, get_json_at_path, is_entrypoint_filename
from pathlib import Path


test_data = Path(__file__).parent.joinpath('test_data')


def test_extra_imports():
    extra_imports = dedent(f"""
        local extralib = import './testlib.libsonnet';
        local fn_closure = extralib.fn_closure('foo');
        local obj_closure = extralib.obj_closure('foo');
    """)
    expander = ESMExpander(extra_imports=extra_imports)
    test_jsn_path = test_data.joinpath('extra_imports.jsonnet').as_posix()
    expected = {
        test_jsn_path: {
            "function closure": "foobar",
            "object_closure.dash": "foo/bar",
            "object_closure.slash": "foo-bar",
            "simple function": "foofoofoo"
        }
    }
    json_doc = expander.expand([test_jsn_path])
    assert json_doc == expected


def test_esm():
    expander = ESMExpander()
    test_jsn_path = test_data.joinpath('simple_esm.jsonnet').as_posix()
    expected = {
        test_jsn_path: {
            "Another JSONPath filter": {
                "description": "description of name field",
                "length": 30,
                "name": "name",
                "type": "string"
            },
            "JSONPath filter": "description of quantity field",
            "array indexing": 10
        }
    }
    json_doc = expander.expand([test_jsn_path])
    assert json_doc == expected


def test_json_import():
    expander = ESMExpander()
    test_jsn_path = test_data.joinpath('json_import.jsonnet').as_posix()
    expected = {
        test_jsn_path: True
    }
    json_doc = expander.expand([test_jsn_path])
    assert json_doc == expected


@pytest.mark.parametrize('path,expected', [
    ('e.*', [1, 2, ['foo']]),
    ('e.z', ['foo']),
    ('e.y', 2),
    ('e.y~', 'y'),
    ('e.*~', ['x', 'y', 'z']),
])
def test_jsonpath(path, expected):
    test_jsn_path = test_data.joinpath('types.json').as_posix()
    with open(test_jsn_path, 'r') as fp:
        data = json.load(fp)
    assert get_json_at_path(data, path) == expected


def test_toplevel_array_filter():
    test_jsn_path = test_data.joinpath('columns.json').as_posix()
    with open(test_jsn_path, 'r') as fp:
        data = json.load(fp)
    assert get_json_at_path(data, '[0]') == {'name': "id", 'type': "int", 'length': 10, 'description': "description of id field",}
    assert get_json_at_path(data, '[?(@.name == "id")]') == {'name': "id", 'type': "int", 'length': 10, 'description': "description of id field",}


@pytest.mark.parametrize('fname,expected', [
    ('entrypoint.jsonnet', True),
    ('entrypoint.json', True),
    ('entrypoint', True),
    ('__entrypoint.jsonnet', True),
    ('_entrypoint.jsonnet', False),
    ('entrypoint.yaml', False),
    ('entrypnt.jsonnet', False),
])
def test_valid_entrypoint_filename(fname, expected):
    assert is_entrypoint_filename(fname) == expected