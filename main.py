# from playwright.sync_api import sync_playwright
# import re
# import pandas as pd
# from pathlib import Path

# with sync_playwright() as pw:
#     browser = p.chromium.launch(headless=False)
#     page = browser.new_page()

#     page.goto("http://boursorama.com/bourse/actions/cotations/")


from datetime import date, datetime
from decimal import Decimal

import models
from db.database import Base, SessionLocal, engine
from models import CurrencyEnum, DailyQuote, LiveQuote, Stock


def create_tables():
    print("Création des tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès !")


def drop_tables():
    print("Suppression des tables...")
    Base.metadata.drop_all(bind=engine)
    print("Tables supprimées avec succès !")


def recreate_tables():
    drop_tables()
    create_tables()


def purge_live_quotes():
    session = SessionLocal()
    try:
        deleted_count = session.query(LiveQuote).delete()
        session.commit()
        print(f"{deleted_count} live quotes supprimées.")
    finally:
        session.close()


def purge_daily_quotes():
    session = SessionLocal()
    try:
        deleted_count = session.query(DailyQuote).delete()
        session.commit()
        print(f"{deleted_count} daily quotes supprimées.")
    finally:
        session.close()


def purge_stocks():
    session = SessionLocal()
    try:
        deleted_count = session.query(Stock).delete()
        session.commit()
        print(f"{deleted_count} stocks supprimés.")
    finally:
        session.close()

def purge_all():
    purge_live_quotes()
    purge_daily_quotes()
    purge_stocks()


if __name__ == "__main__":
    pass
