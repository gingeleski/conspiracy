"""sslyze.py"""


from _interfaces import IDomainPlugin

from sslyze.plugins.certificate_info_plugin import CertificateInfoScanCommand
from sslyze.plugins.compression_plugin import CompressionScanCommand
from sslyze.plugins.session_renegotiation_plugin import SessionRenegotiationScanCommand
from sslyze.server_connectivity_tester import ServerConnectivityTester
from sslyze.server_connectivity_tester import ServerConnectivityError
from sslyze.synchronous_scanner import SynchronousScanner


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
        try:
            sslyze_conn_test = ServerConnectivityTester(hostname=domain)
            sslyze_server_info = sslyze_conn_test.perform()
            sslyze_scanner = SynchronousScanner()
            sslyze_results = sslyze_scanner.run_scan_command(sslyze_server_info, CertificateInfoScanCommand())
            sslyze_result_lines = sslyze_results.as_text()
            for line in sslyze_result_lines:
                #logging.info(line)
                print(line)
            sslyze_results = sslyze_scanner.run_scan_command(sslyze_server_info, SessionRenegotiationScanCommand())
            sslyze_result_lines = sslyze_results.as_text()
            for line in sslyze_result_lines:
                #logging.info(line)
                print(line)
            sslyze_results = sslyze_scanner.run_scan_command(sslyze_server_info, CompressionScanCommand())
            sslyze_result_lines = sslyze_results.as_text()
            for line in sslyze_result_lines:
                #logging.info(line)
                print(line)
        except ServerConnectivityError as e:
            # Could not establish a TLS/SSL connection to the server
            #logging.error(f'sslyze ended early, could not connect to {e.server_info.hostname}: {e.error_message}')
            print(f'sslyze ended early, could not connect to {e.server_info.hostname}: {e.error_message}')
