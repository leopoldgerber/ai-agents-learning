from playwright.sync_api import sync_playwright


STATE_FILE = "state.json"


def save_session(headless: bool) -> None:
    """Generate real browser state and save it."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()

        page = context.new_page()
        page.goto("https://example.com")

        # Generate real localStorage value dynamically
        page.evaluate(
            """
            () => {
                localStorage.setItem(
                    "dynamic_key",
                    Date.now().toString()
                );
                sessionStorage.setItem(
                    "session_key",
                    Math.random().toString()
                );
            }
            """
        )

        # Generate real cookie via browser API
        context.add_cookies(
            [
                {
                    "name": "generated_cookie",
                    "value": page.evaluate("() => Math.random().toString()"),
                    "url": "https://example.com",
                }
            ]
        )

        context.storage_state(path=STATE_FILE)

        context.close()
        browser.close()


def restore_session(headless: bool) -> dict:
    """Restore session and verify state exists."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(storage_state=STATE_FILE)

        page = context.new_page()
        page.goto("https://example.com")

        state_check = page.evaluate(
            """
            () => {
                return {
                    local: localStorage.length,
                    session: sessionStorage.length
                }
            }
            """
        )

        context.close()
        browser.close()

        return state_check


if __name__ == "__main__":
    save_session(headless=True)
    restored_state = restore_session(headless=True)
    print(restored_state)
