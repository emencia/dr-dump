# -*- coding: utf-8 -*-

import os.path

import django
from django.core.management import call_command


def main(manifest_path):
    basedir = os.path.dirname(manifest_path)
    with open(manifest_path, 'r') as manifest:
        for fixture_name in manifest:
            fixture_path = os.path.join(basedir, fixture_name.strip())
            call_command('loaddata', fixture_path)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'manifest',
        nargs='?',
        default='./dumps/drdump.manifest',
    )

    if hasattr(django, 'setup'):
        # django 1.7 +
        django.setup()

    ns = parser.parse_args()
    main(ns.manifest)
