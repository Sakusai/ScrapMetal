from playwright.sync_api import StorageState, sync_playwright
from dotenv import load_dotenv

import os

load_dotenv(".env")

def authenticate() -> StorageState:
    print("Authenticating...")

    username = os.getenv("BOURSO_USERNAME")
    password = os.getenv("BOURSO_PASSWORD")

    if not username or not password:
        raise ValueError("BOURSO_USERNAME and BOURSO_PASSWORD environment variables are required.")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=200)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page =  context.new_page()
        
        page.goto('https://www.boursorama.com/', wait_until="domcontentloaded", timeout=30_000)

        page.locator("span.didomi-continue-without-agreeing").click()

        page.locator("#login-member").click()

        page.locator("#login_member_login").fill(username)
        page.locator("#login_member_password").fill(password)

        page.locator("body").click()
        page.wait_for_timeout(500)

        page.locator("#login_member_connect").click(force=True)

        page.wait_for_load_state("networkidle")

        context.storage_state(path="playwright/.auth/state.json")
        browser.close()

    print("Authenticated successfully !")