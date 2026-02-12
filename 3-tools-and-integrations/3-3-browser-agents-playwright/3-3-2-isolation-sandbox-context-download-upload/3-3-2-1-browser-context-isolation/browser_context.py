

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright


def open_isolated_context(browser: Browser) -> BrowserContext:
    """Create a new isolated browser context.
    Args:
        browser (Browser): Launched Playwright browser instance."""
    context = browser.new_context()
    return context


def run_search_flow(page: Page, query: str) -> str:
    """Run a simple search flow and return the page title.
    Args:
        page (Page): Playwright page within a browser context.
        query (str): Search query to type and submit."""
    page.goto('https://www.google.com', wait_until='domcontentloaded')

    if page.locator("button:has-text('Не интересует')").count() > 0:
        page.locator("button:has-text('Не интересует')").click()

    page.fill("textarea[name='q']", query)
    page.press("textarea[name='q']", 'Enter')
    page.wait_for_load_state('domcontentloaded')

    title = page.title()
    return title


def run_two_isolated_users(headless: bool) -> list[str]:
    """Run two independent user flows using separate browser contexts.
    Args:
        headless (bool): Whether to run the browser in headless mode."""
    results: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)

        context_one = open_isolated_context(browser=browser)
        page_one = context_one.new_page()
        results.append(run_search_flow(page=page_one, query='Python'))
        context_one.close()

        context_two = open_isolated_context(browser=browser)
        page_two = context_two.new_page()
        results.append(run_search_flow(page=page_two, query='Playwright'))
        context_two.close()

        browser.close()

    return results


if __name__ == '__main__':
    titles = run_two_isolated_users(headless=False)
    print(titles)
