# -*- coding: utf-8 -*-

from drdump import load

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            'manifest',
            nargs='?',
            default='./dumps/drdump.manifest',
        )

    def handle(self, **options):
        manifest = options['manifest']
        load.main(manifest)
