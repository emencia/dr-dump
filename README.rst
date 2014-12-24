.. _Django: https://www.djangoproject.com/
.. _Dr Dump: https://github.com/emencia/dr-dump

This is a Django data dump script generator.

It produces command line scripts usable within a Makefile or as a simple shell script to dump or load data with Django from the many app names you give it.

It need a dependancies map to know what is required to be dumped. Currently it only have two maps one for "djangocms-2" and one for "djangocms-3" projects, and so it only knows about:

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
