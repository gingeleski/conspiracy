import asyncio
from pyppeteer import launch

async def browser_stuff():
    browser = await launch()
    page = await browser.newPage()
    await page.goto('http://example.com')
    await page.screenshot({'path': 'example.png'})
    await browser.close()

def main():
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(browser_stuff())

if __name__ == '__main__':
    main()
