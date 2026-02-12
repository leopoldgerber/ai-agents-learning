from playwright.sync_api import Browser, BrowserContext, sync_playwright


def grant_example_perms(context: BrowserContext) -> BrowserContext:
    """Grant example permissions inside the context.
    Args:
        context (BrowserContext): Playwright browser context."""
    context.grant_permissions(['geolocation'], origin='https://example.com')
    return context


def add_example_cookie(context: BrowserContext) -> BrowserContext:
    """Add a demo cookie to the context for example.com.
    Args:
        context (BrowserContext): Playwright browser context."""
    context.add_cookies(
        [
            {
                'name': 'session_id',
                'value': '123456',
                'url': 'https://example.com',
            }
        ]
    )
    return context


def read_state(context: BrowserContext) -> dict[str, int]:
    """Read basic state counters from the context.
    Args:
        context (BrowserContext): Playwright browser context."""
    cookies_count = len(context.cookies())
    return {'cookies_count': cookies_count}


def clear_partial_state(context: BrowserContext) -> BrowserContext:
    """Clear cookies and permissions without closing the context.
    Args:
        context (BrowserContext): Playwright browser context."""
    context.clear_cookies()
    context.clear_permissions()
    return context


def run_demo(headless: bool) -> list[dict[str, int]]:
    """Demonstrate full cleanup via close and partial cleanup via clear_*.
    Args:
        headless (bool): Whether to run the browser in headless mode."""
    snapshots: list[dict[str, int]] = []

    with sync_playwright() as p:
        browser: Browser = p.chromium.launch(headless=headless)

        context = browser.new_context()
        grant_example_perms(context=context)
        add_example_cookie(context=context)
        snapshots.append(read_state(context=context))

        clear_partial_state(context=context)
        snapshots.append(read_state(context=context))

        context.close()

        fresh_context = browser.new_context()
        snapshots.append(read_state(context=fresh_context))
        fresh_context.close()

        browser.close()

    return snapshots


if __name__ == '__main__':
    demo_snapshots = run_demo(headless=False)
    print(demo_snapshots)
