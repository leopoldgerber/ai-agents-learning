import asyncio

from playwright.async_api import async_playwright


async def main() -> None:
    """Open a page using the async Playwright API and print its title."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(
            "https://example.com",
            wait_until="domcontentloaded",
        )

        print("Title:", await page.title())

        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
