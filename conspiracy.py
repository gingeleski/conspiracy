"""
conspiracy.py

Automated web app hacking

python conspiracy.py www.google.com
python conspiracy.py --hitlist ./test/assets/hitlist1.txt play.google.com

"""

import asyncio
import pyppeteer
import time

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
#hitlist = []         # optional individual urls to specially hit
hitlist = ['http://example.com', 'https://play.google.com/store', 'https://play.google.com/store/apps']
requested_items = {} # keeps track of every unique request

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', \
                    handlers=[ logging.FileHandler('conspiracy_' + str(int(time.time())) + '.log'),\
                               logging.StreamHandler() ])
logger = logging.getLogger('conspiracy')

#######################################################################################################################

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
    global BROWSER_PAGE_PLUGINS
    global hitlist #, logger
    # We're going to request stuff with headless Chrome, proxied through Burp Suite
    browser = await get_browser(use_burp_suite_proxy)
    # Then for each item (URL) ...
    for item in hitlist:
        #logger.info(f'Now requesting {item.strip()}')
        # Request the page
        page = await browser.newPage()
        try:
            await page.goto(item)
            await page.screenshot({'path': 'example_' + item.replace('/', '').replace(':', '') + '.png'})
        except pyppeteer.errors.TimeoutError as e:
            print(e)
        #    logger.warning('Timed out on request to ' + item)
        #    logger.warning('\t' + str(e))
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
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(run_processing_on_hitlist(False))

#######################################################################################################################

if __name__ == '__main__':
    main()
