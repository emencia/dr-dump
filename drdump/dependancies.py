"""
Dependancies manager
"""
import sys
import collections
import json
import os.path

if sys.version_info > (3, 0):
    string_types = (str, )
else:
    string_types = (basestring, )   # noqa


class DependanciesManager(object):
    """
    Object to store a catalog of available dump dependancies with some methods
    to get a clean dump map with their required dependancies.
    """

    def __init__(self, dependencies_map, silent_key_error=False):
        self.silent_key_error = silent_key_error
        self._map = dependencies_map

        self.deps_index = collections.defaultdict(set)
        for key, value in self._map.items():
            for k in value.get('dependancies') or []:
                self.deps_index[k].add(key)

    @classmethod
    def from_json_filename(cls, filename, **kw):
        if filename:
            if '/' not in filename and '.' not in filename:
                map_file_path = os.path.join(os.path.dirname(__file__), 'maps/{}.json'.format(filename))
            else:
                map_file_path = filename
        else:
            map_file_path = os.path.join(os.path.dirname(__file__), 'maps/djangocms-3.json')

        with open(map_file_path, 'r') as mapfile:
            dumps_map = json.load(mapfile)

        return cls.from_json_data(dumps_map, **kw)

    @classmethod
    def from_json_data(cls, json_data, **kw):
        """
        Perform string to list translation and dependancies indexing when
        setting an item
        """
        def prepare(name, value):
            assert isinstance(name, string_types) and isinstance(value, collections.Mapping)
            if 'models' not in value:
                value['models'] = []
            elif isinstance(value['models'], string_types):
                value['models'] = value['models'].split()

            if 'dependancies' in value:
                if isinstance(value['dependancies'], string_types):
                    value['dependancies'] = value['dependancies'].split()
            return name, value

        return cls(collections.OrderedDict(prepare(name, value) for name, value in json_data), **kw)

    def __getitem__(self, name):
        return self._map[name]

    def get_dump_names(self, names, dumps=None):
        """
        Find and return all dump names required (by dependancies) for a given
        dump names list

        Beware, the returned name list does not respect order, you should only
        use it when walking throught the "original" dict builded by OrderedDict
        """
        # Default value for dumps argument is an empty set (setting directly
        # as a python argument would result as a shared value between
        # instances)
        if dumps is None:
            dumps = set()

        # Add name to the dumps and find its dependancies
        for item in names:
            if item not in self._map:
                if not self.silent_key_error:
                    raise KeyError("Dump name '{0}' is unknown".format(item))
                else:
                    continue

            dumps.add(item)

            # Add dependancies names to the dumps
            deps = self._map[item].get('dependancies') or []
            dumps.update(deps)

        # Avoid maximum recursion when we already found all the dependancies
        if names == dumps:
            return dumps

        # Seems we don't have found other dependancies yet, recurse to do it
        return self.get_dump_names(dumps.copy(), dumps)

    def get_dump_order(self, names):
        """
        Return ordered dump names required for a given dump names list
        """
        found_names = self.get_dump_names(set(names))
        return [(item, self._map[item]) for item in self._map if item in found_names]


"""
Sample
"""
if __name__ == "__main__":
    apps = ['django-cms', 'porticus']
    if len(sys.argv) > 1:
        map_file_path = sys.argv[1]
        apps = sys.argv[2:] or apps
    else:
        map_file_path = 'djangocms-3'

    dump_manager = DependanciesManager.from_json_filename(map_file_path)
    sys.stdout.write('{}\n'.format(dump_manager.get_dump_order(apps)))
