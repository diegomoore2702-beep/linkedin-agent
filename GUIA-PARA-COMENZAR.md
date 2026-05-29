# Guía: Automatiza tus posts de LinkedIn con IA

**Tiempo estimado:** 30-40 minutos  
**Lo que necesitas:** VS Code instalado, $5 en créditos de Anthropic

Abre la terminal en VS Code con `Ctrl + J` (Windows) o `Cmd + J` (Mac) y sigue los pasos en orden.

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

Verifica:
```bash
python --version
```
Debe mostrar `Python 3.12.x`.

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
Cierra y vuelve a abrir la terminal.

---

## Paso 5 — Instalar las dependencias

```bash
pip install -r requirements.txt
playwright install chromium
```

Tarda 2-3 minutos.

---

## Paso 6 — Agregar tu foto

Copia una foto tuya (preferiblemente de perfil) a la carpeta `config/` y renómbrala `foto.jpg`.

**Mac:**
```bash
open config/
```
Arrastra tu foto ahí y renómbrala `foto.jpg`.

---

## Paso 7 — Configurar tu perfil

**Mac:**
```bash
open config/ejemplo_cliente.json
```

**Windows:**
```powershell
notepad config\ejemplo_cliente.json
```

Edítalo con tus datos:

```json
{
  "nombre": "Tu Nombre",
  "industria": "tu industria (ej: marketing, finanzas, tecnología)",
  "tono": "cómo hablas normalmente (ej: casual y curioso, directo, con humor)",
  "temas_clave": ["tema1", "tema2", "tema3"],
  "idioma": "español",
  "hora_publicacion": "08:00",
  "linkedin_email": "tu@email.com",
  "linkedin_password": "tu_contraseña",
  "instagram_username": "",
  "instagram_password": "",
  "telegram_token": "",
  "telegram_chat_id": "",
  "card_fondo": "#0D0D0D",
  "card_acento": "#C9A02C",
  "card_texto": "#FFFFFF"
}
```

**Colores:** cambia `card_acento` por el color que quieras. Ejemplos: `#E94560` (rojo), `#00B4D8` (azul), `#7B2FBE` (morado).

Guarda con `Ctrl+S`.

---

## Paso 8 — Importar tus posts existentes

Esto hace que el agente aprenda cómo escribes desde el primer día.

```bash
python importer.py config/ejemplo_cliente.json
```

Se abre el navegador. Si LinkedIn pide verificación, complétala manualmente. Cuando estés en el feed presiona Enter en la terminal.

---

## Paso 9 — Generar tu primer carrusel

```bash
python main.py config/ejemplo_cliente.json --solo-generar
```

Genera el texto del post y un **carrusel PDF** listo para subir a LinkedIn. El carrusel queda en `posts/carruseles/`. Ábrelo para ver cómo quedó.

---

## Paso 10 — Publicar en LinkedIn

```bash
python main.py config/ejemplo_cliente.json
```

El flujo:
1. Genera el post y el carrusel
2. Abre LinkedIn en el navegador con el texto ya escrito
3. Abre el Finder con el PDF del carrusel para que lo arrastres al modal
4. Tú revisas, adjuntas el PDF y publicas
5. Presionas Enter en la terminal para confirmar

---

## Paso 11 — Configurar Telegram (para aprobar desde el cel)

Con esto te llega el carrusel + post al cel antes de publicar. Respondes SI para publicar o NO para descartar.

### Crear tu bot

1. Abre Telegram y busca **@BotFather**
2. Escríbele `/newbot`
3. Ponle nombre y username (debe terminar en `bot`)
4. Copia el token que te da — se ve así: `7123456789:AAFxxx...`

### Obtener tu Chat ID

1. Escríbele cualquier cosa a tu bot en Telegram
2. Corre esto reemplazando TU_TOKEN:
```bash
python -c "import requests; r=requests.get('https://api.telegram.org/botTU_TOKEN/getUpdates'); print(r.json())"
```
3. El número después de `"id":` dentro de `"chat"` es tu Chat ID

### Agregar al config
```json
"telegram_token": "7123456789:AAFxxx...",
"telegram_chat_id": "123456789"
```

---

## Paso 12 — Publicación automática diaria

```bash
python scheduler.py config/ejemplo_cliente.json
```

Cada día a la hora configurada:
1. Genera el post y carrusel automáticamente
2. Te manda el texto por Telegram
3. Respondes SI o NO desde el cel
4. Abre el navegador para que publiques (10 segundos de trabajo)

**Deja la terminal abierta y el computador encendido.**

---

## Errores comunes

**"python: command not found"**
```bash
brew install python
```

**"No module named X"**
```bash
pip install -r requirements.txt
```

**"AuthenticationError"**
→ API key mal o sin créditos. Verifica en [console.anthropic.com](https://console.anthropic.com).

**"git: command not found"**
```bash
xcode-select --install
```

---

## Resumen de comandos

| Qué hacer | Comando |
|---|---|
| Aprender tu estilo | `python importer.py config/ejemplo_cliente.json` |
| Generar sin publicar | `python main.py config/ejemplo_cliente.json --solo-generar` |
| Generar y publicar | `python main.py config/ejemplo_cliente.json` |
| Publicación automática diaria | `python scheduler.py config/ejemplo_cliente.json` |
