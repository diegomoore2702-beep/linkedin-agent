# LinkedIn AI Agent

Agente de LinkedIn que genera y publica contenido automáticamente — aprende tu estilo, mejora con el tiempo, y corre 24/7 en la nube sin que toques nada.

## Qué hace

- **Genera posts** que suenan como tú, no como IA — aprende de tu historial
- **A/B testing automático** — genera 2 versiones y publica la mejor
- **Score de calidad** — evalúa cada post antes de publicar, regenera si no es bueno
- **Rotación de formatos** — alterna entre opinión, historia, lista, datos y pregunta para variar el contenido
- **Carruseles PDF** — genera slides profesionales con tu foto y colores
- **Primer comentario automático** — publica un comentario 3 min después del post para aumentar el alcance
- **Memoria persistente** — aprende de cada post y mejora con el tiempo
- **Analytics** — muestra qué funciona, qué temas tienen más engagement y la tendencia

## Stack

- Python 3.12
- Claude API (Anthropic) — generación de contenido e inteligencia
- Playwright — automatización del navegador
- ReportLab + Pillow — generación de carruseles PDF
- APScheduler — programación de tareas
- Docker + Railway — deploy en la nube

## Instalación

```bash
git clone https://github.com/diegomoore2702-beep/linkedin-agent.git
cd linkedin-agent
pip install -r requirements.txt
playwright install chromium
```

Guarda tu API key de Anthropic:
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.zprofile
source ~/.zprofile
```

## Configuración

Edita `config/ejemplo_cliente.json`:

```json
{
  "nombre": "Tu Nombre",
  "industria": "finanzas",
  "tono": "casual y directo",
  "temas_clave": ["IA", "finanzas", "startups"],
  "idioma": "español",
  "hora_publicacion": "08:00",
  "linkedin_email": "tu@email.com",
  "linkedin_password": "...",
  "card_fondo": "#0D0D0D",
  "card_acento": "#C9A02C",
  "card_texto": "#FFFFFF"
}
```

Agrega tu foto en `config/foto.jpg`.

## Uso

```bash
# Aprender tu estilo desde posts existentes
python importer.py config/ejemplo_cliente.json

# Generar post + carrusel sin publicar
python main.py config/ejemplo_cliente.json --solo-generar

# Generar y publicar
python main.py config/ejemplo_cliente.json

# Con tema específico
python main.py config/ejemplo_cliente.json --tema "por qué los múltiplos de valoración fallan en LATAM"

# Con estilo de carrusel diferente
python main.py config/ejemplo_cliente.json --estilo minimalista

# Ver analytics
python analytics.py config/ejemplo_cliente.json

# Publicación automática diaria
python scheduler.py config/ejemplo_cliente.json
```

## Estilos de carrusel

| Estilo | Descripción |
|---|---|
| `clasico` | Fondo negro, acento dorado (default) |
| `minimalista` | Fondo blanco, texto negro |
| `claro` | Fondo gris claro, acento azul |
| `foto-grande` | Fondo oscuro azul, acento rojo |

## Deploy en Railway (24/7 sin computador)

Ver instrucciones en [DEPLOY-RAILWAY.md](DEPLOY-RAILWAY.md).

## Variables de entorno

```
ANTHROPIC_API_KEY
LINKEDIN_EMAIL
LINKEDIN_PASSWORD
INSTAGRAM_USERNAME
INSTAGRAM_PASSWORD
```

---

Built with Claude API · Anthropic
