.. _Django: https://www.djangoproject.com/
.. _Dr Dump: https://github.com/emencia/dr-dump

This is a Django data dump script generator.

It produces command line scripts usable within a Makefile or as a simple bash scripts to dump or load data with Django from the many app names you give it.

It need a dependancies map to know what is required to be dumped.

Maps
====

Currently it only have two maps one for "djangocms-2" and one for "djangocms-3" projects, and so it only knows about:

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

Note : Many app depends on Django's content types but we don't matter because it is automatically filled by Django and we should never try to dump/load it.

Format
******

* Dumps order does matter to respect module's dependancies;
* model or dependancy names can be string or either a list of names, take care that string is splitted on white spaces, if you use excude flag like '-e' with your model names, allways use a list;
* Circular dependancies is possible;

Sample map : ::

    [
        ('DUMP_NAME_KEY', {
            'use_natural_key': true,
            'models': 'mymodel',
            'dependancies': [],
        }),
    ]

Where :

DUMP_NAME_KEY
    Is the dump entry name, can be anything but commonly this is the app package name, this is what is used in embedded map files.
use_natural_key
    A boolean to define if the dump can use natural key, if not defined, a dump entry is assumed to support natural key.
models
    Is either a string of the model name or a list model names. Django accept either an app name from which it will take all its models, or a specific app model.
dependancies
    Either a string of another dump names to depends of. They will be taken also even if they haven't been explicitely requested from user.
