"""
Dependancies manager
"""
from collections import OrderedDict


class DependanciesManager(OrderedDict):
    """
    Object to store a catalog of available dump dependancies with some methods
    to get a clean dump map with their required dependancies.
    """
    deps_index = {}

    def __init__(self, *args, **kwargs):
        self.silent_key_error = kwargs.pop('silent_key_error', False)
        super(DependanciesManager, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        """
        Perform string to list translation and dependancies indexing when
        setting an item
        """
        if isinstance(value['models'], basestring):
            value['models'] = value['models'].split()

        if 'dependancies' in value:
            if isinstance(value['dependancies'], basestring):
                value['dependancies'] = value['dependancies'].split()

            for k in value['dependancies']:
                if k not in self.deps_index:
                    self.deps_index[k] = set([])
                self.deps_index[k].add(key)
        OrderedDict.__setitem__(self, key, value)

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
            dumps = set([])

        # Add name to the dumps and find its dependancies
        for item in names:
            if item not in self:
                if not self.silent_key_error:
                    raise KeyError("Dump name '{0}' is unknowed".format(item))
                else:
                    continue

            dumps.add(item)

            # Add dependancies names to the dumps
            deps = self.__getitem__(item).get('dependancies', [])
            dumps.update(deps)

        # Avoid maximum recursion when we allready find all dependancies
        if names == dumps:
            return dumps

        # Seems we don't have finded other dependancies yet, recurse to do it
        return self.get_dump_names(dumps.copy(), dumps)

    def get_dump_order(self, names):
        """
        Return ordered dump names required for a given dump names list
        """
        finded_names = self.get_dump_names(names)
        return [item for item in self if item in finded_names]


"""
Sample
"""
if __name__ == "__main__":
    import json

    AVAILABLE_DUMPS = json.load(open("maps/djangocms-3.json", "r"))

    dump_manager = DependanciesManager(AVAILABLE_DUMPS, silent_key_error=True)

    print dump_manager.get_dump_order(['django-cms', 'porticus'])
    print
