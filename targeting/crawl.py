"""crawl.py"""

from ._interfaces import ITargetingMode

import logging


class CrawlTargeting(ITargetingMode):
    """Conspiracy targeting mode that crawls from existing target(s)

    Params:
        name (str)
        logger (Logger)
    """

    def __init__(self):
        self.name = 'Crawl'
        self.logger = logging.getLogger('conspiracy')

    def check_arg_match(self, arg_string):
        """Returns whether the given argument value matches this mode.

        Params:
            arg_string (str)

        Returns:
            (bool)
        """
        if arg_string.lower() == 'crawl':
            return True
        # Default to false
        return False

    def acquire_targets(self, inscope_urls={}):
        """Run execution logic for this targeting mode, returns new targets' URLs
        
        Params:
            inscope_urls (dict)

        Returns:
            (list)
        """
        targets = []
        for key, value in inscope_urls.items():
            # TODO actually implement this all here
            print(key)
            """
            browser = await pyppeteer.launch(headless=True)
            page = await browser.newPage()
            try:
                await page.goto(key)
            except pyppeteer.errors.TimeoutError as e:
                # Currently doing nothing on timeout
                pass
            await page.close()
            await browser.close()
            """
        return targets
