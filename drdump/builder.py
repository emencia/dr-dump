from __future__ import absolute_import

"""
Script generator
"""
import os.path
import sys

HELP_MESSAGE = """Usage: builder.py [OPTIONS]

Simple program that return dump django commands.

Options:
  --dump_other_apps             Dump no specify app data in last dump.
  --exclude_apps app1,app2      Exclude theses apps from other_apps dump.
  --help                        Show this message and exit."""


HEADER = """#!/usr/bin/env bash

"""

DUMPER_TEMPLATE = """{line_prefix}echo "* {name}: Dump {fixture_path}
{line_prefix}{django_instance} dumpdata{natural_key} --indent=2 {models} {exclude_models} > {fixture_path}

"""

LOADER_TEMPLATE = """{line_prefix}echo "* Importing: {fixture_path}
{line_prefix}{django_instance} loaddata {fixture_path}

"""


class BaseOutput(object):
    def __init__(self, dump_dir='./dumps/'):
        if not os.path.exists(dump_dir):
            os.makedirs(dump_dir)

        self.dump_dir = dump_dir
        self._step_no = None
        self._manifest = None

    @property
    def manifest_path(self):
        return os.path.join(self.dump_dir, 'drdump.manifest')

    def empty_dump_dir(self):
        file_list = os.listdir(self.dump_dir)
        for file_name in file_list:
            os.remove(os.path.join(self.dump_dir, file_name))

    def __enter__(self):
        assert self._manifest is None
        assert self._step_no is None
        self.empty_dump_dir()
        self._step_no = 0
        self._manifest = open(self.manifest_path, 'w')
        return self

    def __call__(self, name, options):
        self._step_no += 1
        fixture_name = '{:04}_{}.json'.format(self._step_no, name)
        self._manifest.write('{}\n'.format(fixture_name))
        return os.path.join(self.dump_dir, fixture_name)

    def __exit__(self, exc_type, exc_value, tb):
        self._step_no = None
        self._manifest.close()
        self._manifest = None


class DatabaseOutput(BaseOutput):
    def __enter__(self):
        output = super(DatabaseOutput, self).__enter__()
        import django
        if hasattr(django, 'setup'):
            # django 1.7 +
            django.setup()

        from django.core.management import call_command

        if django.VERSION >= (1, 8, 0):
            return DumpdataWrapper(output, call_command)

        return DumpdataWrapperNoOutput(output, call_command)


class BaseDumpdataWrapper(object):
    def __init__(self, output_codec, call_command):
        self.output_codec = output_codec
        self._call_command = call_command

    def __call__(self, name, options):
        from django.core.management import CommandError

        fixture_path = self.output_codec(name, options)
        models = options.get('models') or []
        command_kw = self.get_command_kwargs(options)
        try:
            self.run(fixture_path, models, command_kw)
        except CommandError as ce:
            sys.stderr.write('Cannot dump {} in {}\n'.format(models, fixture_path))
            sys.stderr.write('{}\n'.format(ce))

    def run(self, out, args, kw):
        raise NotImplementedError()

    def get_command_kwargs(self, options):
        return {
            'format': 'json',
            'exclude': options.get('exclude_models') or [],
            'use_natural_foreign_keys': options.get('natural-foreign', True),
            'use_natural_primary_keys': options.get('natural-primary', True),
            'indent': 2,
        }


class DumpdataWrapper(BaseDumpdataWrapper):
    def run(self, out, args, kw):
        kw['output'] = out
        return self._call_command('dumpdata', *args, **kw)


class DumpdataWrapperNoOutput(BaseDumpdataWrapper):
    def run(self, out, args, kw):
        with open(out, 'w') as output:
            _stdout, sys.stdout = sys.stdout, output
            try:
                self._call_command('dumpdata', *args, **kw)
            finally:
                sys.stdout = _stdout


class ScriptOutput(BaseOutput):
    """
    Generate a shell script to run django management commands
    """

    default_context = {
        'line_prefix': '',
        'django_instance': 'bin/django-instance',
    }

    def __init__(self, output=sys.stdout, script_formatter=None, dump_dir='./dumps/', **context):
        super(ScriptOutput, self).__init__(dump_dir)
        self.output = output
        self.script_formatter = script_formatter or ScriptFormatter(DUMPER_TEMPLATE)
        self.context = dict(self.default_context)
        self.context.update(context)

    def __enter__(self):
        self.output.write(HEADER)
        return super(ScriptOutput, self).__enter__()

    def __call__(self, name, options):
        fixture_name = super(ScriptOutput, self).__call__(name, options)
        context = self.context.copy()
        context.update({
            'name': name,
            'fixture_path': fixture_name,
            'natural_key': ' -n' if options.get('use_natural_key', False) else '',
            'models': ' '.join(options.get('models') or []),
            'exclude_models': (' '.join('-e {}'.format(m) for m in options['exclude_models'])
                               if options.get('exclude_models') else ''),
        })
        line = self.script_formatter(context)
        self.output.write(line)

    def __exit__(self, exc_type, exc_value, tb):
        try:
            self.output.flush()
        finally:
            super(ScriptOutput, self).__exit__(exc_value, exc_value, tb)


class ScriptFormatter(object):
    def __init__(self, line_template):
        self.line_template = line_template

    def __call__(self, context):
        return self.line_template.format(**context)
