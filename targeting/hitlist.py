"""hitlist.py"""

from ._interfaces import ITargetingMode
from pathlib import Path

import logging
import os


class HitlistTargeting(ITargetingMode):
    """Conspiracy targeting mode that takes a list of URLs

    Params:
        name (str)
        logger (Logger)
        hitlist_path (object)
    """

    def __init__(self):
        self.name = 'Hitlist'
        self.logger = logging.getLogger('conspiracy')

    def check_arg_match(self, arg_string):
        """Returns whether the given argument value matches this mode.

        Params:
            arg_string (str)

        Returns:
            (bool)
        """
        if arg_string.startswith('hitlist@'):
            self.hitlist_path = arg_string.split('@')[1]
            return True
        # Default to false
        return False

    def acquire_targets(self, inscope_urls={}):
        """Run execution logic for this targeting mode, returns new targets' URLs
        
        Params:
            inscope_urls (dict)

        Returns:
            (list)
        """
        target_list_to_return = []
        self.logger.info('Hitlist was specified @ ' + self.hitlist_path)
        # Take the path from string to object, and try to orient it correctly given dir structure
        if not self.hitlist_path.startswith('/') or self.hitlist_path.startswith('\\'):
            self.hitlist_path = os.sep + self.hitlist_path
        self.hitlist_path = Path(os.path.dirname(os.path.abspath(__file__)) + os.sep + '..' + self.hitlist_path)
        # Is the given path valid for a file?
        hitlist_exists = False
        try:
            hitlist_exists = os.path.isfile(self.hitlist_path)
        except:
            pass
        if hitlist_exists:
            self.logger.info('Validated hitlist path, now starting to read contents...')
            hitlist_lines = []
            # Read it in as a text file
            try:
                f = open(str(self.hitlist_path), 'r')
                # Break down by lines
                hitlist_lines = f.readlines()
                f.close()
            except:
                self.logger.error('Something went wrong while opening hitlist file: ' + str(self.hitlist_path))
            # Validate then add each item to target_list_to_return
            for line in hitlist_lines:
                validated_line = self.get_validated_hitlist_line(line)
                if validated_line == None:
                    continue
                target_list_to_return.append(line)
        else:
            self.logger.error('Hitlist path was specified but appears invalid: ' + str(self.hitlist_path))
        return target_list_to_return

    def get_validated_hitlist_line(self, line):
        """
        Cleans one line of hitlist data read in from whatever_file.txt

        Params:
            line (str)

        Returns:
            (str)
        """
        # Weed out blank/extra lines
        if len(line.strip()) == 0:
            return None
        # Allow lines prepended with # as comments
        elif line.startswith('#'):
            return None
        validated_line = ''
        if False == line.startswith('http://') or False == line.startswith('https://'):
            validated_line += 'http://'
        validated_line += line.replace('\n','') # Strip any line breaks remaining...
        return validated_line
