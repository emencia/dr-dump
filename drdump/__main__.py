# -*- coding: utf-8 -*-

from __future__ import absolute_import

import sys
import importlib
import argparse

from drdump.drdump import Drdump, ApplicationsList
from drdump.dependancies import DependanciesManager


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-m',
        '--map',
        metavar='FILE',
        default=None,
        help='The path to a map file',
    )
    parser.add_argument(
        '-x',
        '--exclude-app',
        metavar='APP',
        dest='exclude_apps',
        action='append',
        help='List of apps to exclude',
    )
    parser.add_argument(
        '-e',
        '--extra-app',
        metavar='APP',
        dest='extra_apps',
        default=[],
        action='append',
        help='Extra apps to dump',
    )
    parser.add_argument(
        '-a',
        '--dump-other-apps',
        action='store_true',
        default=False,
        help='Dump other applications',
    )
    parser.add_argument(
        'apps',
        metavar='APP',
        nargs='*',
        help='Applications to dump',
    )
    parser.add_argument(
        '-o',
        '--option',
        default=[],
        metavar='KEY[=value]',
        action='append',
        dest='options',
        help='Output codec options',
    )
    parser.add_argument(
        '-c',
        '--codec',
        default='ScriptOutput',
        help='Output codec',
    )
    return parser


def main(args=sys.argv[1:]):
    parser = get_parser()
    ns = parser.parse_args(args)

    dm = DependanciesManager.from_json_filename(ns.map, silent_key_error=not bool(ns.apps))
    if ns.apps:
        application_list = ApplicationsList(ns.apps + ns.extra_apps)
    else:
        application_list = ApplicationsList.from_packages(extra_apps=ns.extra_apps)

    drdump = Drdump(dm,
                    application_list,
                    exclude_apps=ns.exclude_apps,
                    dump_other_apps=ns.dump_other_apps,
                    )
    options = dict(x.split('=', 1) if '=' in x else (x, True)
                   for x in ns.options)
    if '.' in ns.codec:
        module_name, cls_name = ns.codec.rsplit('.', 1)
        module = importlib.import_module(module_name)
        output_cls = getattr(module, cls_name)
    else:
        from drdump import builder
        output_cls = getattr(builder, ns.codec)

    output = output_cls(**options)
    drdump(output)


if __name__ == '__main__':
    main()
