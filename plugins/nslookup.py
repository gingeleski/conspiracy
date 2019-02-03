"""nslookup.py"""


from _interfaces import IDomainPlugin


class NslookupPlugin(IDomainPlugin):
    """Conspiracy plugin for nslookup
    
    Params:
        name (str)
        type (_interfaces.PluginType)
    """

    def __init__(self):
        self.name = 'nslookup'
        super(NslookupPlugin, self).__init__(self.name)

    def executePerDomainAction(self, domain):
        """
        TODO fill this in better

        Params:
            domain (str)
        """
        # TODO
        print(domain)
