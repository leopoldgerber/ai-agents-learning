import asyncio
import random
from typing import List

from playwright.async_api import async_playwright, TimeoutError


URLS = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/429",
    "https://httpbin.org/status/200",
]


MAX_CONCURRENT_TASKS = 2
MAX_RETRIES = 3


async def fetch_with_retry(browser, url: str) -> str:
    """Fetch URL with retry and exponential backoff."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            context = await browser.new_context()
            page = await context.new_page()

            response = await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=5000,
            )

            status = response.status if response else None

            await context.close()

            if status == 429:
                raise Exception("Rate limited")

            return f"{url} -> {status}"

        except (TimeoutError, Exception):
            wait_time = 2 ** attempt + random.uniform(0, 1)
            await asyncio.sleep(wait_time)

    return f"{url} -> failed after retries"


async def run_with_limits(headless: bool) -> List[str]:
    """Run tasks with concurrency limits and retry protection."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)

        semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

        async def guarded_fetch(url: str) -> str:
            async with semaphore:
                return await fetch_with_retry(browser, url)

        tasks = [guarded_fetch(url) for url in URLS]
        results = await asyncio.gather(*tasks)

        await browser.close()
        return results


async def main() -> None:
    results = await run_with_limits(headless=True)
    for r in results:
        print(r)


if __name__ == "__main__":
    asyncio.run(main())
