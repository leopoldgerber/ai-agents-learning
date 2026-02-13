import asyncio
from typing import List

from playwright.async_api import async_playwright


MAX_CONCURRENT_TASKS = 2


async def fetch_title(browser, url: str, semaphore: asyncio.Semaphore) -> str:
    """Fetch page title with concurrency control."""
    async with semaphore:
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url, wait_until="domcontentloaded")
        title = await page.title()

        await context.close()
        return f"{url} -> {title}"


async def run_with_throttling(headless: bool) -> List[str]:
    """Run tasks with limited concurrency."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)

        semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

        tasks = [
            fetch_title(browser, url, semaphore)
            for url in URLS
        ]

        results = await asyncio.gather(*tasks)

        await browser.close()
        return results


async def main() -> None:
    results = await run_with_throttling(headless=True)
    for r in results:
        print(r)


if __name__ == "__main__":
    URLS = [
        "https://example.com", "https://httpbin.org/get",
        "https://www.python.org", "https://example.org",
        "https://httpbin.org/ip",]
    asyncio.run(main())
