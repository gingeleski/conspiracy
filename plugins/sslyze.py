"""sslyze.py"""


from ._interfaces import IDomainPlugin


# Note: more specific imports are in-method


class SslyzePlugin(IDomainPlugin):
    """Conspiracy plugin for sslyze certificate information
    
    Params:
        name (str)
        type (_interfaces.PluginType)
        requirements (list)
        logger (Logger)
    """

    def __init__(self):
        self.name = 'sslyze certificate information'
        self.requirements = [\
            'asn1crypto==0.24.0',\
            'cffi==1.12.1',\
            'cryptography==2.5',\
            'nassl==2.1.2',\
            'pycparser==2.19',\
            'six==1.12.0',\
            'sslyze==2.0.6',\
            'tls-parser==1.2.1'\
        ]
        super(SslyzePlugin, self).__init__(self.name, self.requirements)

    def executePerDomainAction(self, domain):
        """
        This plugin's per-domain action is to run a barrage of sslyze certificate tests

        Params:
            domain (str)
        """
        from sslyze.plugins.certificate_info_plugin import CertificateInfoScanCommand
        from sslyze.plugins.compression_plugin import CompressionScanCommand
        from sslyze.plugins.session_renegotiation_plugin import SessionRenegotiationScanCommand
        from sslyze.server_connectivity_tester import ServerConnectivityTester
        from sslyze.server_connectivity_tester import ServerConnectivityError
        from sslyze.synchronous_scanner import SynchronousScanner
        try:
            sslyze_conn_test = ServerConnectivityTester(hostname=domain)
            sslyze_server_info = sslyze_conn_test.perform()
            sslyze_scanner = SynchronousScanner()
            sslyze_results = sslyze_scanner.run_scan_command(sslyze_server_info, CertificateInfoScanCommand())
            sslyze_result_lines = sslyze_results.as_text()
            for line in sslyze_result_lines:
                self.logger.info(line)
            sslyze_results = sslyze_scanner.run_scan_command(sslyze_server_info, SessionRenegotiationScanCommand())
            sslyze_result_lines = sslyze_results.as_text()
            for line in sslyze_result_lines:
                self.logger.info(line)
            sslyze_results = sslyze_scanner.run_scan_command(sslyze_server_info, CompressionScanCommand())
            sslyze_result_lines = sslyze_results.as_text()
            for line in sslyze_result_lines:
                self.logger.info(line)
        except ServerConnectivityError as e:
            # Could not establish a TLS/SSL connection to the server
            self.logger.error(f'sslyze ended early, could not connect to {e.server_info.hostname}: {e.error_message}')
            print(f'sslyze ended early, could not connect to {e.server_info.hostname}: {e.error_message}')


if __name__ == '__main__':
    exit
