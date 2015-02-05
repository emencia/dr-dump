"""
Script generator
"""
import json
import StringIO
import sys
import getopt

from drdump.dependancies import DependanciesManager

HELP_MESSAGE = """Usage: builder.py [OPTIONS]

Simple program that return dump django commands.

Options:
  --dump_other_apps             Dump no specify app data in last dump.
  --exclude_apps app1,app2      Exclude theses apps from other_apps dump.
  --help                        Show this message and exit."""


BASE_TEMPLATE = """#!/usr/bin/env bash

{items}"""

DUMPER_TEMPLATE = """{silencer}echo "* {label}: dump.{item_no}.{name}.json"
{silencer}{django_instance} dumpdata {natural_key} --indent=2 {models} > {dump_dir}/dump.{item_no}.{name}.json

"""

LOADER_TEMPLATE = """{silencer}echo "* Importing: dump.{item_no}.{name}.json"
{silencer}{django_instance} loaddata {dump_dir}/dump.{item_no}.{name}.json

"""


class ScriptBuilder(object):
    """
    Bash scripts builder
    """
    deps_index = {}
    # Make it empty to avoid silencer like without a Makefile
    echo_silencer = '@'
    django_instance_path_default = 'bin/django-instance'
    deps_manager = DependanciesManager

    def __init__(self, dumps_path, silent_key_error=False,
                 use_echo_silencer=False, django_instance_path=None,
                 base_template=BASE_TEMPLATE,
                 loadder_item_template=LOADER_TEMPLATE,
                 dumper_item_template=DUMPER_TEMPLATE, dump_other_apps=False,
                 exclude_apps=[]):

        self.dumps_path = dumps_path
        self.silent_key_error = silent_key_error
        self.use_echo_silencer = use_echo_silencer
        self.django_instance_path = django_instance_path or \
            self.django_instance_path_default
        self.base_template = base_template
        self.dumper_item_template = dumper_item_template
        self.loadder_item_template = loadder_item_template
        self.dump_other_apps = dump_other_apps
        self.exclude_apps = exclude_apps

        if not self.use_echo_silencer:
            self.echo_silencer = ''

    def get_deps_manager(self, *args, **kwargs):
        """
        Return instance of the dependancies manager using given args and kwargs

        Add 'silent_key_error' option in kwargs if not given.
        """
        if 'silent_key_error' not in kwargs:
            kwargs['silent_key_error'] = self.silent_key_error
        return self.deps_manager(*args, **kwargs)

    def get_global_context(self):
        return {
            'silencer': self.echo_silencer,
            'django_instance': self.django_instance_path,
            'dump_dir': self.dumps_path,
        }

    def build_template(self, mapfile, names, renderer):
        """
        Build source from global and item templates
        """
        AVAILABLE_DUMPS = json.load(open(mapfile, "r"))

        manager = self.get_deps_manager(AVAILABLE_DUMPS)

        fp = StringIO.StringIO()

        for i, item in enumerate(manager.get_dump_order(names), start=1):
            fp = renderer(fp, i, item, manager[item])

        if self.dump_other_apps:
            exclude_models = ['-e {0}'.format(app) for app in
                    self.exclude_apps]
            for i, item in enumerate(manager.get_dump_order(names), start=1):
                for model in manager[item]['models']:
                    if '-e ' not in model:
                        model = "-e {0}".format(model)
                    if model not in exclude_apps:
                        exclude_models.append(model)
            fp = renderer(fp, i+1, 'other_apps', {'models': exclude_models,
                                                  'use_natural_key': True})

        content = fp.getvalue()
        fp.close()

        context = self.get_global_context().copy()
        context.update({'items': content})

        return self.base_template.format(**context)

    def _get_dump_item_context(self, index, name, opts):
        """
        Return a formated dict context
        """
        c = {
            'item_no': index,
            'label': name,
            'name': name,
            'models': ' '.join(opts['models']),
            'natural_key': '',
        }
        if opts.get('use_natural_key', False):
            c['natural_key'] = ' -n'
        c.update(self.get_global_context())
        return c

    def _dumpdata_template(self, stringbuffer, index, name, opts):
        """
        StringIO "templates" to build a command line for 'dumpdata'
        """
        context = self._get_dump_item_context(index, name, opts)

        stringbuffer.write(self.dumper_item_template.format(**context))

        return stringbuffer

    def _loaddata_template(self, stringbuffer, index, name, opts):
        """
        StringIO "templates" to build a command line for 'loaddata'
        """
        context = self._get_dump_item_context(index, name, opts)

        stringbuffer.write(self.loadder_item_template.format(**context))

        return stringbuffer

    def generate_dumper(self, mapfile, names):
        """
        Build dumpdata commands
        """
        return self.build_template(mapfile, names, self._dumpdata_template)

    def generate_loader(self, mapfile, names):
        """
        Build loaddata commands
        """
        return self.build_template(mapfile, names, self._loaddata_template)


"""
Sample
"""
if __name__ == "__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help",
                                                       "dump_other_apps",
                                                       "exclude_apps="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        sys.exit(2)

    dump_other_apps = False
    exclude_apps = []
    for o, a in opts:
        if o in ("-h", "--help"):
            print HELP_MESSAGE
            sys.exit()
        elif o in ("--dump_other_apps",):
            dump_other_apps = True
        elif o in ("--exclude_apps",):
            exclude_apps = a.split(',')
        else:
            assert False, "unhandled option"

    sb = ScriptBuilder('dumps', dump_other_apps=dump_other_apps,
                       exclude_apps=exclude_apps)

    print "=== Dump map ==="
    print sb.generate_dumper("maps/djangocms-3.json", ['django-cms',
                                                       'porticus'])
    print
