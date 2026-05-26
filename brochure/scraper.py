from typing import Final
from bs4 import BeautifulSoup
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

headers: Final[dict[str, str]] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


def _clean_soup(soup: BeautifulSoup) -> tuple[str, str]:
    title = soup.title.string.strip() if soup.title and soup.title.string else "No title found"
    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""
    return title, text


def _fetch_with_requests(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")


def _fetch_with_playwright(url: str) -> BeautifulSoup:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=headers["User-Agent"])
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            try:
                page.wait_for_load_state("networkidle", timeout=5_000)
            except PlaywrightTimeoutError:
                pass
            html = page.content()
        finally:
            browser.close()
    return BeautifulSoup(html, "html.parser")


def _fetch_soup(url: str) -> BeautifulSoup:
    try:
        soup = _fetch_with_requests(url)
        _, text = _clean_soup(soup)
        if len(text) < 500:
            # Sparse content likely means JS-rendered page — retry with Playwright
            return _fetch_with_playwright(url)
        return soup
    except Exception:
        return _fetch_with_playwright(url)


def fetch_website_content(url: str) -> str:
    try:
        soup = _fetch_soup(url)
        title, text = _clean_soup(soup)
    except Exception:
        title, text = "Unable to fetch page", "Both requests and Playwright failed for this URL."
    return (title + "\n\n" + text)[:2_000]


def fetch_website_links(url: str) -> list[str]:
    try:
        soup = _fetch_soup(url)
    except Exception:
        return []
    return [
        href
        for tag in soup.find_all("a")
        if isinstance(href := tag.get("href"), str)
    ]
