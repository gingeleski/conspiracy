"""
_interfaces.py

Conspiracy plugin interfaces

"""

import abc

########################################################################################################################

class IPlugin(abc.ABC):

    @abc.abstractmethod
    def registerPluginCallbacks(self, callbacks):
        pass

########################################################################################################################

class IBrowserPagePlugin(IPlugin):

    @abc.abstractmethod
    def registerPerPageActions(self, callbacks):
        pass

########################################################################################################################

class IDomainPlugin(IPlugin):

    @abc.abstractmethod
    def registerPerDomainActions(self, callbacks):
        pass
