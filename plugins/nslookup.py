"""nslookup.py"""


from ._interfaces import IDomainPlugin

import socket


class NslookupPlugin(IDomainPlugin):
    """Conspiracy plugin for nslookup
    
    Params:
        name (str)
        type (_interfaces.PluginType)
        requirements (list)
        logger (Logger)
    """

    def __init__(self):
        self.name = 'nslookup'
        self.requirements = []
        super(NslookupPlugin, self).__init__(self.name, self.requirements)

    def executePerDomainAction(self, domain):
        """
        This plugin's per-domain action is to get relevant nslookup info

        Params:
            domain (str)
        """
        ip_addresses = self.get_ip_addresses_cmd(domain)
        if ip_addresses == None: # Python-native backup
            ip_addresses = self.get_ip_addresses_native(domain)
        if len(ip_addresses) > 0:
            self.logger.info('\t' + 'IP addresses:')
            self.logger.info('\t\t' + str(ip_addresses))
        aliases = self.get_aliases_cmd(domain)
        if aliases == None: # Python-native backup
            aliases = self.get_aliases_native(domain)
        if len(aliases) > 0:
            self.logger.info('\t' + 'Aliases:')
            self.logger.info('\t\t' + str(aliases))

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
