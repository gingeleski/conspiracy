"""whatweb.py"""

try:
    from ._interfaces import IDomainPlugin
except:
    from _interfaces import IDomainPlugin

import subprocess


# Replace this with where your WhatWeb is...
WHATWEB_PATH       = 'C:\\Users\\gingeleski\\workspace\\whatweb\\whatweb'

WHATWEB_AGGRESSION = '4'             # value 1-4 as string, 1 is stealthy, 4 'heavy'
WHATWEB_USER_AGENT = 'WhatWeb/0.4.9' # user agent string that goes on requests


class WhatWebPlugin(IDomainPlugin):
    """Conspiracy plugin for WhatWeb scanner
    
    Params:
        name (str)
        type (_interfaces.PluginType)
    """

    def __init__(self):
        self.name = 'WhatWeb scanner'
        super(WhatWebPlugin, self).__init__(self.name)

    def executePerDomainAction(self, domain):
        """
        Runs WhatWeb against the given domain

        Params:
            domain (str)
        """
        whatweb_run = subprocess.run(['ruby', WHATWEB_PATH,\
                    '-a', WHATWEB_AGGRESSION, '-U', WHATWEB_USER_AGENT, domain], stdout=subprocess.PIPE)
        whatweb_output = whatweb_run.stdout.decode('utf-8')
        print(whatweb_output)


if __name__ == '__main__':
    test_target = 'gingeleski.com'
    ww = WhatWebPlugin()
    ww.executePerDomainAction(test_target)
