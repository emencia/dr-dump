"""
Django datas dump script generator
"""
import StringIO
from collections import OrderedDict

DUMP_TEMPLATE = """{silencer}echo "* {label}: dump.{item_no}.{name}.json"
{silencer}{django_instance} dumpdata {natural_key}--indent=2 {models} > {dump_dir}/dump.{item_no}.{name}.json

"""

LOAD_TEMPLATE = """{silencer}echo "* Importing: dump.{item_no}.{name}.json"
{silencer}{django_instance} loaddata {dump_dir}/dump.{item_no}.{name}.json

"""

class DataDumpScriptMakefile(OrderedDict):
    """
    Object to store a catalog of available dumps with some methods to get a 
    clean dump map with their required dependancies.
    
    * Dumps order does matter to respect module's dependancies;
    * model or dependancy names can be string or either a list of names, take care that string is splitted on white spaces, if you use excude flag like '-e' with your model names, allways use a list;
    * Circular dependancies is possible;
    
    [
        ('DUMP_NAME_KEY', {
            'use_natural_key': USE NATURAL KEY? BOOLEAN,
            'models': MODEL NAME STRING OR MODEL NAMES LIST,
            'dependancies': DEPENDANCY DUMP NAME STRING OR DEPENDANCY DUMP NAMES LIST,
        }),
    ]
    """
    deps_index = {}
    makefile_silencer = '@' # Make it empty to avoid silencer like without a Makefile
    django_instance_path = 'bin/django-instance'
    dumps_path = 'dumps' # Must not end with a slash
    
    def __init__(self, *args, **kwargs):
        self.silent_key_error = kwargs.pop('silent_key_error', False)
        super(DataDumpScriptMakefile, self).__init__(*args, **kwargs)
    
    def __setitem__(self, key, value):
        """
        Perform string to list translation and dependancies indexing when setting an item
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
            #print "* Wanted:", names
            
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
        
        # Seem we don't have finded other dependancies yet, recurse to do it
        return self.get_dump_names(dumps.copy(), dumps)

    def get_dump_order(self, names):
        """
        Return ordered dump names required for a given dump names list
        """
        finded_names = self.get_dump_names(names)
        return [item for item in self if item in finded_names]

    def build_template(self, names, renderer):
        """
        Return a string contained all dumpdata lines for the given dump names
        """
        fp = StringIO.StringIO()
        
        for i, item in enumerate(self.get_dump_order(names), start=1):
            fp = renderer(fp, i, item, self.__getitem__(item))
        
        content = fp.getvalue()
        fp.close()
        return content
    

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
            
            'silencer': self.makefile_silencer,
            'django_instance': self.django_instance_path,
            'dump_dir': self.dumps_path,
        }
        if opts.get('use_natural_key', False):
            c['natural_key'] = ' -n'
        return c


    def build_dumpdata(self, names):
        """
        Build dumpdata commands
        """
        return self.build_template(names, self._dumpdata_template)

    def _dumpdata_template(self, stringbuffer, index, name, opts):
        """
        StringIO "templates" to build a command line for 'dumpdata'
        """
        context = self._get_dump_item_context(index, name, opts)
        
        stringbuffer.write(DUMP_TEMPLATE.format(**context))
        
        return stringbuffer


    def build_loaddata(self, names):
        """
        Build loaddata commands
        """
        return self.build_template(names, self._loaddata_template)

    def _loaddata_template(self, stringbuffer, index, name, opts):
        """
        StringIO "templates" to build a command line for 'loaddata'
        """
        context = self._get_dump_item_context(index, name, opts)
        
        stringbuffer.write(LOAD_TEMPLATE.format(**context))
        
        return stringbuffer


class DataDumpScriptCLI(DataDumpScriptMakefile):
    """
    Same as DataDumpScriptMakefile but for a simple shell script, so disable the silencer
    """
    makefile_silencer = ''


"""
Sample
"""
if __name__ == "__main__":
    import json
    
    AVAILABLE_DUMPS = json.load(open("maps/djangocms-3.json", "r"))
    
    dump_manager = DataDumpScriptMakefile(AVAILABLE_DUMPS)

    print "=== Dump map ==="
    print dump_manager.build_dumpdata(['djangocms','porticus',])
    print
    print

    #print dump_manager.build_loaddata(['deep-foo','socialaggregator',])
    #print
