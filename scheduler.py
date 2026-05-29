import json
import sys
import os
import logging
from pathlib import Path
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(message)s")

BASE_DIR = Path(__file__).parent

def cargar_config(config_path: str) -> dict:
    with open(config_path) as f:
        config = json.load(f)

    env_map = {
        "ANTHROPIC_API_KEY": None,  # lo usa el SDK directamente
        "LINKEDIN_EMAIL": "linkedin_email",
        "LINKEDIN_PASSWORD": "linkedin_password",
        "INSTAGRAM_USERNAME": "instagram_username",
        "INSTAGRAM_PASSWORD": "instagram_password",
    }
    for env_key, config_key in env_map.items():
        if config_key and os.getenv(env_key):
            config[config_key] = os.getenv(env_key)

    return config

def publicar_automatico(config_path: str):
    config = cargar_config(config_path)
    nombre = config.get("nombre", "usuario")
    logging.info(f"— Iniciando ciclo para: {nombre} —")

    post = None
    carrusel_path = None

    # 1. Actualizar engagement (no crítico)
    try:
        from engagement_tracker import actualizar_engagement
        actualizar_engagement(config_path)
        logging.info("Engagement actualizado.")
    except Exception as e:
        logging.warning(f"Engagement skipped: {e}")

    # 2. Generar post (crítico)
    try:
        from trends import get_trends
        from writer import generar_post
        tendencias = get_trends(config.get("industria", "negocios"))
        post = generar_post(config, tendencias, tema=None)
        logging.info(f"Post generado ({len(post)} chars)")
    except Exception as e:
        logging.error(f"Error generando post: {e}")
        return  # sin post no hay nada que hacer

    # 3. Guardar post en disco
    try:
        output = BASE_DIR / "posts" / f"{nombre.replace(' ', '_')}_{datetime.now().strftime('%Y-%m-%d')}.txt"
        output.parent.mkdir(exist_ok=True)
        output.write_text(post, encoding="utf-8")
        logging.info(f"Post guardado: {output.name}")
    except Exception as e:
        logging.warning(f"No se pudo guardar el post en disco: {e}")

    # 4. Generar carrusel (no crítico)
    try:
        from carousel_generator import generar_carrusel
        foto_path = config.get("foto_path", str(BASE_DIR / "config" / "foto.jpg"))
        estilo = config.get("estilo_carrusel", "clasico")
        carrusel_path = generar_carrusel(post, config, foto_path, estilo)
        if carrusel_path:
            logging.info(f"Carrusel generado: {Path(carrusel_path).name}")
        else:
            logging.warning("Carrusel no generado — continuando sin él.")
    except Exception as e:
        logging.warning(f"Carrusel skipped: {e}")

    # 5. Publicar en LinkedIn (crítico si hay credenciales)
    publicado_linkedin = False
    if config.get("linkedin_email") and config.get("linkedin_password"):
        try:
            from publisher import publicar_en_linkedin
            publicar_en_linkedin(
                config["linkedin_email"],
                config["linkedin_password"],
                post,
                carrusel_path
            )
            publicado_linkedin = True
            logging.info("Publicado en LinkedIn.")
        except Exception as e:
            logging.error(f"Error publicando en LinkedIn: {e}")

    # 6. Publicar en Instagram (no crítico)
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
            logging.warning(f"Instagram skipped: {e}")

    # 7. Primer comentario (no crítico, solo si publicó en LinkedIn)
    if publicado_linkedin and config.get("linkedin_email"):
        try:
            from first_comment import publicar_primer_comentario
            publicar_primer_comentario(
                config["linkedin_email"],
                config["linkedin_password"],
                post,
                nombre
            )
            logging.info("Primer comentario publicado.")
        except Exception as e:
            logging.warning(f"Primer comentario skipped: {e}")

    # 8. Guardar en memoria (no crítico)
    try:
        from memory.memory import registrar_post
        registrar_post(nombre, post)
        logging.info("Post guardado en memoria.")
    except Exception as e:
        logging.warning(f"Memoria skipped: {e}")

    logging.info(f"— Ciclo completado para: {nombre} —")

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

    logging.info(f"Scheduler activo — publicará cada día a las {hora} para {config.get('nombre', 'usuario')}")
    logging.info("Ctrl+C para detener.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler detenido.")
