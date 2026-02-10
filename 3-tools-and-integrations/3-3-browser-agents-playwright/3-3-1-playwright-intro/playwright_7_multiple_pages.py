from playwright.sync_api import sync_playwright


def main() -> None:
    """Demonstrate navigation caused by clicking a link."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        context = browser.new_context()
        page = context.new_page()

        page.goto(
            "https://example.com",
            wait_until="domcontentloaded",
        )

        with page.expect_navigation():
            page.get_by_role(
                "link",
                name="Learn more",
            ).click()

        page.wait_for_load_state("domcontentloaded")

        print("Current page URL:", page.url)
        print("Current page title:", page.title())

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
