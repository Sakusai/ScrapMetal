from datetime import datetime, timedelta
from scrapper import scrape_boursorama_stock_daily, scrape_boursorama_stock_forum, scrape_boursorama_stock_live
from playwright.sync_api import sync_playwright

import re
import db.dbactions as dba

db = dba.Database()
db.connect()

def init(purgeOnly: bool = False):
    print("DB > Création des tables...")
    db.purge_tables() if purgeOnly else db.recreate_tables()
    print("DB > Tables créées avec succès !")
    print("DB > Initialisation des données de base...")
    db.insert_currency("EUR")
    print("DB > Données de base initialisées avec succès !\n")

def scrape_live_quote(ticker: str, url: str = None) -> int:
    finalurl = f"https://www.boursorama.com/cours/{ticker}/" if url is None else url
    stock = scrape_boursorama_stock_live(finalurl)
    print(stock)

    db.cursor.execute("SELECT id_stock FROM stock WHERE ticker = ?", (stock.get("ticker"),))
    result = db.cursor.fetchone()

    if result:
        id_stock = result[0]
    else:
        id_currency = db.cursor.execute("SELECT id_currency FROM currency WHERE code = 'EUR'").fetchone()[0]
        id_stock = db.insert_stock(
            ticker=stock["ticker"], 
            symbol=stock["symbol"], 
            label=stock["stock_label"], 
            boursorama_url=finalurl, 
            id_currency=id_currency #Currency EUR by default, but could be automated
        )

    db.insert_quote_live(
        id_stock,
        stock.get("collected_at", datetime.now().isoformat()),
        stock.get("market_price"),
        stock.get("open"),
        stock.get("high"),
        stock.get("low"),
        stock.get("volume")
    )

    return id_stock

def scrape_daily_quote(tickers: list[str], dateStart: str, dateEnd: str) -> None:
    # Arguments validation
    if not tickers:
        raise ValueError("At least one ticker must be provided.")
    if dateStart and not re.match(r"\d{2}/\d{2}/\d{4}", dateStart):
        raise ValueError("dateStart must be in DD/MM/YYYY format.")
    if dateEnd and not re.match(r"\d{2}/\d{2}/\d{4}", dateEnd):
        raise ValueError("dateEnd must be in DD/MM/YYYY format.")
    start_date = datetime.strptime(dateStart, "%d/%m/%Y").date() if dateStart else None
    end_date = datetime.strptime(dateEnd, "%d/%m/%Y").date() if dateEnd else None
    if start_date and end_date and start_date > end_date:
        raise ValueError("dateStart cannot be after dateEnd.")
    
    # Because we scrape daily data, quotes have to be closed, so dateStart and dateEnd cannot be later than yesterday
    yesterday = datetime.now().date() - timedelta(days=1)
    if (start_date and start_date > yesterday) or (end_date and end_date > yesterday):
        raise ValueError("dateStart and dateEnd cannot be in the future.")
        
    # Scrape data
    file_path = scrape_boursorama_stock_daily(tickers, dateStart, dateEnd)
    print(f"Daily quote data downloaded to : {file_path}")

    # Parse file
    print("Parsing daily quote data...")
    with open(file_path, "r") as f:
        stocks = []
        for line in f:
            stocks.append(line.strip().split("\t"))
        stocks.pop(0) # Remove header line
    f.close()

    # Scraping live quote inserts stock into DB, so if stock from tickers is not already present, we insert
    ticker_to_id_stock = {}
    for ticker in tickers:
        db.cursor.execute("SELECT id_stock FROM stock WHERE ticker = ?", (ticker,))
        result = db.cursor.fetchone()
        if not result:
            ticker_to_id_stock[ticker] = scrape_live_quote(ticker)
        else:
            ticker_to_id_stock[ticker] = result[0]

    # Insert data into DB
    print("Inserting daily quote data into DB...")
    for stock in stocks:
        ticker = stock[0]
        id_stock = ticker_to_id_stock[ticker]

        db.upsert_quote_daily(
            id_stock,
            stock[2], # date
            stock[3], # open
            stock[4], # high
            stock[5], # low
            stock[6], # close
            stock[7]  # volume
        )

def resolve_boursorama_quote_url(url: str) -> str:
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
        page.goto(url, wait_until="networkidle")
        final_url = page.url
        browser.close()
        return final_url

def scrape_forum(ticker: str) -> None:
    stock_row = db.cursor.execute(
        "SELECT id_stock, boursorama_url FROM stock WHERE ticker = ?", (ticker,)
    ).fetchone()

    if not stock_row:
        id_stock = scrape_live_quote(ticker)
        print(f"Ticker {ticker} inséré en base avec id {id_stock}.")
        if id_stock is None:
            raise ValueError(f"Impossible d'insérer le stock pour le ticker {ticker}.")
        boursorama_url = db.cursor.execute(
            "SELECT boursorama_url FROM stock WHERE id_stock = ?", (id_stock,)
        ).fetchone()[0]
    else:
        id_stock = stock_row[0]
        boursorama_url = stock_row[1]

    resolved_url = resolve_boursorama_quote_url(boursorama_url)

    print(f"Scraping forum for {ticker} with URL {resolved_url}...")
    m = re.search(r"/cours/([^/]+)/", resolved_url)
    if not m:
        raise ValueError(f"Impossible d'extraire le symbol depuis l'URL : {resolved_url}")
    
    symbol = m.group(1)           
    url    = f"https://www.boursorama.com/bourse/forum/{symbol}/"

    topics = scrape_boursorama_stock_forum(url)

    for topic in topics:
        id_topic = db.insert_topic(
            title=topic["title"],
            date_create=topic["date_create"],
            author=topic["author"],
            id_stock=id_stock,
        )
        for comment in topic["comments"]:
            db.insert_comment(
                content=comment["content"],
                date_comment=comment["date_comment"],
                author=comment["author"],
                id_topic=id_topic,
            )

    print(f" {len(topics)} topics insérés en base pour {ticker}.")

if __name__ == "__main__":
    init(purgeOnly=False)

    print("Scraping live quote...")
    scrape_live_quote("1rPMC") 

    print("Scraping forum...")
    scrape_forum("FR0000121014") # LVMH

    print("Scraping daily quote...")
    scrape_daily_quote(["FR0000133308", "NL0000235190"], "01/01/2026", "01/03/2026") # ORANGE & AIRBUS

    print("Done !")

    db.close()
