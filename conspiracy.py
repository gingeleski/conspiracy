"""
conspiracy.py

Automated web app hacking

python conspiracy.py www.google.com
python conspiracy.py --hitlist ./test/assets/hitlist1.txt play.google.com

"""

import argparse
import asyncio
import importlib
import logging
import os
import pkgutil
import pyppeteer
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

#######################################################################################################################

# These snippets of code facilitate dynamic loading of all Conspiracy plugins that are present

from plugins import *

BROWSER_PAGE_PLUGINS = [cls() for cls in IBrowserPagePlugin.__subclasses__()]
DOMAIN_PLUGINS = [cls() for cls in IDomainPlugin.__subclasses__()]

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
    o = urllib.parse.urlparse(text_line)
    return o.netloc

def add_to_inscope_urls(target):
    global inscope_urls
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
        # FIXME under Github issue #47
        return False
    return True

def console_progress_bar(count, total):
    bar_length = 60
    filled_length = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write('[%s] %s%s\r' % (bar, percents, '%'))
    sys.stdout.flush()

def multi_line_info_log(message):
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
    parser.add_argument('--hitlist', type=str, help='Optional path to text file of URLs to analyze')
    # Then grab them from the command line input
    args = parser.parse_args()
    # Note the extra line breaks in the next two lines of code are for purely visual appearances in the log...
    for ascii_art_line in CONSPIRACY_ASCII_ART:
        logger.info(ascii_art_line)
    logger.info(DESCRIPTION_STR)
    logger.info('')
    logger.info('Starting to parse given targets...')
    # Add the overall target to in-scope URLs
    add_to_inscope_urls(args.target)
    # Was hitlist flag specified?
    if args.hitlist != None:
        logger.info('Hitlist was specified @ ' + args.hitlist)
        # Is the given path valid for a file?
        hitlist_exists = False
        try:
            hitlist_exists = os.path.isfile(args.hitlist)
        except:
            pass
        if hitlist_exists:
            logger.info('Validated hitlist path, now starting to read contents...')
            hitlist_lines = []
            # Read it in as a text file
            try:
                f = open(args.hitlist, 'r')
                # Break down by lines
                hitlist_lines = f.readlines()
                f.close()
            except:
                logger.error('Something went wrong while opening hitlist file: ' + args.hitlist)
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
            logger.error('Hitlist path was specified but appears invalid: ' + args.hitlist)
    # If we have a hitlist then...
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
