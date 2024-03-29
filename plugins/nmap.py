"""nmap.py"""

from ._interfaces import IDomainPlugin

# Note: more specific imports are in-method


NMAP_SCAN_TYPE = 'QUICK'


class NmapPlugin(IDomainPlugin):
    """Conspiracy plugin for nmap port scan
    
    Params:
        name (str)
        type (_interfaces.PluginType)
        requirements (list)
        logger (Logger)
    """

    def __init__(self):
        self.name = 'nmap port scan'
        self.requirements = [ 'python-nmap==0.6.1' ]
        super(NmapPlugin, self).__init__(self.name, self.requirements)

    def executePerDomainAction(self, domain):
        """
        This plugin's per-domain action is to execute an nmap scan of configurable intensity

        Params:
            domain (str)
        """
        import nmap
        skip_nmap = False
        try:
            nm = nmap.PortScanner()
        except nmap.nmap.PortScannerError as e:
            # Most likely, nmap is not on the path
            self.logger.error(f'Could not launch nmap module - is it on the path? : {e.error_message}')
            skip_nmap = True
        if False == skip_nmap:
            nmap_args = None
            # Start nmap scan type logical ladder
            if NMAP_SCAN_TYPE.upper() == 'INTENSE':
                nmap_args = '-T4 -A -v'
            elif NMAP_SCAN_TYPE.upper() == 'INTENSE_PLUS_UDP':
                nmap_args = '-sS -sU -T4 -A -v'
            elif NMAP_SCAN_TYPE.upper() == 'INTENSE_ALL_TCP':
                nmap_args = '-p 1-65535 -T4 -A -v'
            elif NMAP_SCAN_TYPE.upper() == 'INTENSE_NO_PING':
                nmap_args = '-T4 -A -v -Pn'
            elif NMAP_SCAN_TYPE.upper() == 'PING':
                nmap_args = '-sn'
            elif NMAP_SCAN_TYPE.upper() == 'QUICK':
                nmap_args = '-T4 -F'
            elif NMAP_SCAN_TYPE.upper() == 'QUICK_PLUS':
                nmap_args = '-sV -T4 -O -F --version-light'
            elif NMAP_SCAN_TYPE.upper() == 'QUICK_TRACEROUTE':
                nmap_args = '-sn --traceroute'
            elif NMAP_SCAN_TYPE.upper() == 'SLOW_COMPREHENSIVE':
                nmap_args = '-sS -sU -T4 -A -v -PE -PP -PS80,443 -PA3389 -PU40125 -PY -g 53 --script "default or (discovery and safe)"'
            # End nmap scan type logical ladder
            if nmap_args != None:
                nmap_scan_result = nm.scan(hosts=domain, arguments=nmap_args)
            else:
                nmap_scan_result = nm.scan(hosts=domain)
            self.logger.info(nmap_scan_result)


if __name__ == '__main__':
    exit
