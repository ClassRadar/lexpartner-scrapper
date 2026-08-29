import os
import functions_framework
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

CLAVE_SECRETA = os.environ.get("CLAVE_SCRAPER", "")


@functions_framework.http
def scraping_saij(request):
        headers_cors = {"Access-Control-Allow-Origin": "*"}

    if request.method == "OPTIONS":
        headers_cors["Access-Control-Allow-Methods"] = "POST"
        headers_cors["Access-Control-Allow-Headers"] = "Content-Type, X-Clave-Secreta"
        return "", 204, headers_cors

    if request.headers.get("X-Clave-Secreta") != CLAVE_SECRETA:
        return {"error": "No autorizado"}, 401, headers_cors

    request_json = request.get_json(silent=True)
    if not request_json or "url" not in request_json:
        return {"error": "Falta el parámetro 'url'"}, 400

    target_url = request_json["url"]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        )
        page = context.new_page()
        stealth_sync(page)

        try:
            page.goto(target_url, wait_until="networkidle", timeout=30000)
            html_content = page.content()
            context.close()
            browser.close()
            return {"status": "success", "html": html_content}, 200
        except Exception as e:
            browser.close()
            return {"status": "error", "message": str(e)}, 500
