import asyncio
from playwright.async_api import async_playwright


async def worker(name, queue, context):
    while True:
        try:
            url = queue.get_nowait()
        except asyncio.QueueEmpty:
            return

        print(f"[{name}] START {url}")
        page = await context.new_page()
        await page.goto(url)
        title = await page.title()
        print(f"[{name}] END   {url} → {title}")
        await page.close()

        queue.task_done()


async def main(urls):
    queue = asyncio.Queue()

    for url in urls:
        await queue.put(url)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()

        workers = [
            asyncio.create_task(worker(f"W{i}", queue, context))
            for i in range(1, 4)
        ]

        await queue.join()
        for w in workers:
            w.cancel()

        await context.close()
        await browser.close()


if __name__ == '__main__':
    urls = [
        "https://example.com", "https://example.org", "https://example.net"]
    asyncio.run(main(urls))
