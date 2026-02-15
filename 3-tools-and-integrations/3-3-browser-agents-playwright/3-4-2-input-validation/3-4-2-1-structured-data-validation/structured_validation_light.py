from bs4 import BeautifulSoup


def clean_html(html: str, max_length: int = 10000) -> str:
    """Safely extracts text from HTML, removing scripts and styles."""
    # Limit the size of the input data
    html = html[:max_length]

    soup = BeautifulSoup(html, "lxml")

    # Remove all scripts, styles, and other potentially dangerous elements
    for tag in soup(["script", "style", "iframe", "object", "embed"]):
        tag.decompose()

    # Extract clean text
    text = soup.get_text(separator=" ", strip=True)

    return text


if __name__ == '__main__':
    # Example usage
    html_response = """
    <html>
    <head><script>alert('XSS')</script></head>
    <body>
        <h1>Article Title</h1>
        <p>Useful content here</p>
    </body>
    </html>
    """
    clean_text = clean_html(html_response)
    print(f'Result: {clean_text}')
