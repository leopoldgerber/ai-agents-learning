import asyncio
from typing import List

from playwright.async_api import async_playwright


URLS = [
    "https://example.com",
    "https://httpbin.org/get",
    "https://www.python.org",
]


async def fetch_title(browser, url: str) -> str:
    """Open URL in isolated context and return page title."""
    context = await browser.new_context()
    page = await context.new_page()

    await page.goto(url, wait_until="domcontentloaded")
    title = await page.title()

    await context.close()
    return f"{url} -> {title}"


async def run_parallel(headless: bool) -> List[str]:
    """Run multiple isolated tasks in parallel contexts."""
    results: List[str] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)

        tasks = [
            fetch_title(browser=browser, url=url)
            for url in URLS
        ]

        results = await asyncio.gather(*tasks)

        await browser.close()

    return results


async def main() -> None:
    results = await run_parallel(headless=True)
    for result in results:
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
