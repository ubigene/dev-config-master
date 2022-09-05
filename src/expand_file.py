#!/usr/bin/env python3
import argparse
import _jsonnet
import sys
from pathlib import Path
import re
import json
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse
from textwrap import dedent
from itertools import chain

from kubernetes import client, config, utils
from replace_from_yaml import replace_from_dict
import openshift as oc
from functools import partial
import logging
from openshift_overrides import modify_and_apply



def get_argument_parser():
    parser = argparse.ArgumentParser(description='Render config master')

    parser.set_defaults(action=None)

    def _add_subparser(subp, name, help):
        my_parser = subp.add_parser(name, description=help, help=help)
        my_parser.set_defaults(**{'action': name})
        return my_parser

    subp = parser.add_subparsers(dest='action', help='Action to be performed')

    expand_p = _add_subparser(subp, 'expand', 'Expand configuration files')
    # verify_p = _add_subparser(subp, 'verify', 'Verify the passed files without expanding them')
    apply_p = _add_subparser(subp, 'apply', 'Apply schema changes')
    validate_p = _add_subparser(subp, 'validate', 'Validate schema changes')


    expand_p.add_argument('input_files', metavar='CONFIG_FILE', help='Path to the configuration file', nargs="+")

    apply_p.add_argument('input_files', metavar='ENTRYPOINT', help='Path to entrypoint or a folder that will be searched recursively', nargs="+")

    validate_p.add_argument('input_files', metavar='ENTRYPOINT', help='Path to entrypoint or a folder that will be searched recursively', nargs="+")
    # 

    # init_p = _add_subparser(subp, 'init', 'Initialise terraform environment')
    # plan_p = _add_subparser(subp, 'plan', 'Plan infrastructure change')
    # apply_p = _add_subparser(subp, 'apply', 'Apply planned infrastructure change')
    # refresh_p = _add_subparser(subp, 'refresh', 'Refresh a tfstate')
    # output_p = _add_subparser(subp, 'output', 'Print outputs')
    # destroy_p = _add_subparser(subp, 'destroy', 'Destroy the environment')
    # taint_p = _add_subparser(subp, 'taint', 'Taint a resource')
    # list_p = _add_subparser(subp, 'list', 'List resources')
    # console_p = _add_subparser(subp, 'console', 'Run terraform console')

    # # Mode-specific args
    # plan_p.add_argument('--skip-dashboard', default=False, action='store_true', help='Skip dashboard create/update')
    # plan_p.add_argument('--do-not-destroy', default=False, action='store_true',
    #                     help='Do not destroy any resources (only perform create & in-place updates)')
    # taint_p.add_argument('--module', help='-module argument (taint only)')

    # console_p.add_argument('--commands', nargs='*', type=str, help='list of console commands to execute')
    # console_p.add_argument('--output', type=str, help='Filename to save output to (JSON format)')
    # console_p.add_argument('--use-state', default=False, action='store_true', help='Use tfstate')

    # # Shared args
    # for _parser in (plan_p, apply_p, taint_p, refresh_p):
    #     _parser.add_argument('--target', nargs='*', help='targets for the terraform function')
    return parser


def evaluate_jsonnet_file(*args, **kwargs):
    """ Evaluate Jsonnet file and return JSON object """
    return json.loads(_jsonnet.evaluate_file(*args, **kwargs))


class ESMExpander(object):
    def __init__(self, extra_imports=None):
        self.registry = {}
        self.jsonnet_params = {
            'ext_codes': {},
            'ext_vars': {},
            'native_callbacks': {
                'ref': (('rel', 'base'), self.expand_reference_callback),
            }
        }
        esmlib = Path(__file__).parent.joinpath('jsonnet').joinpath('esm.libsonnet').resolve()
        self.extra_imports = dedent(f"""
                local esmlib = import '{esmlib.as_posix()}';
                local esm = esmlib.esm(std.thisFile);
            """)
        if extra_imports:
            self.extra_imports += extra_imports


    def expand(self, input_files):
        rv = {}
        fnames = [Path(f).resolve() for f in input_files]
        assert all((f.exists() for f in fnames)), "All input files should exist"
        full_paths = (f.as_posix() for f in fnames)
        rv = {fname.as_posix(): self.cached_expand_jsonnet_file(fname) for fname in fnames}
        return rv
            
    def expand_reference_callback(self, rel, base):
        # (relative path to file, [subelement path within the file])
        parts = rel.split('#')
        # path to the referred file relative to the file being expanded
        rel_path = parts[0]    
        # full path to the referred file
        refname = Path(base).parent.joinpath(Path(rel_path)).resolve()
        json_doc = self.cached_expand_jsonnet_file(refname)
        # check if we need to return a subelement in a file or a whole file
        return get_json_at_path(json_doc, parts[1]) if len(parts) > 1 and parts[1] else json_doc
        
    def cached_expand_jsonnet_file(self, refname):
        if refname in self.registry:
            rv = self.registry[refname]
        else:
            with open(refname, 'r') as fd:
                jsonnet_doc = self.extra_imports + fd.read()
            
            self.registry[refname] = json.loads(_jsonnet.evaluate_snippet(refname.as_posix(), jsonnet_doc, **self.jsonnet_params))
            # try:
            #     self.registry[refname] = json.loads(_jsonnet.evaluate_snippet(refname.as_posix(), jsonnet_doc, **self.jsonnet_params))
            # except RuntimeError:
            #     import IPython; IPython.embed()
        return self.registry[refname]


def get_json_at_path(json_data, path):
    """ Get JSON element specified by JSONPath """
    # TODO: fix the issue with (~) in the path upstream
    is_key_name = False       # Workaround for the path being a key name selector
    if path.endswith('~'):
        is_key_name = True
        path = path[:-1]

    if path.startswith('['):
        full_path = f'${path}'      # top level array
    else:
        full_path = f'$.{path}'     # top level dictionary
    ex = parse(full_path)
    
    match = ex.find(json_data)
    if not match:
        raise KeyError(f'Unable to resolve "{path}"')

    if  is_key_name:
        rv = [m.path.fields[0] for m in match]
    else:
        rv = [m.value for m in match]
    if len(rv) == 1:
        rv = rv[0]
    return rv


def is_entrypoint_filename(fname: str) -> bool:
    entrypoint_pattern = re.compile(r"^(__)?entrypoint(.json|.jsonnet)?$")
    return bool(re.match(entrypoint_pattern, fname))


def is_entrypoint(fp: Path) -> bool:
    return fp.is_file() and is_entrypoint_filename(fp.name)


def apply_k8s(input_files):
    fnames = {Path(f).resolve() for f in input_files}
    assert all(f.exists() for f in fnames), "All input files should exist"
    assert all(f.is_dir() or is_entrypoint(f) for f in fnames), 'An input should be a directory or an entrypoint'

    input_entrypoints = (f for f in fnames if is_entrypoint(f))
    dirs = (f for f in fnames if f.is_dir())
    found_entrypoints = (fname for dirname in dirs for fname in dirname.glob('**/entrypoint*') if is_entrypoint(fname))
    entrypoints = set(chain(input_entrypoints, found_entrypoints))
    
    expander = ESMExpander()
    json_doc = expander.expand(entrypoints)


    config.load_kube_config()
    k8s_client = client.ApiClient()

    for entrypoint, data in json_doc.items():
        path = Path(entrypoint)
        print(entrypoint)
        for k8s_resource in data['payload']['items']:
            # print(json.dumps(k8s_resource, indent=4))
            replace_from_dict(k8s_client, k8s_resource, namespace='eugene-butan-dev')


def apply_schema_changes(input_files, dry_run=False):
    fnames = {Path(f).resolve() for f in input_files}
    assert all(f.exists() for f in fnames), "All input files should exist"
    assert all(f.is_dir() or is_entrypoint(f) for f in fnames), 'An input should be a directory or an entrypoint'

    input_entrypoints = (f for f in fnames if is_entrypoint(f))
    dirs = (f for f in fnames if f.is_dir())
    found_entrypoints = (fname for dirname in dirs for fname in dirname.glob('**/entrypoint*') if is_entrypoint(fname))
    entrypoints = set(chain(input_entrypoints, found_entrypoints))
    
    expander = ESMExpander()
    json_doc = expander.expand(entrypoints)

    def change_schema(apiobj, new_schema):
        apiobj.model.update(new_schema)
        return True

    if dry_run:
        retries = 0
        cmd_args=["--dry-run=server"]
    else:
        retries = 2
        cmd_args=[]

    validation_results = []

    for entrypoint, data in json_doc.items():
        path = Path(entrypoint)
        for k8s_resource in data['payload']['items']:
            selector = f"{k8s_resource['kind']}/{k8s_resource['metadata']['name']}"
            apiobjects = oc.selector(selector).objects()
            if len(apiobjects) == 1:
                apiobj = apiobjects[0]
                new_schema = oc.APIObject(dict_to_model=k8s_resource).model
                result, changed = modify_and_apply(apiobj,
                    partial(change_schema, new_schema=new_schema, ), retries=retries, cmd_args=cmd_args)

                validation_results.append(changed)  
                if changed:
                    logging.info(result.out().strip())
            elif len(apiobjects) == 0:
                # create new
                raise NotImplementedError
            else:
                raise IndexError(f'Selector "{selector}" matched more than one resource.')

    return all(validation_results)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    args = get_argument_parser().parse_args()
    action = args.action
    logging.debug(f'Args: {args}')
    if action is None:
        get_argument_parser().print_help(sys.stderr)
        sys.exit(1)
    elif action == 'expand':
        expander = ESMExpander()
        json_doc = expander.expand(args.input_files)
        print(json.dumps(json_doc, indent=4))
    elif action == 'apply':
        apply_schema_changes(args.input_files)
    elif action == 'validate':
        print("Config is valid:", apply_schema_changes(args.input_files, dry_run=True))
