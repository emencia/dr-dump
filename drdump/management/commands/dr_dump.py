# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging

from django.core.management.base import BaseCommand
try:
    from django.utils.module_loading import import_string
except ImportError:
    from django.utils.module_loading import import_by_path as import_string

from django.conf import settings

from drdump.dependancies import DependanciesManager
from drdump.drdump import Drdump, ApplicationsList

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '-m',
            '--map',
            metavar='FILE',
            default=getattr(settings, 'DRDUMP_MAP_FILE', 'djangocms-3'),
            help='The path to a map file',
        )
        parser.add_argument(
            '-x',
            '--exclude-app',
            metavar='APP',
            dest='exclude_apps',
            default=getattr(settings, 'DRDUMP_EXCLUDE_APPS', []),
            action='append',
            help='List of apps to exclude',
        )
        parser.add_argument(
            '-e',
            '--extra-app',
            metavar='APP',
            dest='extra_apps',
            default=getattr(settings, 'DRDUMP_EXTRA_APPS', []),
            action='append',
            help='Extra apps to dump',
        )
        parser.add_argument(
            '-a',
            '--dump-other-apps',
            action='store_true',
            default=getattr(settings, 'DRDUMP_OTHER_APPS', False),
            help='Dump other applications',
        )
        parser.add_argument(
            '-o',
            '--option',
            default=getattr(settings, 'DRDUMP_OPTIONS', []),
            metavar='KEY[=value]',
            action='append',
            dest='codec_options',
            help='Output codec options',
        )
        parser.add_argument(
            '-c',
            '--codec',
            default='DatabaseOutput',
            dest='codec',
            help='Output codec',
        )

    def handle(self, **options):
        map_file = options.get('map')
        dm = DependanciesManager.from_json_filename(map_file, silent_key_error=True)
        application_list = ApplicationsList.from_packages(extra_apps=options.get('extra_apps') or [])

        drdump = Drdump(dm,
                        application_list,
                        exclude_apps=options.get('exclude_apps') or [],
                        dump_other_apps=options.get('dump_other_apps'),
                        )

        codec_options = options.get('codec_options') or []
        if isinstance(codec_options, list):
            codec_options = dict(x.split('=', 1) if '=' in x else (x, True) for x in codec_options)
        else:
            assert isinstance(codec_options, dict), 'DRDUMP_OPTIONS setting must be a dict, {!r}'.format(codec_options)

        codec = options.get('codec', 'DatabaseOutput')
        if '.' in codec:
            output_cls = import_string(codec)
        else:
            from drdump import builder
            output_cls = getattr(builder, codec)

        output = output_cls(**codec_options)
        drdump(output)
