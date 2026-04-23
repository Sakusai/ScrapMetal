from datetime import datetime
from scrapper import scrape_boursorama_stock
import db.dbactions as dba

db = dba.Database()
db.connect()

def init():
    print("DB > Création des tables...")
    db.recreate_tables()
    print("DB > Tables créées avec succès !")
    print("DB > Initialisation des données de base...")
    db.insert_currency("EUR")
    print("DB > Données de base initialisées avec succès !\n")

def scrape_live_quote(url="https://www.boursorama.com/cours/1rPORA/"):
    stock = scrape_boursorama_stock(url)
    print(stock)
    db.cursor.execute("SELECT id_stock FROM stock WHERE isin = ?", (stock.get("isin"),))
    result = db.cursor.fetchone()
    if result:
        id_stock = result[0]
    else:
        id_currency = db.cursor.execute("SELECT id_currency FROM currency WHERE code = 'EUR'").fetchone()[0]
        id_stock = db.insert_stock(
            isin=stock["isin"], 
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

if __name__ == "__main__":
    # init()
    db.purge_data()
    db.insert_currency("EUR")

    print("Scraping live quote...")
    scrape_live_quote()

    print(db.execute("SELECT * FROM stock;").fetchall())
    print(db.execute("SELECT * FROM quote_live;").fetchall())

    db.close()
