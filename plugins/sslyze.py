"""sslyze.py"""


from _interfaces import IDomainPlugin


class SslyzePlugin(IDomainPlugin):
    """Conspiracy plugin for sslyze certificate information
    
    Params:
        name (str)
        type (_interfaces.PluginType)
    """

    def __init__(self):
        self.name = 'sslyze certificate information'
        super(SslyzePlugin, self).__init__(self.name)

    def executePerDomainAction(self, domain):
        """
        TODO fill this in better

        Params:
            domain (str)
        """
        # TODO
        print(domain)
