"""
conspiracy.py

Automated web app hacking

python conspiracy.py www.google.com
python conspiracy.py --targeting-mode hitlist@/test/assets/hitlist1.txt play.google.com

"""

import argparse
import asyncio
import importlib
import logging
import os
import pkgutil
import pyppeteer
import re
import requests
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

#######################################################################################################################

# These snippets of code facilitate dynamic loading of all Conspiracy modes and plugins that are present

from plugins import *
from targeting import *

BROWSER_PAGE_PLUGINS = [cls() for cls in IBrowserPagePlugin.__subclasses__()]
DOMAIN_PLUGINS = [cls() for cls in IDomainPlugin.__subclasses__()]
TARGETING_MODES = [cls() for cls in ITargetingMode.__subclasses__()]

#######################################################################################################################

# Global constants

DESCRIPTION_STR  = 'Conspiracy v0.1 - Automated web app hacking'

BURP_SUITE_PROXY = '127.0.0.1:8080'

CONSPIRACY_ASCII_ART = ['',
                        ' ######   #######  ##    ##  ######  ########  #### ########     ###     ######  ##    ##',
                        '##    ## ##     ## ###   ## ##    ## ##     ##  ##  ##     ##   ## ##   ##    ##  ##  ##',
                        '##       ##     ## ####  ## ##       ##     ##  ##  ##     ##  ##   ##  ##         ####',
                        '##       ##     ## ## ## ##  ######  ########   ##  ########  ##     ## ##          ##',
                        '##       ##     ## ##  ####       ## ##         ##  ##   ##   ######### ##          ##',
                        '##    ## ##     ## ##   ### ##    ## ##         ##  ##    ##  ##     ## ##    ##    ##',
                        ' ######   #######  ##    ##  ######  ##        #### ##     ## ##     ##  ######     ##',
                        '']

PROXY_TEST_TIMEOUT = 5 # seconds
PROXY_TEST_URL = 'https://www.google.com/'

PUT_OVERALL_DOMAIN_TARGETS_IN_HITLIST = False

#######################################################################################################################

# Global variables

inscope_urls = {}    # (sub)domains in scope
hitlist = []         # optional individual urls to specially hit
requested_items = {} # keeps track of every unique request

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', \
                    handlers=[ logging.FileHandler('conspiracy_' + str(int(time.time())) + '.log'),\
                               logging.StreamHandler() ])
logger = logging.getLogger('conspiracy')

#######################################################################################################################

def derive_root_url(text_line):
    """
    Derives root URL given string with one in it

    Params:
        text_line (str)
    """
    o = urllib.parse.urlparse(text_line)
    return o.netloc

def add_to_inscope_urls(target):
    """
    Add a new key to the global in-scope URL dict with value True

    Params:
        target (str)
    """
    global inscope_urls
    inscope_urls[target] = True

def check_if_proxy_up(proxy_addr):
    """
    Check if proxy address provided seems possible to send traffic through

    Params:
        proxy_addr (str)

    Returns:
        (bool)
    """
    global logger
    if '127.0.0.1' in proxy_addr or 'localhost:' in proxy_addr:
        cleaned_proxy_addr = proxy_addr.replace('https://', 'http://').replace('http://', '')
        # Assuming there's now just one : and it's before the port number, split the string
        localhost_port = cleaned_proxy_addr.split(':')[-1]
        try:
            # Remove any characters which are not digits then parse that to int
            localhost_port = int(re.sub('[^0-9]', '', localhost_port))
        # If this went sideways then the proxy address is probably bust
        except Exception as e:
            return False
        # Now let's see if we can bind to this port the proxy is on
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('127.0.0.1', localhost_port))
            s.close()
            return False
        # When we *can't* that means port is in use and let's assume proxy is up
        except Exception as e:
            return True
    else:
        try:
            test_proxies = { 'http' : proxy_addr, 'https' : proxy_addr }
            r = requests.get(PROXY_TEST_URL, timeout=PROXY_TEST_TIMEOUT, proxies=test_proxies)
            if r.status_code == requests.codes.ok:
                return True
            else:
                return False
        except Exception as e:
            return False
    return True

def console_progress_bar(count, total):
    """
    Prints a 'progress bar' to console then flushes stdout

    Params:
        count (int)
        total (int)
    """
    bar_length = 60
    filled_length = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write('[%s] %s%s\r' % (bar, percents, '%'))
    sys.stdout.flush()

def multi_line_info_log(message):
    """
    Prints a multi-line log message with a single call for each line

    Params:
        message (str)
    """
    global logger
    split_lines = message.split('\n')
    for line in split_lines:
        logger.info(line)

async def get_browser(use_burp_suite_proxy):
    """
    Get browser

    Params:
        use_burp_suite_proxy (bool)
    """
    if use_burp_suite_proxy:
        return await pyppeteer.launch(headless=True,args=['--proxy-server=' + BURP_SUITE_PROXY])
    # else, don't proxy
    return await pyppeteer.launch(headless=True)

async def run_processing_on_hitlist(use_burp_suite_proxy):
    """
    Run processing on hitlist

    Params:
        use_burp_suite_proxy (bool)
    """
    global hitlist, logger
    # We're going to request stuff with headless Chrome, proxied through Burp Suite
    browser = await get_browser(use_burp_suite_proxy)
    # Then for each item (URL) ...
    for item in hitlist:
        logger.info(f'Now requesting {item.strip()}')
        # Request the page
        page = await browser.newPage()
        try:
            await page.goto(item)
        except pyppeteer.errors.TimeoutError as e:
            logger.warning('Timed out on request to ' + item)
            logger.warning('\t' + str(e))
        # Looping through plugins of this type
        for plugin in BROWSER_PAGE_PLUGINS:
            logger.info('Begin plugin: ' + plugin.get_name() + ' <' + item.strip() + '>')
            plugin.executePerDomainAction(inscope_url)
            logger.info('End plugin: ' + plugin.get_name() + ' <' + item.strip() + '>')
        # Close the page now
        await page.close()
    await browser.close()

#######################################################################################################################

def main():
    global hitlist, inscope_urls, logger, requested_items
    # Instantiate the argument parser
    parser = argparse.ArgumentParser(description=DESCRIPTION_STR)
    # Declaring all our acceptable arguments below...
    parser.add_argument('target', type=str, help='Overall target URL')
    parser.add_argument('--targeting-mode', type=str, help='Optional mode for acquiring target surface')
    # Then grab them from the command line input
    args = parser.parse_args()
    # Note the extra line breaks in the next two lines of code are for purely visual appearances in the log...
    for ascii_art_line in CONSPIRACY_ASCII_ART:
        logger.info(ascii_art_line)
    logger.info(DESCRIPTION_STR)
    logger.info('')
    logger.info('Starting to parse given targets...')
    if PUT_OVERALL_DOMAIN_TARGETS_IN_HITLIST:
        overall_target_as_url = 'https://' + args.target
        logger.info('Adding overall target <' + overall_target_as_url + '> to hitlist')
        # Add overall target to hitlist in URL form with a probably-unneeded check for duplicates along the way
        hitlist = hitlist + (list(set(overall_target_as_url) - set(hitlist)))
    # Add the overall target to in-scope URLs
    add_to_inscope_urls(args.target)
    # Was targeting mode specified?
    if args.targeting_mode != None:
        logger.info('Looking for match to given targeting mode string "' + args.targeting_mode + '"')
        has_run_one_targeting_mode = False
        for targeting_mode in TARGETING_MODES:
            if True == targeting_mode.check_arg_match(args.targeting_mode):
                has_run_one_targeting_mode = True
                logger.info('Matched targeting mode "' + targeting_mode.get_name() + '"')
                logger.info('Conducting ' + targeting_mode.get_name() + ' targeting now...')
                # Run whatever the mode's logic is to get target URLs from initial scope
                targets_output = targeting_mode.acquire_targets(inscope_urls)
                previous_targets_number = len(hitlist)
                # Add any new target URLs to the master list - we avoid duplicate entries
                hitlist = hitlist + list(set(targets_output) - set(hitlist))
                new_targets_number = len(hitlist) - previous_targets_number
                logger.info('Added ' + str(new_targets_number) + ' targets after ' + targeting_mode.get_name())
        if False == has_run_one_targeting_mode:
            logger.warning('Did not run any targeting modes - none available matched "' + args.targeting_mode + '"')
        else:
            # Let's now make align in-scope URLs with the hitlist... *THIS IS OPINIONATED*
            for entry in hitlist:
                this_root_url = derive_root_url(entry)
                add_to_inscope_urls(this_root_url)
    # If we have any targets then...
    if len(hitlist) > 0:
        logger.info('Checking if Burp Suite proxy ' + BURP_SUITE_PROXY + ' is running...')
        burp_proxy_is_up = check_if_proxy_up(BURP_SUITE_PROXY)
        if burp_proxy_is_up:
            logger.info('Burp Suite proxy appears to be running, will use this for headless Chrome')
        else: # Burp Suite proxy is down
            logger.warning('Found Burp Suite proxy @ ' + BURP_SUITE_PROXY + ' to be down')
            logger.warning('Will not use proxy for headless Chrome')
        logger.info('Starting asynchronous processing of hitlist now...')
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(run_processing_on_hitlist(burp_proxy_is_up))
        logger.info('Done processing hitlist')
    else:
        logger.warning('No targets in hitlist, not requesting anything via headless Chrome')
    logger.info('Starting broader processing of in-scope URLs...')
    # For each of our in-scope URLs ...
    for inscope_url, _ in inscope_urls.items():
        logger.info('Processing <' + inscope_url + '>')
        # Looping through plugins of this type
        for plugin in DOMAIN_PLUGINS:
            logger.info('Begin plugin: ' + plugin.get_name() + ' <' + inscope_url + '>')
            plugin.executePerDomainAction(inscope_url)
            logger.info('End plugin: ' + plugin.get_name() + ' <' + inscope_url + '>')
    logger.info('End of execution, shutting down...')

#######################################################################################################################

if __name__ == '__main__':
    main()
