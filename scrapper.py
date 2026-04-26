from os import path
from playwright.sync_api import sync_playwright
from datetime import datetime
from auth import authenticate

import re

def load_page(page, url: str):
    page.goto(url, wait_until="domcontentloaded", timeout=30_000)
    page.wait_for_load_state("networkidle")

def parse_float_fr(text: str) -> float | None:
    if not text:
        return None
    try:
        cleaned = text.strip().replace("\xa0", " ")
        cleaned = re.sub(r"[^\d,.\- ]", "", cleaned)
        cleaned = cleaned.replace(" ", "").replace(",", ".")
        parts = cleaned.split(".")
        if len(parts) > 2:
            cleaned = "".join(parts[:-1]) + "." + parts[-1]
        return float(cleaned) if cleaned else None
    except Exception:
        return None

def scrape_boursorama_stock_live(url: str) -> dict:
    """
    Scrape a Boursorama stock's live data.
    Compatible with such URLs : https://www.boursorama.com/cours/1rP74SW/

    Returns a Dict : {collected_at, stock_label, ticker, market_price, variation, open, high, low, volume}
    """
    
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        collected_at = datetime.now()
        load_page(page, url)

        data = {
            "collected_at": collected_at.strftime("%Y-%m-%d %H:%M:%S"),
            "url": url,
            "symbol": None,
            "stock_label": None,
            "ticker": None,
            "market_price": None,
            "currency": None,
            "variation": None,
            "open": None,
            "high": None,
            "low": None,
            "volume": None,
        }

        faceplate = page.locator("div.c-faceplate").first

        # 1. Ticker & Symbol
        try:
            fullTicker = faceplate.locator("h2.c-faceplate__isin").inner_text().strip().split(" ")
            data["ticker"] = fullTicker[0]
            data["symbol"] = fullTicker[1]
        except Exception:
            pass

        # 2. Stock label
        try:
            title_block = faceplate.locator("h1.c-faceplate__company-title").first
            data["stock_label"] = title_block.locator("a.c-faceplate__company-link").inner_text().strip()
        except Exception:
            pass

        # 3. Market price & currency & variation
        try:
            values_block = faceplate.locator("div.c-faceplate__values").first

            price_block = values_block.locator("div.c-faceplate__price").first
            price_text = price_block.locator("span.c-instrument.c-instrument--last").inner_text().strip()
            data["market_price"] = parse_float_fr(price_text)
            data["currency"] = price_block.locator("span.c-faceplate__price-currency").inner_text().strip()

            variation_block = values_block.locator("div.c-faceplate__fluctuation").first
            variation_text = variation_block.locator("span.c-instrument.c-instrument--variation").inner_text().strip()
            data["variation"] = parse_float_fr(variation_text)
        except Exception:
            pass

        # 4. Open & High & Low & Volume
        try:
            data_block = faceplate.locator("div.c-faceplate__data").first

            data["open"] = parse_float_fr(data_block.locator("span.c-instrument.c-instrument--open").first.inner_text().strip())
            data["high"] = parse_float_fr(data_block.locator("span.c-instrument.c-instrument--high").first.inner_text().strip())
            data["low"] = parse_float_fr(data_block.locator("span.c-instrument.c-instrument--low").first.inner_text().strip())
            data["volume"] = parse_float_fr(data_block.locator("span.c-instrument.c-instrument--totalvolume").first.inner_text().strip())
        except Exception:
            pass

        browser.close()
        return data
    
def has_download_form(page) -> bool:
    return page.locator('form[name="quote_search"]').count() == 1

def scrape_boursorama_stock_daily(ticker: str) -> dict:
    storage_path = "playwright/.auth/state.json"

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)

        context_args = {
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        if path.exists(storage_path):
            context_args["storage_state"] = storage_path

        context = browser.new_context(**context_args)
        page = context.new_page()

        # Try direct access
        url = "https://www.boursorama.com/espace-membres/telecharger-cours/paris"
        load_page(page, url)

        # If no form found, re-authenticate in the same page/session
        if not has_download_form(page):
            print("Session invalid or expired, re-authentification...")

            ok = authenticate(page, context)
            if not ok:
                browser.close()
                raise RuntimeError("Authentication failed.")

            # Retry accessing the member page
            load_page(page, url)

            if not has_download_form(page):
                browser.close()
                raise RuntimeError("Authenticated, but download form still not found.")

        # Suppose the form exists
        form = page.locator('form[name="quote_search"]').first
        print("Form OK:", form.count())

        data = {
            "ticker": None,
            "stock_label": None,
            "date": None,
            "open": None,
            "high": None,
            "low": None,
            "close": None,
            "volume": None,
        }

        #TODO: fill the form with the ticker, submit it, wait for results, parse results

        browser.close()
        return data