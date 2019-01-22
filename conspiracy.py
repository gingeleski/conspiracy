"""
conspiracy.py

Demo
python conspiracy.py www.google.com
python conspiracy.py --hitlist ./test/hitlist1.txt play.google.com

"""

from sslyze.plugins.certificate_info_plugin import CertificateInfoScanCommand
from sslyze.plugins.compression_plugin import CompressionScanCommand
from sslyze.plugins.session_renegotiation_plugin import SessionRenegotiationScanCommand
from sslyze.server_connectivity_tester import ServerConnectivityTester
from sslyze.server_connectivity_tester import ServerConnectivityError
from sslyze.synchronous_scanner import SynchronousScanner

import argparse
import asyncio
import logging
import nmap
import os
import pyppeteer
import socket
import time
import urllib.error
import urllib.parse
import urllib.request

#######################################################################################################################

DESCRIPTION_STR  = 'Conspiracy v0.1 - Automated web app hacking'

BURP_SUITE_PROXY = '127.0.0.1:8080'
NMAP_SCAN_TYPE   = 'PING'

inscope_urls = {}    # (sub)domains in scope
hitlist = []         # optional individual urls to specially hit
requested_items = {} # keeps track of every unique request
output = ''          # what we print out to the user at the end

logging.basicConfig(level=logging.INFO, filename='conspiracy_' + str(int(time.time())) + '.log', \
                    filemode='w', format='%(asctime)s [%(levelname)s] %(message)s')

#######################################################################################################################

def derive_root_url(text_line):
    o = urllib.parse.urlparse(text_line)
    return o.netloc

def add_to_inscope_urls(target):
    inscope_urls[target] = True

def get_validated_hitlist_line(line):
    # Weed out blank/extra lines
    if len(line.strip()) == 0:
        return None
    # Allow lines prepended with # as comments
    elif line.startswith('#'):
        return None
    validated_line = ''
    if False == line.startswith('http://') or False == line.startswith('https://'):
        validated_line += 'http://'
    validated_line += line.replace('\n','') # Strip any line breaks remaining...
    return validated_line

def get_ip_addresses_cmd(domain):
    # TODO
    return None

def get_aliases_cmd(domain):
    # TODO
    return None

def get_ip_addresses_native(domain):
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

def get_aliases_native(domain):
    """
    Returns one or more aliases for the provided domain
    """
    try:
        data = socket.gethostbyname_ex(domain)
        aliases = repr(data[1])
        return aliases
    except Exception:
        return None

def check_if_proxy_up(proxy_addr):
    try:
        proxy_handler = urllib.request.ProxyHandler({ 'http' : proxy_addr })
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        req = urllib.request.Request('https://github.com')
        sock = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        if e.getcode() >= 400 and e.getcode() <= 500:
            return True
        return False
    except Exception as e:
        print(str(e))
        return False
    return True

def console_print(message, level='INFO', line_end='\n'):
    print('[Conspiracy] ' + message, end=line_end)

async def get_browser():
    return await pyppeteer.launch(headless=True,args=['--proxy-server=' + BURP_SUITE_PROXY])

async def run_processing_on_hitlist():
    # We're going to request stuff with headless Chrome, proxied through Burp Suite
    browser = await get_browser()
    # Then for each item (URL) ...
    for item in hitlist:
        logging.info(f'Now requesting {item.strip()}')
        # Request the page
        page = await browser.newPage()
        # TODO somehow record traffic into `requested_items` around here
        try:
            await page.goto(item)
        except pyppeteer.errors.TimeoutError as e:
            logging.warning('Timed out on request to ' + item)
            logging.warning('\t' + str(e))
        # ** Here, in the future, could add some hooks + handles for other functionality **
        # Close the page now
        await page.close()
    await browser.close()

#######################################################################################################################

def main():
    # Instantiate the argument parser
    parser = argparse.ArgumentParser(description=DESCRIPTION_STR)
    # Declaring all our acceptable arguments below...
    parser.add_argument('target', type=str, help='Overall target URL')
    parser.add_argument('--hitlist', type=str, help='Optional path to text file of URLs to analyze')
    # Then grab them from the command line input
    args = parser.parse_args()
    logging.info(DESCRIPTION_STR)
    logging.info('Starting to parse given targets...')
    # Add the overall target to in-scope URLs
    add_to_inscope_urls(args.target)
    # Was hitlist flag specified?
    if args.hitlist != None:
        logging.info('Hitlist was specified @ ' + args.hitlist)
        # Is the given path valid for a file?
        hitlist_exists = False
        try:
            hitlist_exists = os.path.isfile(args.hitlist)
        except:
            pass
        if hitlist_exists:
            logging.info('Validated hitlist path, now starting to read contents...')
            hitlist_lines = []
            # Read it in as a text file
            try:
                f = open(args.hitlist, 'r')
                # Break down by lines
                hitlist_lines = f.readlines()
                f.close()
            except:
                logging.error('something went wrong while opening hitlist file: ' + args.hitlist)
            # Validate then add each item to the hitlist
            for line in hitlist_lines:
                validated_line = get_validated_hitlist_line(line)
                if validated_line == None:
                    continue
                hitlist.append(line)
                # Also add root url to in-scope URLs if not already in there
                this_root_url = derive_root_url(line)
                add_to_inscope_urls(this_root_url)
        else:
            logging.error('hitlist path was specified but appears invalid: ' + args.hitlist)
    # If we have a hitlist then...
    if len(hitlist) > 0:
        if True == check_if_proxy_up(BURP_SUITE_PROXY):
            logging.info('Starting asynchronous processing of hitlist now...')
            console_print('Starting asynchronous processing of hitlist')
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(run_processing_on_hitlist())
            logging.info('Done processing hitlist')
            console_print('Done processing hitlist')
        else: # Burp Suite proxy is down
            logging.warning('Found Burp Suite proxy @ ' + BURP_SUITE_PROXY + ' to be down')
            logging.warning('Skipping processing of hitlist (requests with headless Chrome via Burp Suite)')
    logging.info('Starting broader processing of in-scope URLs...')
    # For each of our in-scope URLs ...
    for inscope_url, _ in inscope_urls.items():
        logging.info('Processing <' + inscope_url + '>')
        console_print('Processing <' + inscope_url + '>')
        # START MODULE: nslookup
        logging.info('Begin module: nslookup <' + inscope_url + '>')
        console_print('Begin module: nslookup <' + inscope_url + '>')
        ip_addresses = get_ip_addresses_cmd(inscope_url)
        if ip_addresses == None: # Python-native backup
            ip_addresses = get_ip_addresses_native(inscope_url)
        if len(ip_addresses) > 0:
            logging.info('\t' + 'IP addresses:')
            logging.info('\t\t' + str(ip_addresses))
        aliases = get_aliases_cmd(inscope_url)
        if aliases == None: # Python-native backup
            aliases = get_aliases_native(inscope_url)
        if len(aliases) > 0:
            logging.info('\t' + 'Aliases:')
            logging.info('\t\t' + str(aliases))
        logging.info('End module: nslookup <' + inscope_url + '>')
        console_print('End module: nslookup <' + inscope_url + '>')
        # END MODULE: nslookup
        # START MODULE: sslyze
        logging.info('Begin module: sslyze certificate information <' + inscope_url + '>')
        console_print('Begin module: sslyze certificate information <' + inscope_url + '>')
        try:
            sslyze_conn_test = ServerConnectivityTester(hostname=inscope_url)
            sslyze_server_info = sslyze_conn_test.perform()
            sslyze_scanner = SynchronousScanner()
            sslyze_results = sslyze_scanner.run_scan_command(sslyze_server_info, CertificateInfoScanCommand())
            sslyze_result_lines = sslyze_results.as_text()
            for line in sslyze_result_lines:
                logging.info(line)
            sslyze_results = sslyze_scanner.run_scan_command(sslyze_server_info, SessionRenegotiationScanCommand())
            sslyze_result_lines = sslyze_results.as_text()
            for line in sslyze_result_lines:
                logging.info(line)
            sslyze_results = sslyze_scanner.run_scan_command(sslyze_server_info, CompressionScanCommand())
            sslyze_result_lines = sslyze_results.as_text()
            for line in sslyze_result_lines:
                logging.info(line)
        except ServerConnectivityError as e:
            # Could not establish a TLS/SSL connection to the server
            logging.error(f'sslyze ended early, could not connect to {e.server_info.hostname}: {e.error_message}')
        logging.info('End module: sslyze certificate information <' + inscope_url + '>')
        console_print('End module: sslyze certificate information <' + inscope_url + '>')
        # END MODULE: sslyze
        # START MODULE: nmap
        logging.info('Start module: nmap port scan <' + inscope_url + '>')
        console_print('Start module: nmap port scan <' + inscope_url + '>')
        skip_nmap = False
        try:
            nm = nmap.PortScanner()
        except nmap.nmap.PortScannerError as e:
            # Most likely, nmap is not on the path
            logging.error(f'Error launching nmap module - is it on the path? : {e.error_message}')
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
                nmap_scan_result = nm.scan(hosts=inscope_url, arguments='-sS -sU -T4 -A -v')
            else:
                nmap_scan_result = nm.scan(hosts=inscope_url)
            logging.info(nmap_scan_result)
        logging.info('End module: nmap port scan <' + inscope_url + '>')
        console_print('End module: nmap port scan <' + inscope_url + '>')
        # END MODULE: nmap
    logging.info('End of execution, shutting down...')
    console_print('End of execution, shutting down...')

#######################################################################################################################

if __name__ == '__main__':
    main()
