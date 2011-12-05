import sys
import os
from poc.plugin import plugin

known_modules = {}

def scan_plugins():
    # Scan the plugins directory.
    # Inside, we expect to find folders naming modules containing .py files
    # containing classes with the same name as the .py file with a runloop()
    # method.
    pwd = os.path.dirname( os.path.realpath( __file__ ) )
    possible_modules = filter(lambda x: os.path.isdir(os.path.join("plugins",x)), os.listdir("plugins"))
    # Now we have only folders.  For each folder:
    for modulename in possible_modules:
        #print "considering plugins of module", modulename
        # Scan that folder for .py files.
        filenames = os.listdir(os.path.join("plugins",modulename))
        plugins = filter(lambda x: x.endswith(".py"), filenames)
        plugins = filter(lambda x: x != "__init__.py", plugins)
        plugins = map(lambda x: os.path.splitext(x)[0], plugins) #strip .py from end
        #print plugins
        for plugin in plugins:
            # Try importing that module:plugin and test if it has a runloop() method.
            __import__(".".join(["plugins", modulename, plugin]))
            if hasattr(getattr(getattr(getattr(__import__("plugins"), modulename), plugin), plugin), "runloop"):
                # If so, add it to the known_modules registry.
                #print "module %s has plugin %s with runloop" % (modulename, plugin)
                if modulename not in known_modules:
                    known_modules[modulename] = list()
                known_modules[modulename].append(plugin)

def usage():
    print 'Please provide the name of the module and plugin to launch.'
    print 'Known modules and plugins:'
    for module, plugins in known_modules.iteritems():
        for plugin in plugins:
            print "\t", " ".join([module,plugin])
    sys.exit(1)

if __name__ == "__main__":
    scan_plugins()
    if len(sys.argv) is not 3:
        usage()

    module = sys.argv[1]
    plugin_name = sys.argv[2]

    if module in known_modules and plugin_name in known_modules[module]:
        userplugin = plugin.load(module, plugin_name)
        userplugin.init()
        userplugin.runloop()
    else:
        print 'Unknown module:plugin requested: %s:%s' % (module, plugin_name)
        usage()
