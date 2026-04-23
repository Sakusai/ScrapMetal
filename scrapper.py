from playwright.sync_api import sync_playwright
from datetime import datetime
import pandas as pd
import re

def scrape_boursorama_action(url: str) -> dict:
    """
    Scrape les données du cours du jour d'une action Boursorama.
    Compatible avec les URLs de type : https://www.boursorama.com/cours/1rP74SW/

    Returns:
        dict avec : collecte_at, nom_action, isin, cours, variation,
                    cours_ouverture, cours_haut, cours_bas, volume, dernier_echange
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

        collecte_at = datetime.now()
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        page.wait_for_selector("h1", timeout=15_000)

        data = {
            "collected_at": collecte_at.strftime("%Y-%m-%d %H:%M:%S"),
            "url": url,
            "nom_action": None,
            "isin": None,
            "cours": None,
            "variation": None,
            "cours_ouverture": None,
            "cours_haut": None,
            "cours_bas": None,
            "volume": None,
            "dernier_echange": None,
        }

        body_text = page.locator("body").inner_text()

        try:
            h1 = page.locator("h1").first.inner_text().strip()
            data["nom_action"] = re.sub(r"^Cours\s+", "", h1)
        except Exception:
            pass

        try:
            m = re.search(r"\b([A-Z]{2}[A-Z0-9]{10})\b", body_text)
            if m:
                data["isin"] = m.group(1)
        except Exception:
            pass

        try:
            for part in page.title().split():
                val = _parse_float(part)
                if val and val > 0:
                    data["cours"] = val
                    break
        except Exception:
            pass

        try:
            m = re.search(r"([+-][\d,\s]+%)", body_text)
            if m:
                data["variation"] = m.group(1).strip()
        except Exception:
            pass


        t = body_text.lower()

        patterns = {
            "cours_ouverture": r"ouverture\s*\n\s*([\d\s]+[,.][\d]+)",
            "cours_haut":      r"\+\s*haut\s*\n\s*([\d\s]+[,.][\d]+)",
            "cours_bas":       r"\+\s*bas\s*\n\s*([\d\s]+[,.][\d]+)",
            "volume":          r"volume\s*\n\s*([\d\s]+)\n",
            "dernier_echange": r"dernier échange\s*\n\s*(.+)",
        }

        for key, pattern in patterns.items():
            m = re.search(pattern, t)
            if m:
                raw = m.group(1)
                if key == "volume":
                    data[key] = _parse_volume(raw)
                elif key == "dernier_echange":
                    data[key] = raw.strip()
                else:
                    data[key] = _parse_float(raw)

        browser.close()
        return data


def scrape_multiple_actions(urls: list[str]) -> pd.DataFrame:
    """Scrape plusieurs actions et retourne un DataFrame consolidé."""
    results = []
    for url in urls:
        print(f"Scraping : {url}")
        try:
            row = scrape_boursorama_action(url)
            results.append(row)
            print(f"  ✓ {row['nom_action']} — cours : {row['cours']}")
        except Exception as e:
            print(f"  ✗ Erreur : {e}")
            results.append({"url": url, "erreur": str(e)})
    return pd.DataFrame(results)



def _parse_float(text: str) -> float | None:
    """'1 234,56' ou '32,9000 EUR'  →  float"""
    if not text:
        return None
    try:
        cleaned = re.sub(r"[^\d,.\-]", "", text.strip()).replace(",", ".")
        parts = cleaned.split(".")
        if len(parts) > 2:
            cleaned = "".join(parts[:-1]) + "." + parts[-1]
        return float(cleaned) if cleaned else None
    except Exception:
        return None


def _parse_volume(text: str) -> int | None:
    """'12 345'  →  12345"""
    if not text:
        return None
    try:
        cleaned = re.sub(r"[^\d]", "", text)
        return int(cleaned) if cleaned else None
    except Exception:
        return None


def scrape():
    URLS = [
        "https://www.boursorama.com/cours/1rP74SW/",   
        "https://www.boursorama.com/cours/1rPAIR/",  
    ]

    df = scrape_multiple_actions(URLS)

    print("\n=== Résultat ===")
    print(df.to_string(index=False))

    df.to_csv("boursorama_cours.csv", index=False, encoding="utf-8-sig")
    print("\nCSV exporté : boursorama_cours.csv")