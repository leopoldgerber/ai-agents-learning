from playwright.sync_api import sync_playwright

URL = "https://example.com"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # Контекст 1
    ctx1 = browser.new_context()
    page1 = ctx1.new_page()
    page1.goto(URL)
    print("ctx1 title:", page1.title())

    # Контекст 2 (полностью изолирован)
    ctx2 = browser.new_context()
    page2 = ctx2.new_page()
    page2.goto(URL)
    print("ctx2 title:", page2.title())

    ctx1.close()
    ctx2.close()
    browser.close()
