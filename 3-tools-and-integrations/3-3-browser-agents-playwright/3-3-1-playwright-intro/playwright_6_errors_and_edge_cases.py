from playwright.sync_api import (
    TimeoutError,
    sync_playwright,
)


def main() -> None:
    """Demonstrate error handling and edge cases in Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto(
                "https://example.com",
                wait_until="domcontentloaded",
                timeout=5_000,
            )

            page.locator("button.submit").click(timeout=3_000)

        except TimeoutError as exc:
            print("Timeout occurred:", exc)
            page.screenshot(path="timeout_error.png")

        except Exception as exc:
            print("Unexpected error:", exc)
            page.screenshot(path="unexpected_error.png")

        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
