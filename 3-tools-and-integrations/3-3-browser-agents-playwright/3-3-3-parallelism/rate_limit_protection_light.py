import random
import asyncio
from playwright.async_api import async_playwright


async def fetch_page(url, context, semaphore):
    async with semaphore:
        page = await context.new_page()
        await page.goto(url)
        title = await page.title()
        print(title)
        await page.close()

    await asyncio.sleep(random.uniform(0.8, 1.5))


async def main(urls):
    semaphore = asyncio.Semaphore()

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()

        tasks = [fetch_page(url, context, semaphore) for url in urls]

        await asyncio.gather(*tasks)

        await context.close()
        await browser.close()


if __name__ == '__main__':
    urls = [
        "https://example.com", "https://example.org",
        "https://example.net"]

    asyncio.run(main(urls))
