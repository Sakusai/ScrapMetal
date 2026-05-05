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
            print("Ticker and symbol not found.")

        # 2. Stock label
        try:
            title_block = faceplate.locator("h1.c-faceplate__company-title").first
            data["stock_label"] = title_block.locator("a.c-faceplate__company-link").inner_text().strip()
        except Exception:
            print("Stock label not found.")

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
            print("Market price, currency or variation not found.")

        # 4. Open & High & Low & Volume
        try:
            data_block = faceplate.locator("div.c-faceplate__data").first

            data["open"] = parse_float_fr(data_block.locator("span.c-instrument.c-instrument--open").first.inner_text().strip())
            data["high"] = parse_float_fr(data_block.locator("span.c-instrument.c-instrument--high").first.inner_text().strip())
            data["low"] = parse_float_fr(data_block.locator("span.c-instrument.c-instrument--low").first.inner_text().strip())
            data["volume"] = parse_float_fr(data_block.locator("span.c-instrument.c-instrument--totalvolume").first.inner_text().strip())
        except Exception:
            print("Open, High, Low or Volume not found.")

        browser.close()
        return data
def scrape_boursorama_stock_forum(url: str) -> list[dict]:
    """
    Scrape a Boursorama stock's forum data.
    Compatible with such URLs : https://www.boursorama.com/bourse/forum/1rPABCA/

    Returns a list of dicts : [
        {
            "title": str,
            "date_create": str,      
            "author": str,
            "url": str,
            "comments": [
                {
                    "content": str,
                    "date_comment": str, 
                    "author": str,
                }
            ]
        },
        ...
    ]
    """

    def parse_boursorama_date(raw: str) -> str:
        raw   = raw.strip()
        today = datetime.now()  
        MOIS = {
            "janv": 1, "févr": 2, "mars": 3, "avr": 4, "mai": 5, "juin": 6,
            "juil": 7, "août": 8, "sept": 9, "oct": 10, "nov": 11, "déc": 12
        }
        if raw.lower().startswith("aujourd"):
            m = re.search(r"(\d{1,2})[h:](\d{2})", raw)
            if m:
                return today.replace(
                    hour=int(m.group(1)), minute=int(m.group(2)), second=0, microsecond=0
                ).strftime("%Y-%m-%d %H:%M:%S")

        if raw.lower().startswith("hier"):
            m = re.search(r"(\d{1,2})[h:](\d{2})", raw)
            if m:
                return (today - timedelta(days=1)).replace(
                    hour=int(m.group(1)), minute=int(m.group(2)), second=0, microsecond=0
                ).strftime("%Y-%m-%d %H:%M:%S")

        m = re.search(r"(\d{1,2})\s+(\w+\.?)\s+(\d{4})\s+[•·]\s+(\d{2}):(\d{2})", raw)
        if m:
            d, mo_str, y, h, mn = m.groups()
            mo = MOIS.get(mo_str.rstrip("."), 1)
            return f"{y}-{mo:02d}-{int(d):02d} {h}:{mn}:00"

        return raw

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

        topics_data      = []
        current_list_url = url
        page_num = 0
        while current_list_url:
            if page_num >= 1:    
                break
            page_num += 1
            load_page(page, current_list_url)
            print(current_list_url)
            topic_rows = page.locator("tr.c-table__row:has(a.c-link--bold[href*='/forum/'])").all()            
            if not topic_rows:
                print("Aucun topic trouvé sur cette page.")
                break
            print(f"{len(topic_rows)} topic(s) trouvés sur la page.")
            for topic_row in topic_rows:
                try:
                    link      = topic_row.locator("a.c-link--bold[href*='/forum/']").first
                    title     = link.inner_text().strip()
                    href      = link.get_attribute("href")
                    topic_url = href if href.startswith("http") else f"https://www.boursorama.com{href}"

                    author    = topic_row.locator("div.c-source button.c-source__username").first.inner_text().strip()

                    raw_date  = topic_row.locator("span.c-source__time").first.inner_text().strip()

                    topics_data.append({
                        "title":       title,
                        "date_create": parse_boursorama_date(raw_date),
                        "author":      author,
                        "url":         topic_url,
                        "comments":    [],
                    })
                except Exception as e:
                        print(f"Erreur lecture topic : {e}")
                        continue

            next_btn = page.locator("a.c-pagination__link--mobile[aria-label='Page suivante']").first
            if next_btn.count() and next_btn.get_attribute("href"):
                href = next_btn.get_attribute("href")
                current_list_url = href if href.startswith("http") else f"https://www.boursorama.com{href}"
            else:
                current_list_url = None

        for i, topic in enumerate(topics_data):
            print(f"Topic {i+1}/{len(topics_data)} : {topic['title']}")
            current_topic_url = topic["url"]
          

            while current_topic_url:
                load_page(page, current_topic_url)


                for block in page.locator("ul[data-load-more-content] > li > div.c-message").all():
                    try:
                        content = block.locator("> p.c-message__text").first.inner_text().strip()
                        author  = block.locator("div.c-profile-card__name button").first.inner_text().strip()

                        time_spans = block.locator("div.c-source span.c-source__time").all()
                        raw_date   = " • ".join([s.inner_text().strip() for s in time_spans])

                        topic["comments"].append({
                            "content":      content,
                            "date_comment": parse_boursorama_date(raw_date),
                            "author":       author,
                        })

                    except Exception as e:
                        print(f"  Erreur lecture message : {e}")
                        continue

                current_topic_url = None  # Pas de pagination dans les topics

            print(f"  → {len(topic['comments'])} message(s)")

        browser.close()
        return topics_data
def has_download_form(page) -> bool:
    return page.locator('form[name="quote_search"]').count() == 1

def fill_download_form(form, tickers: list[str], dateStart: str = None, dateEnd: str = None):
    # Select quote search type "Custom indexes list"
    form.locator('label[for="quote_search_type_1"]').dispatch_event("click")

    ticker_input_string = ",".join(tickers)
    tickers_input = form.locator('input[name="quote_search[customIndexesList]"]')
    tickers_input.fill(ticker_input_string)

    # Deselect currency data
    # form.locator('input[name="quote_search[currency]"]').dispatch_event("click")
    
    # Select period
    if dateStart:
        form.locator('input[name="quote_search[startDate]"]').fill(dateStart)
    if dateEnd:
        form.locator('input[name="quote_search[endDate]"]').fill(dateEnd)

    # Select decimal separator -> POINT
    decimal_format_select = form.locator('select[name="quote_search[decimalFormat]"]')
    decimal_format_select.select_option(value="POINT", force=True)

def scrape_boursorama_stock_daily(tickers: list[str], dateStart: str = None, dateEnd: str = None) -> str:
    """
    Scrape a Boursorama stock's daily data.
    Compatible with such Tickers : FR0000133308

    Returns a path to the file downloaded from Boursorama, containing the historical data for the given tickers and period.
    The dates given refer to the period of data to download. The default period will be from yesterday to yesterday at the time of execution.

    Note: session persistence for the authenticated Boursorama download flow has been identified as partially unreliable.

    In practice, the saved Playwright storage state may remain valid enough to access the download page and display the form, 
    while still being too old to authorize the actual file download request. 
    -> Not a priority to fix... For now, deleting the stored session state and re-authenticating resolves the issue when it occurs.
    """

    storage_path = "playwright/.auth/state.json"

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)

        context_args = {
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "accept_downloads": True
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
        else:
            print("Using cached session...")

        # Suppose the form exists
        form = page.locator('form[name="quote_search"]').first
        print("Form OK:", form.count())

        # Form filling
        fill_download_form(form, tickers, dateStart, dateEnd)

        # Download
        with page.expect_download() as download_info:
            form.evaluate("(f) => f.submit()")

        download = download_info.value
        download.save_as("downloads/boursorama_daily_export.txt")

        browser.close()
        return path.abspath("downloads/boursorama_daily_export.txt")