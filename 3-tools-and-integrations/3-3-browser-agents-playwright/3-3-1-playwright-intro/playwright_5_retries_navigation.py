import time
from typing import Optional

from playwright.sync_api import (
    TimeoutError,
    sync_playwright,
)


def goto_with_retries(
    page,
    url: str,
    attempts: int,
) -> Optional[int]:
    """Navigate to a page with retry logic."""
    last_status: Optional[int] = None

    for attempt in range(attempts):
        try:
            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=10_000,
            )
            if response is not None:
                last_status = response.status
            return last_status
        except TimeoutError:
            time.sleep(1 + attempt)

    return last_status


def main() -> None:
    """Demonstrate retry logic for page navigation."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context()
        page = context.new_page()

        status_code = goto_with_retries(
            page=page,
            url="https://news.ycombinator.com/",
            attempts=3,
        )

        print("Final status code:", status_code)

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
