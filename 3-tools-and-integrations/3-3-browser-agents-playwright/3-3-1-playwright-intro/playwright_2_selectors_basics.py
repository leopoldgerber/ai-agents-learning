from playwright.sync_api import sync_playwright


def main() -> None:
    """Demonstrate basic selector strategies in Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context()
        page = context.new_page()

        page.goto("https://example.com")

        heading = page.locator("h1")
        print("H1 text:", heading.inner_text())

        more_info = page.get_by_role(
            "link",
            name="More information..."
        )
        print("Link href:", more_info.get_attribute("href"))

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
