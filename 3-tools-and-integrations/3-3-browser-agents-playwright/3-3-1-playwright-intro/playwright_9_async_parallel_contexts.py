import asyncio
from dataclasses import dataclass

from playwright.async_api import async_playwright


@dataclass(frozen=True)
class TaskResult:
    """Represents a single navigation result."""
    name: str
    url: str
    final_url: str
    title: str


async def fetch_title_in_new_context(
    browser,
    name: str,
    url: str,
) -> TaskResult:
    """Open a URL in an isolated context and return basic page info."""
    context = await browser.new_context()
    page = await context.new_page()

    try:
        await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=20_000,
        )
        title = await page.title()
        return TaskResult(
            name=name,
            url=url,
            final_url=page.url,
            title=title,
        )
    finally:
        await context.close()


async def main() -> None:
    """Run multiple isolated browser contexts in parallel."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        tasks = [
            fetch_title_in_new_context(
                browser=browser,
                name="example",
                url="https://example.com",
            ),
            fetch_title_in_new_context(
                browser=browser,
                name="hn",
                url="https://news.ycombinator.com/",
            ),
        ]

        results = await asyncio.gather(*tasks)

        for r in results:
            print(
                f"[{r.name}] url={r.url} "
                f"final_url={r.final_url} title={r.title!r}"
            )

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
