"""crawl.py"""

from ._interfaces import ITargetingMode

class CrawlTargeting(ITargetingMode):
    """Conspiracy targeting mode that crawls from existing target(s)

    Params:
        name (str)
    """

    def __init__(self):
        self.name = 'Crawl'

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
