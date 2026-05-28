"""
Lee likes y comentarios de los últimos posts de LinkedIn
y actualiza la memoria para que el agente aprenda qué funciona.
"""
import sys
import json
import time
sys.path.insert(0, ".")
from playwright.sync_api import sync_playwright
from memory.memory import cargar_memoria, guardar_memoria

def actualizar_engagement(config_path: str):
    with open(config_path) as f:
        config = json.load(f)

    if not config.get("linkedin_email") or not config.get("linkedin_password"):
        print("Se necesitan credenciales de LinkedIn.")
        return

    memoria = cargar_memoria(config["nombre"])
    posts_sin_engagement = [
        p for p in memoria["posts_publicados"]
        if p["fecha"] != "importado" and p["engagement"]["likes"] == 0
    ]

    if not posts_sin_engagement:
        print("No hay posts pendientes de actualizar.")
        return

    print(f"Actualizando engagement de {len(posts_sin_engagement)} posts...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("https://www.linkedin.com/login")
            page.fill("#username", config["linkedin_email"])
            page.fill("#password", config["linkedin_password"])
            page.click('[type="submit"]')
            page.wait_for_url("**/feed**", timeout=15000)

            page.goto("https://www.linkedin.com/in/me/recent-activity/shares/")
            time.sleep(3)

            # Extraer engagement de cada post visible
            posts_en_pagina = page.query_selector_all(".feed-shared-update-v2")

            for post_el in posts_en_pagina[:10]:
                try:
                    texto_el = post_el.query_selector(".feed-shared-update-v2__description-wrapper")
                    if not texto_el:
                        continue
                    texto = texto_el.inner_text().strip()[:100]

                    # Buscar el post correspondiente en memoria
                    for post_memoria in posts_sin_engagement:
                        if texto in post_memoria["post"] or post_memoria["post"][:100] in texto:
                            # Extraer likes
                            likes_el = post_el.query_selector("[aria-label*='reactions'], .social-details-social-counts__reactions-count")
                            comentarios_el = post_el.query_selector("[aria-label*='comments'], .social-details-social-counts__comments")

                            likes = 0
                            comentarios = 0

                            if likes_el:
                                likes_text = likes_el.inner_text().strip().replace(",", "")
                                likes = int(likes_text) if likes_text.isdigit() else 0

                            if comentarios_el:
                                com_text = comentarios_el.inner_text().strip().split()[0].replace(",", "")
                                comentarios = int(com_text) if com_text.isdigit() else 0

                            post_memoria["engagement"] = {
                                "likes": likes,
                                "comentarios": comentarios,
                                "reposts": 0
                            }

                            if likes > 0 and post_memoria["post"] not in memoria["temas_exitosos"]:
                                # Guardar tema como exitoso si tuvo likes
                                resumen = post_memoria["post"][:80] + "..."
                                if resumen not in memoria["temas_exitosos"]:
                                    memoria["temas_exitosos"].append(resumen)

                            print(f"Post actualizado: {likes} likes, {comentarios} comentarios")
                            break

                except Exception:
                    continue

            browser.close()

        except Exception as e:
            print(f"Error: {e}")
            browser.close()
            return

    # Actualizar en memoria
    for post_actualizado in posts_sin_engagement:
        for i, post in enumerate(memoria["posts_publicados"]):
            if post["post"] == post_actualizado["post"]:
                memoria["posts_publicados"][i] = post_actualizado
                break

    guardar_memoria(memoria)
    print("Engagement actualizado en memoria.")

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/ejemplo_cliente.json"
    actualizar_engagement(config_path)
