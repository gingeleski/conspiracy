"""_interfaces.py

Interface base classes for writing Conspiracy plugins.
"""


import abc
from enum import Enum


class PluginType(Enum):
    """Enum class that defines types of Conspiracy plugins."""
    BROWSER_PAGE = 1
    DOMAIN = 2


class IPlugin(abc.ABC):
    """Abstract interface base class for a Conspiracy plugin.

    Params:
        name (str)
        type (PluginType)
    """

    @abc.abstractmethod
    def __init__(self, name):
        """Abstract - constructor, should set plugin name and type.

        Params:
            name (str)
        """
        pass

    def get_name(self):
        """Get name of this plugin.

        Returns:
            (str)
        """
        return self.name

    def get_type(self):
        """Get type of this plugin.

        Returns:
            (.PluginType)
        """
        return self.type


class IBrowserPagePlugin(IPlugin):
    """Abstract base class for a 'browser page' Conspiracy plugin. Extends .IPlugin class.

    Params:
        name (str)
        type (.PluginType)
    """

    def __init__(self, name):
        """
        Constructor, sets plugin name and type.

        Params:
            name (str)
        """
        self.name = name
        self.type = PluginType.BROWSER_PAGE

    @abc.abstractmethod
    def executePerPageAction(self, page):
        """Abstract - perform an action on a Pyppeteer / headless Chrome page.

        Params:
            page (pyppeteer.page.Page)
        """
        pass


class IDomainPlugin(IPlugin):
    """Abstract base class for a 'domain' Conspiracy plugin. Extends .IPlugin class.

    Params:
        name (str)
        type (.PluginType)
    """

    def __init__(self, name):
        """Constructor, sets plugin name and type.

        Params:
            name (str)
        """
        self.name = name
        self.type = PluginType.DOMAIN

    @abc.abstractmethod
    def executePerDomainAction(self, domain):
        """Abstract - perform an action on an in-scope domain or URL.

        Params:
            domain (str)
        """
        pass
