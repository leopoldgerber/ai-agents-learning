from playwright.sync_api import sync_playwright


def main() -> None:
    """Record a browser session video and save it to the videos directory."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            record_video_dir="videos",
        )
        page = context.new_page()

        try:
            page.goto(
                "https://demo.playwright.dev/todomvc/",
                wait_until="domcontentloaded",
                timeout=20_000,
            )

            new_todo = page.locator("input.new-todo")
            new_todo.fill("record video")
            new_todo.press("Enter")

            page.wait_for_timeout(1_000)
            print("Video will be saved after context.close()")
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
