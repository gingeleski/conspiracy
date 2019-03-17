import asyncio
from pyppeteer import launch

hitlist = ['http://example.com', 'https://play.google.com/store', 'https://play.google.com/store/apps']

async def browser_stuff():
    global hitlist
    browser = await launch()
    for url in hitlist:
        page = await browser.newPage()
        await page.goto(url)
        await page.screenshot({'path': 'example_' + url.replace('/', '').replace(':', '') + '.png'})
    await browser.close()

def main():
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(browser_stuff())

if __name__ == '__main__':
    main()
