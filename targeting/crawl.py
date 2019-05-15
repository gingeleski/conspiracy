"""crawl.py"""

from ._interfaces import ITargetingMode

from browser import BrowserRender, Response
from bs4 import BeautifulSoup
from typing import List, Union
from urllib.parse import urljoin, urlparse

import asyncio
import logging
import pyppeteer


class PageQueue(object):
    """Page queue, crawler helper class

    Params:
        page_queue (asyncio.Queue)
        seen_urls (set)
        active_jobs (int)
    """

    def __init__(self, seed_urls: Union[List[str], str]):
        self.page_queue = asyncio.Queue()
        self.seen_urls = set()
        self.seed_queue(seed_urls)
        self.active_jobs = 0

    def seed_queue(self, seed_urls: Union[List[str], str]):
        if isinstance(seed_urls, str):
            self.page_queue.put_nowait(seed_urls)
        elif isinstance(seed_urls, (set, list)):
            for item in seed_urls:
                self.page_queue.put_nowait(item)

    async def put_unique_url(self, url):
        if url not in self.seen_urls:
            await self.page_queue.put(url)
            self.seen_urls.add(url)

    async def get_next_url(self):
        while True:
            try:
                next_page = self.page_queue.get_nowait()
                self.active_jobs += 1
            except asyncio.QueueEmpty:
                if self.active_jobs > 0:
                    await asyncio.sleep(0.01)
                elif self.active_jobs <= 0:
                    raise asyncio.QueueEmpty('Queue empty with no pending jobs')
                else:
                    await asyncio.sleep(0.01)
            else:
                return next_page


class Crawler(object):
    """Main crawler class, call it to crawl

    Params:
        start_url (str)
        visited_urls (dict)
        base_host (str)
        url_queue (PageQueue)
        loop (asyncio.EventLoop)
        browser (obj)
    """

    def __init__(self, start_url: str):
        self.start_url = start_url
        self.base_host = '{parsed.scheme}://{parsed.netloc}'.format(parsed=urlparse(start_url))
        self.url_queue = PageQueue(self.start_url)
        self.loop = asyncio.get_event_loop()
        self.browser = BrowserRender(loop=self.loop, headless=True, tabs=5)

    async def urls_from_response(self, resp: Response):
        soup = BeautifulSoup(resp.html, 'lxml')
        links = soup.find_all('a', href=True)
        for l in links:
            tmp_link = l['href']
            joined = urljoin(self.start_url, tmp_link)
            if joined.startswith(self.base_host):
                await self.url_queue.put_unique_url(joined)
        return

    async def consume_queue(self, consume: int):
        while True:
            try:
                target = await self.url_queue.get_next_url()
                resp = await self.browser.get_request(target, timeout=30, post_load_wait=0)
                await self.urls_from_response(resp)
            except asyncio.QueueEmpty:
                return
            except Exception as e:
                print('Consumer {}'.format(consume), e)

    def run_scraper(self, workers: int) -> None:
        groups = [self.consume_queue(i) for i in range(workers)]
        work_group = asyncio.gather(*groups)

        loop = self.loop
        try:
            loop.run_until_complete(work_group)
        finally:
            loop.close()

    def get_seen_urls(self):
        """
        Get seen URLs from this crawler's URL queue

        Returns:
            (set)
        """
        return self.url_queue.seen_urls


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
        targets = set()
        for key, value in inscope_urls.items():
            # key of inscope_urls is URL
            start_url = key
            if False == start_url.startswith('http'):
                start_url = 'http://' + start_url
            cr = Crawler(start_url)
            cr.run_scraper(2)
            # We are considering every unique URL seen as a target
            just_acquired_targets = cr.get_seen_urls()
            targets = targets.union(just_acquired_targets)
        return targets
