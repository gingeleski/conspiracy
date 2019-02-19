"""nslookup.py"""


from ._interfaces import IDomainPlugin

import socket


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
        ip_addresses = self.get_ip_addresses_cmd(domain)
        if ip_addresses == None: # Python-native backup
            ip_addresses = self.get_ip_addresses_native(domain)
        if len(ip_addresses) > 0:
            #logging.info('\t' + 'IP addresses:')
            print('\t' + 'IP addresses:')
            #logging.info('\t\t' + str(ip_addresses))
            print('\t\t' + str(ip_addresses))
        aliases = self.get_aliases_cmd(domain)
        if aliases == None: # Python-native backup
            aliases = self.get_aliases_native(domain)
        if len(aliases) > 0:
            #logging.info('\t' + 'Aliases:')
            print('\t' + 'Aliases:')
            #logging.info('\t\t' + str(aliases))
            print('\t\t' + str(aliases))

    def get_ip_addresses_cmd(self, domain):
        # TODO
        return None

    def get_aliases_cmd(self, domain):
        # TODO
        return None

    def get_ip_addresses_native(self, domain):
        """
        Returns one or more IP address strings that respond as the provided
        domain name
        """
        try:
            data = socket.gethostbyname_ex(domain)
            ip_addresses = repr(data[2])
            return ip_addresses
        except Exception:
            return None

    def get_aliases_native(self, domain):
        """
        Returns one or more aliases for the provided domain
        """
        try:
            data = socket.gethostbyname_ex(domain)
            aliases = repr(data[1])
            return aliases
        except Exception:
            return None


if __name__ == '__main__':
    exit
