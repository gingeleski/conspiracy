"""
conspiracy.py

Demo
python conspiracy.py www.google.com
python conspiracy.py --hitlist ./test/hitlist1.txt play.google.com

"""

import argparse
import asyncio
import importlib
import logging
import os
import pkgutil
import pyppeteer
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

#######################################################################################################################

# These snippets of code facilitate dynamic loading of all Conspiracy plugins that are present

from Plugins import *

BROWSER_PAGE_PLUGINS = [cls() for cls in IBrowserPagePlugin.__subclasses__()]
DOMAIN_PLUGINS = [cls() for cls in IDomainPlugin.__subclasses__()]

#######################################################################################################################

# Global constants

DESCRIPTION_STR  = 'Conspiracy v0.1 - Automated web app hacking'

BURP_SUITE_PROXY = '127.0.0.1:8080'

#######################################################################################################################

# Global variables

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
        # Looping through plugins of this type
        for plugin in BROWSER_PAGE_PLUGINS:
            logging.info('Begin plugin: ' + plugin.get_name() + ' <' + item.strip() + '>')
            console_print('Begin plugin: ' + plugin.get_name() + ' <' + item.strip() + '>')
            plugin.executePerDomainAction(inscope_url)
            logging.info('End plugin: ' + plugin.get_name() + ' <' + item.strip() + '>')
            console_print('End plugin: ' + plugin.get_name() + ' <' + item.strip() + '>')
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
        # Looping through plugins of this type
        for plugin in DOMAIN_PLUGINS:
            logging.info('Begin plugin: ' + plugin.get_name() + ' <' + inscope_url + '>')
            console_print('Begin plugin: ' + plugin.get_name() + ' <' + inscope_url + '>')
            plugin.executePerDomainAction(inscope_url)
            logging.info('End plugin: ' + plugin.get_name() + ' <' + inscope_url + '>')
            console_print('End plugin: ' + plugin.get_name() + ' <' + inscope_url + '>')
    logging.info('End of execution, shutting down...')
    console_print('End of execution, shutting down...')

#######################################################################################################################

if __name__ == '__main__':
    main()
