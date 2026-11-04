---
name: envivo-performance
description: Rendimiento del módulo EN VIVO — reflows, repaints, timers únicos, listeners limpios y actualización parcial del DOM para ~30 espectadores simultáneos. Use when optimizing vivo.html, adding timers/counters, or when the user says "performance", "lento", "memory leak", "reflow".
---

# envivo-performance

Objetivo: interfaz fluida con ~30 usuarios conectados y un show corriendo durante horas.

## Revisar siempre

- Reflows/repaints: agrupar escrituras DOM; animar solo `transform`/`opacity`.
- DOM: actualizar SOLO los nodos afectados por cada evento socket; jamás reconstruir la lista.
- Timers: UN único intervalo activo para el cronómetro; al cambiar de elemento `clearInterval(anterior)` antes de iniciar el nuevo. NUNCA timers duplicados.
- El cronómetro modifica únicamente el nodo del elemento actual (un textContent), jamás re-render global cada segundo.
- Listeners e intervals: registrar una sola vez; limpiar en reconnect/re-render parciales.
- Memoria: sin referencias circulares ni nodos huérfanos acumulados.
- Frecuencia: contadores solo cuando cambian; nada de trabajo por tick salvo el timer actual.

## Antipatrones que esta skill rechaza

`renderEverything()` ante cada socket · setInterval por elemento · listeners añadidos dentro de handlers · animaciones CSS costosas en listas largas (box-shadow animado masivo).
