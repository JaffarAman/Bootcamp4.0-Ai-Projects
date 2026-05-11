from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def clean_html(html):
    soup = BeautifulSoup(html, "lxml")

    # remove unwanted tags
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    return soup.get_text(separator=" ", strip=True)


def scrape_vercel_playwright(url: str) -> str:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, timeout=60000)

            # wait for rendering
            page.wait_for_timeout(3000)

            html = page.content()

            browser.close()

            # 🔥 CLEAN HERE
            clean_text = clean_html(html)

            return clean_text

    except Exception as e:
        print("Playwright Error:", e)
        return ""