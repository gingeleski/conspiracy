"""
conspiracy.py

Conspiracy - automated web app hacking

Demo
python conspiracy.py www.google.com

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

BURP_SUITE_PROXY = '127.0.0.1:8080'

inscope_urls = {}    # (sub)domains in scope
hitlist = []         # optional individual urls to specially hit

requested_items = {} # keeps track of every unique request

output = ''

def derive_root_url(text_line):
    return text_line

def add_to_inscope_urls(target):
    inscope_urls[target] = True

# Instantiate the argument parser
parser = argparse.ArgumentParser(description='Conspiracy - automated web app hacking')

parser.add_argument('target', type=str, help='Overall target URL')
parser.add_argument('--hitlist', type=str, help='Optional path to text file of URLs to analyze')
args = parser.parse_args()

# add the overall target to inscope_urls
add_to_inscope_urls(args.target)

# was hitlist flag specified?
if args.hitlist != None:
    # is the given path valid for a file?
    hitlist_exists = False
    try:
        hitlist_exists = os.path.isfile(args.hitlist)
    except:
        pass
    if hitlist_exists:
        hitlist_lines = []
        # read it in as a text file
        try:
            f = open(args.hitlist, 'r')
            # break down by lines
            hitlist_lines = f.readlines()
            f.close()
        except:
            print('ERROR: something went wrong while opening hitlist file: ' + args.hitlist)
            output += 'ERROR: something went wrong while opening hitlist file: ' + args.hitlist + '\n'
        # validate then add each item to the hitlist
        for line in hitlist_lines:
            hitlist.append(line)
            # also add root url to `inscope_urls` if not already in there
            this_root_url = derive_root_url(line)
            add_to_inscope_urls(this_root_url)
    else:
        print('ERROR: hitlist path was specified but appears invalid: ' + args.hitlist)
        output += 'ERROR: hitlist path was specified but appears invalid: ' + args.hitlist + '\n'

# for each item in hitlist
if len(hitlist) > 0:
    # we'll request it in headless chrome, proxied through burp suite
    browser = launch(headless=True,args=['--proxy-server=' + BURP_SUITE_PROXY])
    for item in hitlist:
        page = browser.newPage()
        # get page + wait for it to load
        page.goto('https://www.google.com')
        page.waitForSelect('body')
        # (in the future could add some hooks + handles here for other stuff)
        # close the tab or whatever
        page.close()
    browser.close()

# for each item in `inscope_urls`
for inscope_url, _ in inscope_urls.items():
    # Module: sslyze
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
    # Module: Burp Suite scan
    # TODO

# print out all findings for user
print(output)
