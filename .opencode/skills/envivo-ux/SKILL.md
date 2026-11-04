---
name: envivo-ux
description: Análisis de la experiencia del operador del show EN VIVO — jerarquía ACTUAL/SIGUIENTE/PENDIENTES, carga cognitiva, errores humanos, doble toque, retroceso y cronómetro. Use when improving UX of app/view/en_vivo/vivo.html, when the user says "ux en vivo", "operador", "jerarquía de estados" or plans interaction changes.
---

# envivo-ux

Analizar la experiencia de QUIEN OPERA EL SHOW durante un juego de béisbol, bajo presión y probablemente con una mano en un teléfono.

## Invariantes que NUNCA se rompen

```text
pendiente → en_curso → completado
```

- El flujo es **estrictamente secuencial**: prohibido saltar elementos (3→5) o avanzar dos a la vez.
- El **retroceso** significa: "marqué por error y aún necesito ejecutarlo" → completado→en_curso, o en_curso→pendiente reactivando el anterior pendiente. Mantener esa lógica exacta.

## Prioridad (en este orden)

1. mobile
2. operación rápida
3. claridad
4. estética

## Qué evaluar siempre

- Jerarquía visual: ACTUAL debe dominar sin ocupar media pantalla; SIGUIENTE visible; PENDIENTES compactos.
- Descubribilidad de la acción principal (doble toque/doble clic) sin convertirla en botón gigante.
- Feedback inmediato de cada acción (guardado, sincronizando, pendiente).
- Carga cognitiva: cero información irrelevante durante el show.
- Errores humanos: doble toque accidental, tocar completado, retroceder sin querer.
- Estadísticas y cronómetro como información secundaria, nunca dominante.

## Reglas generales aplicables

No modificar backend/API/DB/SocketIO server. Mobile-first. Sin PWA, sin modo TV. Doble toque y retroceso intocables como interacciones primarias.
