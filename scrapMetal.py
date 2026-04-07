from playwright.sync_api import sync_playwright
import re
import pandas as pd
from pathlib import Path

with sync_playwright() as pw:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("http://boursorama.com/bourse/actions/cotations/")
