from playwright.sync_api import sync_playwright


def main() -> None:
    """Launch Chromium, open a page, and print its title."""
    with sync_playwright() as p:
        # Launch Chromium browser
        browser = p.chromium.launch(headless=True)

        # Create an isolated browser context (profile/session)
        context = browser.new_context()
        # Create a new page (tab) inside the context
        page = context.new_page()

        page.goto("https://example.com")  # Navigate to the website
        print(page.title())               # Print the page title

        context.close()                   # Close the context
        browser.close()                   # Close the browser


if __name__ == "__main__":
    main()
