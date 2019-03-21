"""hitlist.py"""

from ._interfaces import ITargetingMode

class HitlistTargeting(ITargetingMode):
    """Conspiracy targeting mode that takes a list of URLs

    Params:
        name (str)
    """

    def __init__(self):
        self.name = 'Hitlist'

    def check_arg_match(self, arg_string):
        """Returns whether the given argument value matches this mode.

        Params:
            arg_string (str)

        Returns:
            (bool)
        """
        return False

    def acquire_targets(self):
        """Run execution logic for this targeting mode."""
        pass
