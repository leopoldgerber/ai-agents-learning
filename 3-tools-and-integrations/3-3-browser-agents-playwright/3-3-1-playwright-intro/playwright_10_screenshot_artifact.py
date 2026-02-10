from playwright.sync_api import sync_playwright


def main() -> None:
    """Open a page and save a full-page screenshot."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto(
                "https://example.com",
                wait_until="domcontentloaded",
                timeout=20_000,
            )

            page.screenshot(
                path="screenshot.png",
                full_page=True,
            )

            print("Saved screenshot: screenshot.png")
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
