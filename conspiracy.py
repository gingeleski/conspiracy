"""
conspiracy.py

Conspiracy - automated web app hacking

Demo
python conspiracy.py www.google.com
python conspiracy.py --hitlist ./test/hitlist1.txt play.google.com

"""

from pyppeteer import launch
from sslyze.plugins.certificate_info_plugin import CertificateInfoScanCommand
from sslyze.plugins.compression_plugin import CompressionScanCommand
from sslyze.plugins.session_renegotiation_plugin import SessionRenegotiationScanCommand
from sslyze.server_connectivity_tester import ServerConnectivityTester
from sslyze.server_connectivity_tester import ServerConnectivityError
from sslyze.synchronous_scanner import SynchronousScanner

import argparse
#import asyncio # we probably need some await's somewhere...
import os

#######################################################################################################################

BURP_SUITE_PROXY = '127.0.0.1:8080'

inscope_urls = {}    # (sub)domains in scope
hitlist = []         # optional individual urls to specially hit
requested_items = {} # keeps track of every unique request
output = ''          # what we print out to the user at the end

#######################################################################################################################

def derive_root_url(text_line):
    return text_line

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
    validated_line += line
    return validated_line

#######################################################################################################################

# Instantiate the argument parser
parser = argparse.ArgumentParser(description='Conspiracy - automated web app hacking')
# Declaring all our acceptable arguments below...
parser.add_argument('target', type=str, help='Overall target URL')
parser.add_argument('--hitlist', type=str, help='Optional path to text file of URLs to analyze')
# Then grab them from the command line input
args = parser.parse_args()
# Add the overall target to in-scope URLs
add_to_inscope_urls(args.target)
# Was hitlist flag specified?
if args.hitlist != None:
    # Is the given path valid for a file?
    hitlist_exists = False
    try:
        hitlist_exists = os.path.isfile(args.hitlist)
    except:
        pass
    if hitlist_exists:
        hitlist_lines = []
        # Read it in as a text file
        try:
            f = open(args.hitlist, 'r')
            # Break down by lines
            hitlist_lines = f.readlines()
            f.close()
        except:
            print('ERROR: something went wrong while opening hitlist file: ' + args.hitlist)
            output += 'ERROR: something went wrong while opening hitlist file: ' + args.hitlist + '\n'
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
        print('ERROR: hitlist path was specified but appears invalid: ' + args.hitlist)
        output += 'ERROR: hitlist path was specified but appears invalid: ' + args.hitlist + '\n'
# If we have a hitlist then...
if len(hitlist) > 0:
    # We're going to request stuff with headless Chrome, proxied through Burp Suite
    browser = launch(headless=True,args=['--proxy-server=' + BURP_SUITE_PROXY])
    # Then for each item (URL) ...
    for item in hitlist:
        # Request the page
        page = browser.newPage()
        page.goto(item)
        # Wait for it to load "fully"
        page.waitForSelect('body')
        # ** Here, in the future, could add some hooks + handles for other functionality **
        # Close the page now
        page.close()
    browser.close()
# For each of our in-scope URLs ...
for inscope_url, _ in inscope_urls.items():
    # START MODULE: sslyze
    output += 'START: SSLYZE CERTIFICATE INFORMATION' + '\n'
    try:
        sslyze_conn_test = ServerConnectivityTester(hostname=inscope_url)
        sslyze_server_info = sslyze_conn_test.perform()
        sslyze_scanner = SynchronousScanner()
        sslyze_results = sslyze_scanner.run_scan_command(sslyze_server_info, CertificateInfoScanCommand())
        sslyze_result_lines = sslyze_results.as_text()
        for line in sslyze_result_lines:
            output += line + '\n'
        sslyze_results = sslyze_scanner.run_scan_command(sslyze_server_info, SessionRenegotiationScanCommand())
        sslyze_result_lines = sslyze_results.as_text()
        for line in sslyze_result_lines:
            output += line + '\n'
        sslyze_results = sslyze_scanner.run_scan_command(sslyze_server_info, CompressionScanCommand())
        sslyze_result_lines = sslyze_results.as_text()
        for line in sslyze_result_lines:
            output += line + '\n'
    except ServerConnectivityError as e:
        # Could not establish a TLS/SSL connection to the server
        print(f'ERROR: sslyze ended early, could not connect to {e.server_info.hostname}: {e.error_message}')
        output += f'ERROR: sslyze ended early, could not connect to {e.server_info.hostname}: {e.error_message}' + '\n'
    output += 'END: SSLYZE CERTIFICATE INFORMATION' + '\n'
    # END MODULE: sslyze
    # START MODULE: Burp Suite
    # TODO
    # END MODULE: Burp Suite
# Print out all findings for user
print(output)
