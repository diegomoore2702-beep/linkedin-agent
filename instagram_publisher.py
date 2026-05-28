"""
Publica en Instagram usando instagrapi.
Requiere: pip install instagrapi
"""
import sys

def publicar_en_instagram(username: str, password: str, texto: str, imagen_path: str = None) -> bool:
    try:
        from instagrapi import Client
    except ImportError:
        print("Instala instagrapi: pip install instagrapi")
        return False

    try:
        cl = Client()
        cl.login(username, password)

        if imagen_path:
            cl.photo_upload(imagen_path, texto)
            print("Post con imagen publicado en Instagram.")
        else:
            # Sin imagen: publicar como reel de texto (carousel de fondo sólido)
            print("Instagram requiere imagen. Genera una con image_generator.py primero.")
            return False

        return True

    except Exception as e:
        print(f"Error publicando en Instagram: {e}")
        return False
