"""openvas.py"""

from ._interfaces import IDomainPlugin


class OpenVASPlugin(IDomainPlugin):
    """Conspiracy plugin for OpenVAS
    
    Params:
        name (str)
        type (_interfaces.PluginType)
        requirements (list)
        logger (Logger)
    """

    def __init__(self):
        self.name = 'OpenVAS scan'
        self.requirements = []
        super(OpenVASPlugin, self).__init__(self.name, self.requirements)

    def executePerDomainAction(self, domain):
        """
        This plugin's per-domain action is to execute an OpenVAS scan

        Params:
            domain (str)
        """
        pass # TODO


if __name__ == '__main__':
    exit
