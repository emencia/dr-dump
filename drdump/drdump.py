# -*- coding: utf-8 -*-

from __future__ import absolute_import


import pkg_resources


class ApplicationsList(object):
    def __init__(self, apps):
        self._apps = apps

    def __iter__(self):
        return iter(self._apps)

    @classmethod
    def from_packages(cls, extra_apps=()):
        packages = [d for d in pkg_resources.working_set]
        apps = {p.key for p in packages}
        apps.update(extra_apps)
        return cls(apps)


class Drdump(object):
    def __init__(self, dependencies, names, exclude_apps=None, dump_other_apps=True):
        self.dependencies = dependencies
        self.names = names
        self.exclude_apps = list(exclude_apps) if exclude_apps else []
        self.dump_other_apps = dump_other_apps

    def __call__(self, output_codec):
        with output_codec as output:
            for name, context in self:
                output(name, context)

    def __iter__(self):
        """
        Build source from global and item templates
        """

        exclude_models = set(self.exclude_apps)

        for name, item in self.dependencies.get_dump_order(self.names):
            yield name, item
            exclude_models.update(item['models'])

        if self.dump_other_apps:
            yield 'other_apps', {
                'exclude_models': list(exclude_models),
                'use_natural_key': True
            }
