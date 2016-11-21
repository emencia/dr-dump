.. _Django: https://www.djangoproject.com/
.. _Dr Dump: https://github.com/emencia/dr-dump

This is a Django data dump script generator. It either generates a script to
call dumpdata or does dumpddata itself.

It may produce command line scripts usable within a Makefile or as a simple
bash scripts to dump or load data with Django from the many app names you give
it.

It need a dependancies map to know what is required to be dumped.

Maps
====

Currently it only have two maps one for "djangocms-2" and one for "djangocms-3"
projects, and so it only knows about:

* Django contrib auth;
* Django sites;
* emencia.django.countries;
* contact_form;
* DjangoCMS and its common plugins;
* Zinnia;
* Porticus;
* South;
* django-tagging;
* django-taggit;
* easy-thumbnails;
* django-filer;
* django-google-tools;
* emencia-django-socialaggregator;
* emencia-django-slideshows;

Note : Many app depends on Django's content types but we don't bother because
it is automatically filled by Django and we should never try to dump/load it.

Format
******

* Dumps order does matter to respect module's dependancies;
* model or dependancy names can be string or either a list of names, take care
  that string is splitted on white spaces, if you use excude flag like '-e'
  with your model names, always use a list;
* Circular dependancies is possible;

Sample map : ::

    [
        ('DUMP_NAME_KEY', {
            'use_natural_key': true,
            'models': 'mymodel',
            'exclude_models': 'my_excluded_model',
            'dependancies': [],
        }),
    ]

Where :

DUMP_NAME_KEY
    Is the dump entry name, can be anything but commonly this is the app
    package name, this is what is used in embedded map files.
use_natural_key
    A boolean to define if the dump can use natural key, if not defined, a dump
    entry is assumed to support natural key.
models
    Is either a string of the model name or a list model names. Django accept
    either an app name from which it will take all its models, or a specific
    app model.
exclude_models
    Is either a string of the model name or a list model names. It will exclude
    all those models from the dumpdata command.
dependancies
    Either a string of another dump names to depends of. They will be taken
    also even if they haven't been explicitely requested from user.


Codec
=====

DrDump will use a dump codec to tranform the list of dump instructions (models
or apps to dump, excluded models, usage of natural keys) into actions: actual
call of management commands or script generation.


Loading data
============

DrDump will generate a manifest file with the list of the fixtures it
has generated.

DrDump can automate the process of loading the data it has generated. The
Python module drdump.load can load the manifest::

    python -m drdump.load <manifest file>

The management command dr_load does the same thing::

    manage.py dr_load <manifest>


Django
======

DrDump provides a management command to launch the dump or generate the dump
commands::

    manage.py dr_dump ...

It will take command line arguments that defaults to settings.

DRDUMP_MAP_FILE
    The path to the map file
DRDUMP_OTHER_APPS
    A boolean that decides if all unlisted apps are also dumped
DRDUMP_EXCLUDE_APPS
    A list of applications or models to exclude from the dump
DRDUMP_OPTIONS
    The options of the dump codec
