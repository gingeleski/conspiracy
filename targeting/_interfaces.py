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

    def __init__(self):
        """Abstract - constructor, should set targeting mode name."""
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
        """Run execution logic for this targeting mode, returns new targets' URLs
        
        Returns:
            (list)
        """
        pass
