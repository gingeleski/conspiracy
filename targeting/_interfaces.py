"""_interfaces.py

Interface base classes for writing Conspiracy targeting modes.
"""

import abc
import logging


class ITargetingMode(abc.ABC):
    """Abstract interface base class for a Conspiracy targeting mode.

    Params:
        name (str)
    """

    @abc.abstractmethod
    def __init__(self, name):
        """Abstract - constructor, should set targeting mode name.

        Params:
            name (str)
        """
        pass

    def get_name(self):
        """Get name of this targeting mode.

        Returns:
            (str)
        """
        return self.name

    @abc.abstractmethod
    def check_arg_match(self, arg_string):
        """Returns whether the given argument value matches this mode.

        Params:
            arg_string (str)

        Returns:
            (bool)
        """
        pass

    @abc.abstractmethod
    def acquire_targets(self):
        """Run execution logic for this targeting mode."""
        pass
