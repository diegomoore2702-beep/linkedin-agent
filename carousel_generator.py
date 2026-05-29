"""
Genera un carrusel PDF profesional para LinkedIn.
Cada página es una slide del carrusel.
"""
import anthropic
import json
from pathlib import Path
from datetime import datetime
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

client = anthropic.Anthropic()

# Colores por defecto
FONDO = colors.HexColor("#0D0D0D")
ACENTO = colors.HexColor("#C9A02C")
BLANCO = colors.HexColor("#FFFFFF")
GRIS = colors.HexColor("#888888")

W, H = 1080, 1080  # cuadrado como Instagram/LinkedIn carrusel

def generar_contenido_carrusel(post: str, config: dict) -> list[dict]:
    respuesta = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": f"""Basándote en este post de LinkedIn, crea el contenido para un carrusel de 5-6 slides.

POST:
{post}

PERFIL: {config.get('nombre','')}, estudiante de {config.get('industria','negocios')}, tono: {config.get('tono','casual')}

Responde en JSON con esta estructura exacta:
{{
  "slides": [
    {{
      "tipo": "portada",
      "titulo": "frase gancho impactante, máximo 8 palabras",
      "subtitulo": "contexto en una línea"
    }},
    {{
      "tipo": "contenido",
      "numero": "01",
      "titulo": "punto clave",
      "cuerpo": "explicación en 2-3 líneas cortas, lenguaje simple"
    }},
    {{
      "tipo": "contenido",
      "numero": "02",
      "titulo": "punto clave",
      "cuerpo": "explicación en 2-3 líneas cortas"
    }},
    {{
      "tipo": "contenido",
      "numero": "03",
      "titulo": "punto clave",
      "cuerpo": "explicación en 2-3 líneas cortas"
    }},
    {{
      "tipo": "contenido",
      "numero": "04",
      "titulo": "punto clave",
      "cuerpo": "explicación en 2-3 líneas cortas"
    }},
    {{
      "tipo": "cierre",
      "pregunta": "pregunta que invite a comentar",
      "nombre": "{config['nombre']}"
    }}
  ]
}}

Solo el JSON, sin explicaciones."""
        }]
    )

    try:
        texto = respuesta.content[0].text.strip()
        if texto.startswith("```"):
            texto = texto.split("```")[1]
            if texto.startswith("json"):
                texto = texto[4:]
        return json.loads(texto)["slides"]
    except Exception as e:
        print(f"Error generando contenido: {e}")
        return []

def dibujar_slide_portada(c, slide: dict, config: dict, colores_config: dict):
    fondo = colors.HexColor(colores_config.get("card_fondo", "#0D0D0D"))
    acento = colors.HexColor(colores_config.get("card_acento", "#C9A02C"))

    c.setFillColor(fondo)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Línea de acento arriba
    c.setFillColor(acento)
    c.rect(0, H - 8, W, 8, fill=1, stroke=0)

    # Línea de acento abajo
    c.rect(0, 0, W, 8, fill=1, stroke=0)

    # Número de slide
    c.setFillColor(acento)
    c.setFont("Helvetica", 20)
    c.drawString(60, H - 60, "01")

    # Título grande
    c.setFillColor(BLANCO)
    titulo = slide.get("titulo", "")
    _dibujar_texto_centrado(c, titulo, W // 2, H // 2 + 60, "Helvetica-Bold", 64, W - 120, acento)

    # Subtítulo
    c.setFillColor(GRIS)
    c.setFont("Helvetica", 28)
    subtitulo = slide.get("subtitulo", "")
    _dibujar_texto_centrado(c, subtitulo, W // 2, H // 2 - 60, "Helvetica", 28, W - 160)

    # Nombre
    c.setFillColor(acento)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W // 2, 50, config.get("nombre", "").upper())

def dibujar_slide_contenido(c, slide: dict, colores_config: dict):
    fondo = colors.HexColor(colores_config.get("card_fondo", "#0D0D0D"))
    acento = colors.HexColor(colores_config.get("card_acento", "#C9A02C"))

    c.setFillColor(fondo)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Barra lateral izquierda
    c.setFillColor(acento)
    c.rect(0, 0, 8, H, fill=1, stroke=0)

    # Número grande de fondo (decorativo)
    c.setFillColor(colors.HexColor("#1a1a1a"))
    c.setFont("Helvetica-Bold", 220)
    c.drawString(W - 250, 20, slide.get("numero", "01"))

    # Número pequeño
    c.setFillColor(acento)
    c.setFont("Helvetica-Bold", 32)
    c.drawString(60, H - 80, slide.get("numero", "01"))

    # Línea dorada bajo el número
    c.setStrokeColor(acento)
    c.setLineWidth(2)
    c.line(60, H - 95, 120, H - 95)

    # Título del punto
    c.setFillColor(BLANCO)
    titulo = slide.get("titulo", "")
    _dibujar_texto_izquierda(c, titulo, 60, H - 200, "Helvetica-Bold", 52, W - 120)

    # Cuerpo
    c.setFillColor(colors.HexColor("#CCCCCC"))
    cuerpo = slide.get("cuerpo", "")
    _dibujar_texto_izquierda(c, cuerpo, 60, H - 380, "Helvetica", 32, W - 120)

def dibujar_slide_cierre(c, slide: dict, config: dict, foto_path: str, colores_config: dict):
    fondo = colors.HexColor(colores_config.get("card_fondo", "#0D0D0D"))
    acento = colors.HexColor(colores_config.get("card_acento", "#C9A02C"))

    c.setFillColor(fondo)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Líneas de acento
    c.setFillColor(acento)
    c.rect(0, H - 8, W, 8, fill=1, stroke=0)
    c.rect(0, 0, W, 8, fill=1, stroke=0)

    # Foto circular si existe
    if foto_path and Path(foto_path).exists():
        try:
            from PIL import Image as PILImage
            import io
            foto = PILImage.open(foto_path).convert("RGBA")
            size = 200
            foto = foto.resize((size, size))

            from PIL import ImageDraw as PILDraw
            mask = PILImage.new("L", (size, size), 0)
            draw = PILDraw.Draw(mask)
            draw.ellipse([(0, 0), (size, size)], fill=255)

            output = PILImage.new("RGBA", (size, size), (0, 0, 0, 0))
            output.paste(foto, (0, 0))
            output.putalpha(mask)

            buf = io.BytesIO()
            output.save(buf, format="PNG")
            buf.seek(0)

            foto_x = (W - size) // 2
            foto_y = H // 2 + 20
            c.drawImage(ImageReader(buf), foto_x, foto_y, size, size, mask="auto")
        except Exception:
            pass

    # Pregunta
    c.setFillColor(BLANCO)
    pregunta = slide.get("pregunta", "¿Qué opinas tú?")
    _dibujar_texto_centrado(c, pregunta, W // 2, H - 180, "Helvetica-Bold", 42, W - 120)

    # Nombre
    c.setFillColor(acento)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(W // 2, H // 2 - 20, config.get("nombre", "").upper())

    c.setFillColor(GRIS)
    c.setFont("Helvetica", 22)
    c.drawCentredString(W // 2, H // 2 - 55, config.get("industria", "").capitalize())

def _dibujar_texto_centrado(c, texto: str, x: int, y: int, fuente: str, size: int, max_ancho: int, color_alt=None):
    c.setFont(fuente, size)
    palabras = texto.split()
    lineas = []
    linea = ""
    for palabra in palabras:
        prueba = f"{linea} {palabra}".strip()
        if c.stringWidth(prueba, fuente, size) <= max_ancho:
            linea = prueba
        else:
            if linea:
                lineas.append(linea)
            linea = palabra
    if linea:
        lineas.append(linea)

    alto_total = len(lineas) * (size + 10)
    y_actual = y + alto_total // 2

    for i, linea in enumerate(lineas):
        if color_alt and i == 0:
            c.setFillColor(color_alt)
        c.drawCentredString(x, y_actual, linea)
        y_actual -= (size + 10)
        if color_alt and i == 0:
            c.setFillColor(BLANCO)

def _dibujar_texto_izquierda(c, texto: str, x: int, y: int, fuente: str, size: int, max_ancho: int):
    c.setFont(fuente, size)
    palabras = texto.split()
    lineas = []
    linea = ""
    for palabra in palabras:
        prueba = f"{linea} {palabra}".strip()
        if c.stringWidth(prueba, fuente, size) <= max_ancho:
            linea = prueba
        else:
            if linea:
                lineas.append(linea)
            linea = palabra
    if linea:
        lineas.append(linea)

    y_actual = y
    for linea in lineas:
        c.drawString(x, y_actual, linea)
        y_actual -= (size + 12)

ESTILOS = {
    "clasico":      {"fondo": "#0D0D0D", "acento": "#C9A02C", "texto": "#FFFFFF", "secundario": "#888888"},
    "minimalista":  {"fondo": "#FFFFFF", "acento": "#0D0D0D", "texto": "#0D0D0D", "secundario": "#555555"},
    "claro":        {"fondo": "#F5F5F5", "acento": "#2563EB", "texto": "#111111", "secundario": "#666666"},
    "foto-grande":  {"fondo": "#1a1a2e", "acento": "#E94560", "texto": "#FFFFFF", "secundario": "#AAAAAA"},
}

def generar_carrusel(post: str, config: dict, foto_path: str = None, estilo: str = "clasico") -> str | None:
    try:
        estilo_data = ESTILOS.get(estilo, ESTILOS["clasico"])
        colores_config = {
            "card_fondo":  config.get("card_fondo", estilo_data["fondo"]),
            "card_acento": config.get("card_acento", estilo_data["acento"]),
            "card_texto":  config.get("card_texto",  estilo_data["texto"]),
        }

        # Si el estilo no es clasico, usar los colores del estilo elegido
        if estilo != "clasico":
            colores_config = {
                "card_fondo":  estilo_data["fondo"],
                "card_acento": estilo_data["acento"],
                "card_texto":  estilo_data["texto"],
            }

        print(f"Generando contenido del carrusel (estilo: {estilo})...")
        slides = generar_contenido_carrusel(post, config)

        if not slides:
            print("No se pudo generar el contenido del carrusel.")
            return None

        carpeta = Path("posts/carruseles")
        carpeta.mkdir(parents=True, exist_ok=True)
        fecha = datetime.now().strftime("%Y-%m-%d")
        ruta = str(carpeta / f"{config['nombre'].replace(' ', '_')}_{fecha}_{estilo}.pdf")

        c = canvas.Canvas(ruta, pagesize=(W, H))

        for slide in slides:
            tipo = slide.get("tipo")
            if tipo == "portada":
                dibujar_slide_portada(c, slide, config, colores_config)
            elif tipo == "contenido":
                dibujar_slide_contenido(c, slide, colores_config)
            elif tipo == "cierre":
                dibujar_slide_cierre(c, slide, config, foto_path or "config/foto.jpg", colores_config)
            c.showPage()

        c.save()
        print(f"Carrusel generado: {ruta}")
        return ruta

    except Exception as e:
        print(f"Error generando carrusel: {e}")
        return None
