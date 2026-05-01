from playwright.sync_api import StorageState, sync_playwright
from dotenv import load_dotenv

import os

load_dotenv(".env")

def authenticate(page, context) -> bool:
    print("Authenticating...")

    username = os.getenv("BOURSO_USERNAME")
    password = os.getenv("BOURSO_PASSWORD")

    if not username or not password:
        raise ValueError("BOURSO_USERNAME and BOURSO_PASSWORD environment variables are required.")
    
    page.goto('https://www.boursorama.com/', wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")

    # Check cookies not necessary because we use dispatch_event("click"), bypasses the interface and directly triggers the event

    page.locator("#login-member").dispatch_event("click")

    page.locator("#login_member_login").fill(username)
    page.locator("#login_member_password").fill(password)

    page.locator("body").dispatch_event("click")
    page.wait_for_timeout(500)

    page.locator("#login_member_connect").dispatch_event("click")
    page.wait_for_load_state("networkidle")

    topbar = page.locator("div.topbar-header__full")
    logged_in_member_name = topbar.locator("span.c-link-media__content.c-navigation__header-logged-member")

    if logged_in_member_name.inner_text().strip().upper() == username.upper():
        context.storage_state(path="playwright/.auth/state.json")
        print("Authenticated successfully !")
        return True
    else:
        print("Authentication failed.")
        return False