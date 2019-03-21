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
        if targeting_mode.startswith('hitlist@'):
            self.hitlist_path = targeting_mode.split('@')[1]
            return True
        # Default to false
        return False

    def acquire_targets(self):
        """Run execution logic for this targeting mode, returns new targets' URLs
        
        Returns:
            (list)
        """
        # FIXME FIXME FIXME THIS IS OLD CODE JUST COPY-PASTED IN HERE
        logger.info('Hitlist was specified @ ' + args.hitlist)
        # Is the given path valid for a file?
        hitlist_exists = False
        try:
            hitlist_exists = os.path.isfile(args.hitlist)
        except:
            pass
        if hitlist_exists:
            logger.info('Validated hitlist path, now starting to read contents...')
            hitlist_lines = []
            # Read it in as a text file
            try:
                f = open(args.hitlist, 'r')
                # Break down by lines
                hitlist_lines = f.readlines()
                f.close()
            except:
                logger.error('Something went wrong while opening hitlist file: ' + args.hitlist)
            # Validate then add each item to the hitlist
            for line in hitlist_lines:
                validated_line = get_validated_hitlist_line(line)
                if validated_line == None:
                    continue
                hitlist.append(line)
                # Also add root url to in-scope URLs if not already in there
                this_root_url = derive_root_url(line)
                add_to_inscope_urls(this_root_url)
        else:
            logger.error('Hitlist path was specified but appears invalid: ' + args.hitlist)
