# Guía: Automatiza tus posts de LinkedIn con IA

**Tiempo estimado:** 30-40 minutos  
**Lo que necesitas:** VS Code instalado, $5 en créditos de Anthropic, cuenta de Telegram

Abre la terminal en VS Code con `Ctrl + J` (Windows) o `Cmd + J` (Mac) y sigue los pasos.

---

## Paso 1 — Instalar Python

**Mac:**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Cuando termine:
```bash
brew install python
```

**Windows (PowerShell como administrador):**
```powershell
winget install Python.Python.3.12
```

Verifica que quedó bien:
```bash
python --version
```
Debe mostrarte algo como `Python 3.12.x`.

---

## Paso 2 — Obtener tu API Key de Anthropic

1. Ve a [console.anthropic.com](https://console.anthropic.com) y crea una cuenta
2. Ve a **Plans & Billing** y carga $5
3. Ve a **API Keys** → **Create Key**
4. Copia la key — empieza con `sk-ant-...`

---

## Paso 3 — Descargar el agente

```bash
git clone https://github.com/diegomoore2702-beep/linkedin-agent.git
cd linkedin-agent
```

---

## Paso 4 — Guardar tu API Key

**Mac:**
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-PEGA-TU-KEY-AQUI"' >> ~/.zprofile
source ~/.zprofile
```

**Windows (PowerShell):**
```powershell
setx ANTHROPIC_API_KEY "sk-ant-PEGA-TU-KEY-AQUI"
```
Cierra y vuelve a abrir la terminal después de esto.

---

## Paso 5 — Instalar las dependencias

```bash
pip install anthropic feedparser apscheduler python-dotenv playwright requests
playwright install chromium
```

Esto puede tardar 2-3 minutos.

---

## Paso 6 — Configurar tu perfil

**Mac:**
```bash
open config/ejemplo_cliente.json
```

**Windows:**
```powershell
notepad config\ejemplo_cliente.json
```

Edítalo con tu información — deja telegram_token y telegram_chat_id vacíos por ahora:

```json
{
  "nombre": "Tu Nombre",
  "industria": "marketing",
  "tono": "profesional pero cercano, directo, sin frases de relleno",
  "temas_clave": ["tema1", "tema2", "tema3"],
  "idioma": "español",
  "hora_publicacion": "08:00",
  "linkedin_email": "tu@email.com",
  "linkedin_password": "tu_contraseña",
  "telegram_token": "",
  "telegram_chat_id": ""
}
```

Guarda con `Ctrl+S`.

---

## Paso 7 — Importar tus posts existentes (recomendado)

Esto hace que el agente suene como tú desde el primer día — analiza todos tus posts anteriores y aprende tu estilo.

```bash
python importer.py config/ejemplo_cliente.json
```

Se abrirá el navegador, entrará a LinkedIn y leerá tus posts. Tarda 1-2 minutos.

---

## Paso 8 — Generar tu primer post

```bash
python main.py config/ejemplo_cliente.json --solo-generar
```

El post se guarda en la carpeta `posts/`. Revísalo — si suena como tú, el sistema está funcionando.

---

## Paso 9 — Configurar aprobación por Telegram

Con esto te llega el post al cel antes de publicarse. Respondes SI y se publica solo.

### Crear tu bot de Telegram

1. Abre Telegram y busca **@BotFather**
2. Escríbele `/newbot`
3. Ponle un nombre (ej: `Mi LinkedIn Bot`)
4. Ponle un username que termine en `bot` (ej: `milinkedin_bot`)
5. BotFather te da un token — cópialo. Se ve así: `7123456789:AAFxxx...`

### Obtener tu Chat ID

1. Busca tu bot en Telegram y escríbele cualquier cosa (ej: `hola`)
2. Corre este comando reemplazando TU_TOKEN:
```bash
python -c "import requests; r=requests.get('https://api.telegram.org/botTU_TOKEN/getUpdates'); print(r.json())"
```
3. Busca el número después de `"id":` dentro de `"chat"` — ese es tu Chat ID

### Agregar al config

Abre el JSON y agrega:
```json
"telegram_token": "7123456789:AAFxxx...",
"telegram_chat_id": "123456789"
```

---

## Paso 10 — Publicación automática (mientras duermes)

```bash
python scheduler.py config/ejemplo_cliente.json
```

**Flujo completo:**
1. A las 8:00am el agente genera el post
2. Te llega por Telegram: *"📝 Post listo. Responde SI para publicar, NO para descartar, o EDITAR [tu versión]"*
3. Respondes desde el cel
4. Se publica automáticamente en LinkedIn

**Deja la ventana abierta y el computador encendido.**  
Para detenerlo: `Ctrl + C`

### Correr sin tener la terminal abierta (Mac)

Para que corra aunque cierres la terminal, configura un cron job:

```bash
crontab -e
```

Agrega esta línea (cambia la ruta si es diferente):
```
0 8 * * * cd /Users/TU_USUARIO/linkedin-agent && python scheduler.py config/ejemplo_cliente.json >> logs/cron.log 2>&1
```

Crea la carpeta de logs:
```bash
mkdir -p ~/linkedin-agent/logs
```

---

## Errores comunes

**"python: command not found"**
```bash
brew install python
```

**"anthropic: module not found"**
```bash
pip install anthropic
```

**"AuthenticationError"**  
→ Tu API key está mal o no tiene créditos. Verifica en [console.anthropic.com](https://console.anthropic.com).

**"git: command not found"**

Mac:
```bash
xcode-select --install
```
Windows:
```powershell
winget install Git.Git
```

**El bot de Telegram no responde**  
→ Verifica que escribiste algo al bot antes de buscar el chat_id. El bot solo recibe mensajes de chats donde alguien lo inició primero.

---

## Resumen de comandos

| Qué hacer | Comando |
|---|---|
| Importar posts existentes | `python importer.py config/ejemplo_cliente.json` |
| Generar post sin publicar | `python main.py config/ejemplo_cliente.json --solo-generar` |
| Publicar manualmente | `python main.py config/ejemplo_cliente.json` |
| Activar publicación automática | `python scheduler.py config/ejemplo_cliente.json` |
