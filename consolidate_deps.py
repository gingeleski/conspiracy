"""consolidate_deps.py
"""

from plugins import *

#######################################################################################################################

class DependenciesHolder:
    """
    TODO document me
    """

    def __init__(self):
        """
        TODO document me
        """
        self.dependencies = []

    def add(self, obj_to_add):
        """
        TODO document me
        """
        if len(self.dependencies) == 0:
            self.dependencies.append(obj_to_add)
        elif len(self.dependencies) == 1:
            # TODO
            pass
        else:
            # TODO
            pass

#######################################################################################################################

BROWSER_PAGE_PLUGINS = [cls() for cls in IBrowserPagePlugin.__subclasses__()]
DOMAIN_PLUGINS = [cls() for cls in IDomainPlugin.__subclasses__()]
AUXILIARY_PLUGINS = [cls() for cls in IAuxiliaryPlugin.__subclasses__()]
ALL_PLUGINS = BROWSER_PAGE_PLUGINS + DOMAIN_PLUGINS + AUXILIARY_PLUGINS

#######################################################################################################################

if __name__ == '__main__':
    dependencies = DependenciesHolder()
    # TODO get existing dependencies
    for plugin in ALL_PLUGINS:
        for dep in plugin.dependencies:
            if '==' in dep:
                version_spec = '=='
            elif '>=' in dep:
                version_spec = '>='
            elif '<=' in dep:
                version_spec = '<='
            else:
                raise RuntimeError('Unexpected version specifier in dependency string ' + dep)
            dep_tuple = dep.split(version_spec).insert(1, version_spec)
            dependencies.add(dep_tuple)
    # TODO replace existing requirements.txt with a new one
