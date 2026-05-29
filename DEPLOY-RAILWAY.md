# Deploy en Railway — Corre 24/7 sin tu computador

## Paso 1 — Crear cuenta en Railway

Ve a [railway.app](https://railway.app) y crea una cuenta con tu GitHub.

---

## Paso 2 — Crear nuevo proyecto

1. Click en **New Project**
2. Selecciona **Deploy from GitHub repo**
3. Elige `linkedin-agent`
4. Railway detecta el Dockerfile automáticamente

---

## Paso 3 — Configurar variables de entorno

En Railway, ve a tu proyecto → **Variables** y agrega:

```
ANTHROPIC_API_KEY     = sk-ant-...
LINKEDIN_EMAIL        = tu@email.com
LINKEDIN_PASSWORD     = tu_contraseña
TELEGRAM_TOKEN        = 7123456789:AAFxxx...
TELEGRAM_CHAT_ID      = 123456789
```

---

## Paso 4 — Agregar volumen persistente

Para que la memoria del agente y la sesión de LinkedIn no se borren en cada deploy:

1. Ve a tu proyecto → **Add Volume**
2. Monta el volumen en `/app/data`
3. En `config/ejemplo_cliente.json` cambia las rutas:
   - `"foto_path": "/app/data/foto.jpg"`

Sube tu foto al volumen desde la terminal de Railway.

---

## Paso 5 — Deploy

Railway hace el deploy automáticamente al detectar cambios en GitHub.

Para forzar un deploy manual: **Deploy** → **Redeploy**.

---

## Paso 6 — Ver logs

En Railway → tu proyecto → **Logs**. Ahí ves todo lo que hace el agente en tiempo real.

---

## Flujo en producción

```
08:00am (hora configurada)
  → Agente genera post + carrusel
  → Te manda el texto por Telegram
  → Respondes SI o NO desde el cel
  → SI: publica en LinkedIn automáticamente
  → NO: descarta y hasta mañana
```

---

## Costo estimado

Railway tiene plan gratuito con $5 de crédito mensual.
El agente consume muy poco — debería correr gratis o casi gratis.
