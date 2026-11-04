---
name: envivo-offline
description: Experiencia del módulo EN VIVO al perder conexión — estado local, cola de cambios pendientes, reintento, reconexión y reconciliación; indicadores CONECTADO/RECONECTANDO/SIN CONEXIÓN/CAMBIOS PENDIENTES. Solo frontend. Use when implementing or reviewing the offline mode of vivo.html, retry queues, or when the user says "offline", "sin conexión", "cola", "reintento".
---

# envivo-offline

El estadio pierde WiFi. La UI NO se congela y NINGUNA acción se pierde en silencio.

## Modelo (solo frontend)

```text
estado local (mapa id→estado)
   ↓ acción del operador
cola de cambios pendientes
   ↓ flush con reintento
POST /en-vivo/api/sincronizar/<id>
   ↓ reconexión
GET /en-vivo/api/estado-actual/<id>  →  reconciliar
```

1. Toda acción actualiza el estado local YA y entra a la cola si no hay red.
2. Reintento periódico suave + flush inmediato al reconectar SocketIO.
3. Al reconectar: consultar estado real del servidor, reconciliar y recién ahí vaciar la cola.
4. Si el servidor confirma un estado distinto para un elemento con cambios pendientes, prevalece lo confirmado por el servidor; mostrar aviso.

## Indicador visible y persistente (no modal bloqueante)

```text
● CONECTADO   ↻ RECONECTANDO...   ● SIN CONEXIÓN   ⚠ CAMBIOS PENDIENTES: n
```

Nunca perder silenciosamente una acción. Toast pequeño "Otro operador actualizó el guion" ante cambio remoto no originado localmente.

## Límites duros

NO modificar backend. NO modificar API. Sin PWA, sin IndexedDB/Service Workers: memoria de la página es suficiente para cortes temporales.
