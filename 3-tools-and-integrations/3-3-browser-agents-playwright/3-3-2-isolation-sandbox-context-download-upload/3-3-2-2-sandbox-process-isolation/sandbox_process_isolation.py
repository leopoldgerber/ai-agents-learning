from playwright.sync_api import Browser, Page, sync_playwright


def open_browser(headless: bool) -> Browser:
    """Launch a new browser process.
    Args:
        headless (bool): Whether to run the browser in headless mode."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        return browser


def run_flow(page: Page, label: str) -> str:
    """Open a page in the given browser and return its title.
    Args:
        page (Page): Playwright page.
        label (str): Flow label to log in the console."""
    page.goto('https://example.com', wait_until='domcontentloaded')
    title = page.title()
    print(f'{label}: {title}')
    return title


def run_two_sandboxes(headless: bool) -> list[str]:
    """Run two independent flows in two separate browser processes.
    Args:
        headless (bool): Whether to run the browsers in headless mode."""
    titles: list[str] = []

    with sync_playwright() as p:
        browser_one = p.chromium.launch(headless=headless)
        page_one = browser_one.new_page()
        titles.append(run_flow(page=page_one, label='Sandbox #1'))
        browser_one.close()

        browser_two = p.chromium.launch(headless=headless)
        page_two = browser_two.new_page()
        titles.append(run_flow(page=page_two, label='Sandbox #2'))
        browser_two.close()

    return titles


if __name__ == '__main__':
    sandbox_titles = run_two_sandboxes(headless=False)
    print(sandbox_titles)
