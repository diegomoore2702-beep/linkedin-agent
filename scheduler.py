import json
import sys
import os
import logging
from pathlib import Path
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from trends import get_trends
from writer import generar_post
from publisher import publicar_en_linkedin
from memory.memory import registrar_post
from carousel_generator import generar_carrusel
from engagement_tracker import actualizar_engagement

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(message)s")

def cargar_config(config_path: str) -> dict:
    with open(config_path) as f:
        config = json.load(f)

    # Variables de entorno sobreescriben el config (para Railway)
    if os.getenv("LINKEDIN_EMAIL"):
        config["linkedin_email"] = os.getenv("LINKEDIN_EMAIL")
    if os.getenv("LINKEDIN_PASSWORD"):
        config["linkedin_password"] = os.getenv("LINKEDIN_PASSWORD")
    if os.getenv("TELEGRAM_TOKEN"):
        config["telegram_token"] = os.getenv("TELEGRAM_TOKEN")
    if os.getenv("TELEGRAM_CHAT_ID"):
        config["telegram_chat_id"] = os.getenv("TELEGRAM_CHAT_ID")
    if os.getenv("INSTAGRAM_USERNAME"):
        config["instagram_username"] = os.getenv("INSTAGRAM_USERNAME")
    if os.getenv("INSTAGRAM_PASSWORD"):
        config["instagram_password"] = os.getenv("INSTAGRAM_PASSWORD")

    return config

def publicar_automatico(config_path: str):
    config = cargar_config(config_path)
    logging.info(f"Iniciando agente para: {config['nombre']}")

    try:
        # 1. Actualizar engagement de posts anteriores
        try:
            actualizar_engagement(config_path)
        except Exception as e:
            logging.warning(f"No se pudo actualizar engagement: {e}")

        # 2. Generar post
        tendencias = get_trends(config["industria"])
        logging.info(f"Tendencias: {len(tendencias)}")
        post = generar_post(config, tendencias)

        logging.info(f"Post generado ({len(post)} chars)")

        # 3. Generar carrusel
        foto_path = config.get("foto_path", "config/foto.jpg")
        estilo = config.get("estilo_carrusel", "clasico")
        carrusel_path = generar_carrusel(post, config, foto_path, estilo)

        # 4. Guardar post
        output = Path("posts") / f"{config['nombre'].replace(' ', '_')}_{datetime.now().strftime('%Y-%m-%d')}.txt"
        output.parent.mkdir(exist_ok=True)
        output.write_text(post)

        # 5. Aprobación por Telegram
        post_aprobado = post
        if config.get("telegram_token") and config.get("telegram_chat_id"):
            from telegram_approval import enviar_y_esperar_aprobacion
            post_aprobado = enviar_y_esperar_aprobacion(
                config["telegram_token"],
                config["telegram_chat_id"],
                post
            )
            if not post_aprobado:
                logging.info("Post descartado por el usuario.")
                return
        else:
            logging.warning("Sin Telegram configurado — publicando sin aprobación.")

        # 6. Publicar en LinkedIn
        if config.get("linkedin_email") and config.get("linkedin_password"):
            publicar_en_linkedin(
                config["linkedin_email"],
                config["linkedin_password"],
                post_aprobado,
                carrusel_path
            )
            logging.info("Publicado en LinkedIn.")

        # 7. Publicar en Instagram
        if config.get("instagram_username") and config.get("instagram_password") and carrusel_path:
            try:
                from instagram_publisher import publicar_en_instagram
                publicar_en_instagram(
                    config["instagram_username"],
                    config["instagram_password"],
                    post_aprobado,
                    carrusel_path
                )
                logging.info("Publicado en Instagram.")
            except Exception as e:
                logging.warning(f"Error Instagram: {e}")

        # 8. Guardar en memoria
        registrar_post(config["nombre"], post_aprobado)
        logging.info("Post guardado en memoria.")

    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/ejemplo_cliente.json"

    config = cargar_config(config_path)
    hora = config.get("hora_publicacion", "08:00")
    hora_h, hora_m = hora.split(":")

    scheduler = BlockingScheduler()
    scheduler.add_job(
        publicar_automatico,
        "cron",
        hour=int(hora_h),
        minute=int(hora_m),
        args=[config_path]
    )

    logging.info(f"Scheduler activo — publicará cada día a las {hora} para {config['nombre']}")
    logging.info("Ctrl+C para detener.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler detenido.")
