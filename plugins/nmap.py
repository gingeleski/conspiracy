"""nmap.py"""


from _interfaces import IDomainPlugin


class NmapPlugin(IDomainPlugin):
    """Conspiracy plugin for nmap port scan
    
    Params:
        name (str)
        type (_interfaces.PluginType)
    """

    def __init__(self):
        self.name = 'nmap port scan'
        super(NmapPlugin, self).__init__(self.name)

    def executePerDomainAction(self, domain):
        """
        TODO fill this in better

        Params:
            domain (str)
        """
        # TODO
        print(domain)
