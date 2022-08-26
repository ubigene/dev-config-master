#!/usr/bin/env python3
import argparse
import _jsonnet
import sys
from pathlib import Path
import re
import json
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse


class AliasDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.aliases = {}

    def __getitem__(self, key):
        return dict.__getitem__(self, self.aliases.get(key, key))

    def __setitem__(self, key, value):
        return dict.__setitem__(self, self.aliases.get(key, key), value)

    def add_alias(self, key, alias):
        self.aliases[alias] = key


def get_argument_parser():
    parser = argparse.ArgumentParser(description='Render config master')

    parser.set_defaults(action=None)

    def _add_subparser(subp, name, help):
        my_parser = subp.add_parser(name, description=help, help=help)
        my_parser.set_defaults(**{'action': name})
        return my_parser

    subp = parser.add_subparsers(dest='action', help='Action to be performed')

    expand_p = _add_subparser(subp, 'expand', 'Expand configuration files')
    verify_p = _add_subparser(subp, 'verify', 'Verify the passed files without expanding them')


    expand_p.add_argument('input_files', metavar='CONFIG_FILE', 
        # type=argparse.FileType('r'), 
        help='Path to the configuration file', nargs="+")

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


def get_json_at_path(json_data, path):
    ex = parse(f'$.{path}')
    match = ex.find(json_data)
    if not match:
        raise KeyError(f'Unable to resolve "{path}"')
    return match[0].value

    
def expand(args):
    fnames = [Path(f).resolve() for f in args.input_files]
    assert all((f.exists() for f in fnames)), "All input files should exist"
    
    registry = AliasDict()
    ext_codes = {'brunch': 'true'}

    for fname in fnames:
        registry[fname] = expand_file(fname, registry, ext_codes, ext_vars={'prefix': 'Happy Hour '})
       
    for fname in fnames:     
        print(json.dumps({fname.as_posix(): registry[fname]}, indent=4))


    # import IPython; IPython.embed()

def expand_file(fname, registry, ext_codes, ext_vars=None):
    repo_root = Path('/Users/ebutan/Documents/workspace/config-master')
    # pattern = re.compile(r"esm.ref\((.*?)\)")


    pattern = re.compile(r"esm.ref\('(.*?)'\)")

    with open(fname, 'r') as fp:
        for lineno, line in enumerate(fp):
            for match in re.finditer(pattern, line):
                print('Found on line %s: %s' % (lineno+1, match.group(1)))
                if 'json' in line:
                    uri = match.group(1).strip(r' \'\"')
                    parts = uri.split('#')
                    # path to the referred file relative to the file being expanded
                    refname_string = parts[0]
                    # full path to the referred file
                    refname = fname.parent.joinpath(Path(refname_string)).resolve()
                    assert refname.is_relative_to(repo_root), refname

                    # expand referred file first
                    # registry[refname] = {'cat': {'paws': [{'kind': 'furry'}, {}, {}]}}
                    registry[refname] = expand_file(refname, registry, ext_codes, ext_vars)
                    # Now we have 4 paths
                    # refname - full path to the referred file
                    # fname - full path to file being expanded
                    # refname_string - path to the referred file relative to the fname
                    # uri - full reference string
                    
                    if len(parts) > 1 and parts[1]:
                        value = get_json_at_path(registry[refname], parts[1])
                    else:
                        value = registry[refname]
                    ext_codes[uri] = json.dumps(value)

    if not ext_vars:
        ext_vars = {}
    json_string = _jsonnet.evaluate_file(fname.as_posix(), ext_vars=ext_vars, ext_codes=ext_codes)
    return json.loads(json_string)




if __name__ == '__main__':
    args = get_argument_parser().parse_args()
    action = args.action
    print(args)
    if action is None:
        get_argument_parser().print_help(sys.stderr)
        sys.exit(1)
    elif action == 'expand':
        expand(args)
    