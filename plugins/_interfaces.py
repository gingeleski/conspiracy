"""_interfaces.py

Interface base classes for writing Conspiracy plugins.
"""


import abc
from enum import Enum


class PluginType(Enum):
    """Enum class that defines types of Conspiracy plugins."""
    BROWSER_PAGE = 1
    DOMAIN = 2
    AUXILIARY = 3


class IPlugin(abc.ABC):
    """Abstract interface base class for a Conspiracy plugin.

    Params:
        name (str)
        type (PluginType)
        requirements (list)
    """

    @abc.abstractmethod
    def __init__(self, name, requirements):
        """Abstract - constructor, should set plugin name and type.

        Params:
            name (str)
            requirements (list)
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

    def __init__(self, name, requirements):
        """Constructor, sets plugin name and type.

        Params:
            name (str)
            requirements (list)
        """
        self.name = name
        self.type = PluginType.BROWSER_PAGE
        self.requirements = requirements

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

    def __init__(self, name, requirements):
        """Constructor, sets plugin name and type.

        Params:
            name (str)
            requirements (list)
        """
        self.name = name
        self.type = PluginType.DOMAIN
        self.requirements = requirements

    @abc.abstractmethod
    def executePerDomainAction(self, domain):
        """Abstract - perform an action on an in-scope domain or URL.

        Params:
            domain (str)
        """
        pass


class IAuxiliaryPlugin(IPlugin):
    """Base class for an 'auxiliary' Conspiracy plugin. Extends .IPlugin class.

    Params:
        name (str)
        type (.PluginType)
        requirements (list)
    """

    def __init__(self, name, requirements):
        """Constructor, sets plugin name and type.

        Params:
            name (str)
            requirements (list)
        """
        self.name = name
        self.type = PluginType.AUXILIARY
        self.requirements = requirements
