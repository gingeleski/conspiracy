"""nmap.py"""


from ._interfaces import IDomainPlugin

import nmap


NMAP_SCAN_TYPE = 'PING'


class NmapPlugin(IDomainPlugin):
    """Conspiracy plugin for nmap port scan
    
    Params:
        name (str)
        type (_interfaces.PluginType)
    """

    def __init__(self):
        self.name = 'nmap port scan'
        self.dependencies = [ 'python-nmap==0.6.1' ]
        super(NmapPlugin, self).__init__(self.name, self.dependencies)

    def executePerDomainAction(self, domain):
        """
        TODO fill this in better

        Params:
            domain (str)
        """
        skip_nmap = False
        try:
            nm = nmap.PortScanner()
        except nmap.nmap.PortScannerError as e:
            # Most likely, nmap is not on the path
            #logging.error(f'Error launching nmap module - is it on the path? : {e.error_message}')
            print(f'Error launching nmap module - is it on the path? : {e.error_message}')
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
                nmap_scan_result = nm.scan(hosts=domain, arguments='-sS -sU -T4 -A -v')
            else:
                nmap_scan_result = nm.scan(hosts=domain)
            #logging.info(nmap_scan_result)
            print(nmap_scan_result)


if __name__ == '__main__':
    exit
