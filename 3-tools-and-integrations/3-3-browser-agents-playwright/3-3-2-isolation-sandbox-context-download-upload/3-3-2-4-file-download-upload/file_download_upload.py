from pathlib import Path

from playwright.sync_api import Browser, Page, sync_playwright


def build_upload_file(work_dir: Path) -> Path:
    """Create a small local file for upload demo.
    Args:
        work_dir (Path): Directory to place the file in."""
    work_dir.mkdir(parents=True, exist_ok=True)
    file_path = work_dir / 'example_upload.txt'
    file_path.write_text('Hello from Playwright!\n', encoding='utf-8')
    return file_path


def run_download_demo(page: Page, downloads_dir: Path) -> Path:
    """Download a file using expect_download and save it locally.
    Args:
        page (Page): Playwright page.
        downloads_dir (Path): Directory to save downloaded files."""
    downloads_dir.mkdir(parents=True, exist_ok=True)

    page.goto(
        'https://the-internet.herokuapp.com/download',
        wait_until='domcontentloaded',
    )

    download_link = page.locator('#content a').first
    with page.expect_download() as download_info:
        download_link.click()

    download = download_info.value
    suggested_name = download.suggested_filename
    target_path = downloads_dir / suggested_name
    download.save_as(str(target_path))

    return target_path


def run_upload_demo(page: Page, file_path: Path) -> str:
    """Upload a file via input[type=file] using set_input_files.
    Args:
        page (Page): Playwright page.
        file_path (Path): Path to a local file for upload."""
    page.goto(
        'https://the-internet.herokuapp.com/upload',
        wait_until='domcontentloaded',
    )

    page.set_input_files('input[type="file"]', str(file_path))
    page.click('#file-submit')
    page.wait_for_load_state('domcontentloaded')

    uploaded_name = page.locator('#uploaded-files').inner_text().strip()
    return uploaded_name


def run_demo(headless: bool) -> dict[str, str]:
    """Run download and upload demos in one isolated context.
    Args:
        headless (bool): Whether to run the browser in headless mode."""
    result: dict[str, str] = {}

    with sync_playwright() as p:
        browser: Browser = p.chromium.launch(headless=headless)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        base_dir = Path(__file__).resolve().parent
        work_dir = base_dir / 'work'
        downloads_dir = base_dir / 'downloads'

        upload_file = build_upload_file(work_dir=work_dir)
        downloaded_path = run_download_demo(
            page=page,
            downloads_dir=downloads_dir,
        )
        uploaded_name = run_upload_demo(page=page, file_path=upload_file)

        result['downloaded_file'] = str(downloaded_path)
        result['uploaded_file'] = uploaded_name

        context.close()
        browser.close()

    return result


if __name__ == '__main__':
    demo_result = run_demo(headless=False)
    print(demo_result)
