from playwright.sync_api import sync_playwright


STATE_FILE = "state.json"


def save_session(headless: bool) -> None:
    """Login simulation and save storage state."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()

        page = context.new_page()
        page.goto("https://example.com")

        # Here could be your business-logic

        context.storage_state(path=STATE_FILE)

        context.close()
        browser.close()


def restore_session(headless: bool) -> str:
    """Restore session from saved storage state."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)

        context = browser.new_context(storage_state=STATE_FILE)
        page = context.new_page()
        page.goto("https://example.com")

        title = page.title()

        context.close()
        browser.close()

        return title


if __name__ == "__main__":
    save_session(headless=True)
    restored_title = restore_session(headless=True)
    print(restored_title)
