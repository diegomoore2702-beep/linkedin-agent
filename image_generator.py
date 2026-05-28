"""
Genera una card profesional para LinkedIn con foto del cliente y frase clave del post.
Coloca la foto a la izquierda, la frase a la derecha, nombre abajo.
"""
import anthropic
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
from datetime import datetime

client = anthropic.Anthropic()

def hex_a_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def extraer_frase_clave(post: str) -> str:
    respuesta = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=80,
        messages=[{
            "role": "user",
            "content": f"""Del siguiente post de LinkedIn, extrae LA frase más impactante y corta (máximo 12 palabras).
Debe ser la idea central, la que haría que alguien pare el scroll.
Solo la frase, sin comillas ni explicaciones.

Post:
{post}"""
        }]
    )
    return respuesta.content[0].text.strip()

def crear_card(post: str, nombre: str, foto_path: str = None, colores: dict = None) -> str | None:
    try:
        c = colores or {}
        COLOR_FONDO = hex_a_rgb(c.get("card_fondo", "#0D0D0D"))
        COLOR_ACENTO = hex_a_rgb(c.get("card_acento", "#C9A02C"))
        COLOR_TEXTO = hex_a_rgb(c.get("card_texto", "#FFFFFF"))
        COLOR_NOMBRE = COLOR_ACENTO

        ancho, alto = 1200, 627
        img = Image.new("RGB", (ancho, alto), COLOR_FONDO)
        draw = ImageDraw.Draw(img)

        # Línea de acento izquierda
        draw.rectangle([(0, 0), (6, alto)], fill=COLOR_ACENTO)

        # Foto del cliente (si existe)
        foto_x = 80
        foto_size = 300

        if foto_path and Path(foto_path).exists():
            foto = Image.open(foto_path).convert("RGB")
            foto = foto.resize((foto_size, foto_size))

            # Recortar en círculo
            mask = Image.new("L", (foto_size, foto_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse([(0, 0), (foto_size, foto_size)], fill=255)
            foto_circular = ImageOps.fit(foto, (foto_size, foto_size))
            foto_circular.putalpha(mask)

            foto_y = (alto - foto_size) // 2
            img.paste(foto_circular, (foto_x, foto_y), mask)

            # Círculo dorado alrededor de la foto
            draw.ellipse(
                [(foto_x - 4, foto_y - 4), (foto_x + foto_size + 4, foto_y + foto_size + 4)],
                outline=COLOR_ACENTO,
                width=3
            )

            texto_x = foto_x + foto_size + 60
        else:
            texto_x = 80

        # Frase clave
        frase = extraer_frase_clave(post)

        try:
            fuente_frase = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 52)
            fuente_nombre = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
            fuente_linea = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
        except Exception:
            fuente_frase = ImageFont.load_default()
            fuente_nombre = ImageFont.load_default()
            fuente_linea = ImageFont.load_default()

        # Dividir frase en líneas
        texto_max_ancho = ancho - texto_x - 80
        palabras = frase.split()
        lineas = []
        linea_actual = ""
        for palabra in palabras:
            prueba = f"{linea_actual} {palabra}".strip()
            bbox = draw.textbbox((0, 0), prueba, font=fuente_frase)
            if bbox[2] <= texto_max_ancho:
                linea_actual = prueba
            else:
                if linea_actual:
                    lineas.append(linea_actual)
                linea_actual = palabra
        if linea_actual:
            lineas.append(linea_actual)

        # Centrar verticalmente el texto
        alto_linea = 65
        alto_total_texto = len(lineas) * alto_linea + 60
        texto_y = (alto - alto_total_texto) // 2

        # Comilla de apertura dorada
        draw.text((texto_x, texto_y - 10), "❝", font=fuente_frase, fill=COLOR_ACENTO)
        texto_y += 55

        for linea in lineas:
            draw.text((texto_x, texto_y), linea, font=fuente_frase, fill=COLOR_TEXTO)
            texto_y += alto_linea

        # Línea separadora dorada
        draw.rectangle([(texto_x, texto_y + 10), (texto_x + 60, texto_y + 13)], fill=COLOR_ACENTO)

        # Nombre
        draw.text((texto_x, texto_y + 25), nombre, font=fuente_nombre, fill=COLOR_NOMBRE)

        # Guardar
        carpeta = Path("posts/imagenes")
        carpeta.mkdir(parents=True, exist_ok=True)
        fecha = datetime.now().strftime("%Y-%m-%d")
        ruta = carpeta / f"{nombre.replace(' ', '_')}_{fecha}.jpg"
        img = img.convert("RGB")
        img.save(str(ruta), "JPEG", quality=95)

        print(f"Card generada: {ruta}")
        return str(ruta)

    except Exception as e:
        print(f"Error generando card: {e}")
        return None

def generar_imagen(post: str, nombre: str, industria: str = "", foto_path: str = None, colores: dict = None) -> str | None:
    return crear_card(post, nombre, foto_path, colores)
