import asyncio
import time
from playwright.async_api import async_playwright


async def open_page(context, url, idx):
    start = time.perf_counter()
    print(f"[{idx}] START {start:.2f}")

    page = await context.new_page()
    await page.goto(url)

    title = await page.title()
    end = time.perf_counter()

    print(f"[{idx}] END {end:.2f} | duration: {end - start:.2f}s | {title}")
    await page.close()


async def main():
    url = "https://example.com"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()

        tasks = [open_page(context, url, idx) for idx in range(1, 6)]

        await asyncio.gather(*tasks)
        await context.close()
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
