from datetime import datetime, timedelta
from scrapper import scrape_boursorama_stock_daily, scrape_boursorama_stock_live

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

def scrape_live_quote(url="https://www.boursorama.com/cours/1rPORA/"):
    stock = scrape_boursorama_stock_live(url)
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
            boursorama_url=url, 
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
        
    file_path = scrape_boursorama_stock_daily(tickers, dateStart, dateEnd)
    print(f"Daily quote data downloaded to : {file_path}")

    #TODO : parse file and insert data into DB

if __name__ == "__main__":
    # init(purgeOnly=False)

    # print("Scraping live quote...")
    # scrape_live_quote()

    print("Scraping daily quote...")
    scrape_daily_quote(["FR0000133308"], "01/01/2026", "01/03/2026")

    db.close()
