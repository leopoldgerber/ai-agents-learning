from playwright.sync_api import sync_playwright


def main() -> None:
    """Demonstrate explicit and implicit waits in Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context()
        page = context.new_page()

        page.goto(
            "https://demo.playwright.dev/todomvc/",
            wait_until="domcontentloaded",
        )

        new_todo = page.locator("input.new-todo")
        new_todo.fill("learn waiting")
        new_todo.press("Enter")

        todo_item = page.locator(
            "label",
            has_text="learn waiting",
        )

        todo_item.wait_for(state="visible")
        print("Todo item is visible")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
