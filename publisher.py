import time
from playwright.sync_api import sync_playwright

def publicar_en_linkedin(email: str, password: str, texto: str) -> bool:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            # Login
            page.goto("https://www.linkedin.com/login")
            page.fill("#username", email)
            page.fill("#password", password)
            page.click('[type="submit"]')
            page.wait_for_url("**/feed**", timeout=15000)

            # Abrir modal de post
            page.click('button:has-text("Comenzar una publicación"), button:has-text("Start a post")')
            time.sleep(2)

            # Escribir el post
            editor = page.locator('.ql-editor, [role="textbox"]').first
            editor.click()
            editor.type(texto, delay=20)
            time.sleep(1)

            # Publicar
            page.click('button:has-text("Publicar"), button:has-text("Post")')
            time.sleep(3)

            print("Post publicado en LinkedIn.")
            browser.close()
            return True

        except Exception as e:
            print(f"Error al publicar: {e}")
            browser.close()
            return False
