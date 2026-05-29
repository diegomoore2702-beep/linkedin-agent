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
from first_comment import publicar_primer_comentario

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(message)s")

BASE_DIR = Path(__file__).parent

def cargar_config(config_path: str) -> dict:
    with open(config_path) as f:
        config = json.load(f)

    # Variables de entorno sobreescriben el config (para Railway)
    env_map = {
        "LINKEDIN_EMAIL": "linkedin_email",
        "LINKEDIN_PASSWORD": "linkedin_password",
        "INSTAGRAM_USERNAME": "instagram_username",
        "INSTAGRAM_PASSWORD": "instagram_password",
    }
    for env_key, config_key in env_map.items():
        if os.getenv(env_key):
            config[config_key] = os.getenv(env_key)

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
        tendencias = get_trends(config.get("industria", "negocios"))
        logging.info(f"Tendencias: {len(tendencias)}")
        post = generar_post(config, tendencias, tema=None)
        logging.info(f"Post generado ({len(post)} chars)")

        # 3. Generar carrusel
        foto_path = config.get("foto_path", str(BASE_DIR / "config" / "foto.jpg"))
        estilo = config.get("estilo_carrusel", "clasico")
        carrusel_path = generar_carrusel(post, config, foto_path, estilo)

        # 4. Guardar post
        output = BASE_DIR / "posts" / f"{config['nombre'].replace(' ', '_')}_{datetime.now().strftime('%Y-%m-%d')}.txt"
        output.parent.mkdir(exist_ok=True)
        output.write_text(post)
        logging.info(f"Post guardado en: {output}")

        # 5. Publicar en LinkedIn
        if config.get("linkedin_email") and config.get("linkedin_password"):
            publicar_en_linkedin(
                config["linkedin_email"],
                config["linkedin_password"],
                post,
                carrusel_path
            )
            logging.info("Publicado en LinkedIn.")
        else:
            logging.warning("Sin credenciales de LinkedIn.")

        # 6. Publicar en Instagram
        if config.get("instagram_username") and config.get("instagram_password") and carrusel_path:
            try:
                from instagram_publisher import publicar_en_instagram
                publicar_en_instagram(
                    config["instagram_username"],
                    config["instagram_password"],
                    post,
                    carrusel_path
                )
                logging.info("Publicado en Instagram.")
            except Exception as e:
                logging.warning(f"Error Instagram: {e}")

        # 7. Primer comentario automático
        if config.get("linkedin_email") and config.get("linkedin_password"):
            try:
                publicar_primer_comentario(
                    config["linkedin_email"],
                    config["linkedin_password"],
                    post,
                    config["nombre"]
                )
                logging.info("Primer comentario publicado.")
            except Exception as e:
                logging.warning(f"No se pudo publicar el primer comentario: {e}")

        # 8. Guardar en memoria
        registrar_post(config["nombre"], post)
        logging.info("Post guardado en memoria.")

    except Exception as e:
        logging.error(f"Error en publicar_automatico: {e}", exc_info=True)

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else str(BASE_DIR / "config" / "ejemplo_cliente.json")

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
