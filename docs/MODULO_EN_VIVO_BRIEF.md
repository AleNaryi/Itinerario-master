# BRIEF TÉCNICO — Módulo "Guion en Vivo" (en_vivo)

> Documento de traspaso para una IA/developer externa. Objetivo: rediseñar la vista
> del show EN VIVO y mejorar su UX de forma radical. Todo lo descrito aquí fue
> verificado contra el código real del proyecto (no inventado).

## 1. Qué es (contexto de negocio)

El Estadio Antonio Herrera Gutiérrez produce **shows en vivo** durante los juegos de
béisbol (animación, música, promos, dinámicas con público). Un **guion** es la lista
ordenada de esos momentos ("elementos"). Este módulo es la **pantalla de operación
durante el juego**: un operador va marcando cada elemento conforme ocurre y todos
los usuarios conectados ven el avance en tiempo real.

Estados posibles de un guion: `borrador → publicado → en_vivo → finalizado`.
Solo puede haber **UN** guion `en_vivo` a la vez en todo el sistema (restricción dura).

Ciclo de vida de un elemento durante el show:
```
pendiente → en_curso → completado
     ↑          │  (↩ retroceder devuelve al estado anterior)
     └──────────┘   (también existe estado 'reiniciado' válido en backend)
```

## 2. Archivos involucrados

| Archivo | Rol |
|---|---|
| `app/controller/en_vivo_controller.py` | Rutas Flask (blueprint `en_vivo`, prefijo `/en-vivo`) |
| `app/model/en_vivo_model.py` | `EnVivoModel` (iniciar/finalizar/elementos/sincronizar) + `SincronizacionModel` (log) |
| `app/model/guion_model.py` | `GuionModel.obtener_por_id`, `ElementoGuionModel` |
| `app/view/en_vivo/index.html` | Lista de guiones disponibles + botones iniciar/ver/finalizar/reiniciar (~142 líneas) |
| `app/view/en_vivo/vivo.html` | **LA VISTA A REDISEÑAR** — pantalla de operación (~611 líneas, CSS+JS embebidos, vanilla) |
| `app/view/en_vivo/log.html` | Log de sincronizaciones por guion (~64 líneas) |
| `app/__init__.py` | Handlers globales de SocketIO (`connect`, `registrar_usuario`, `cambio_pagina`, `disconnect`) |

No hay JS/CSS externo del módulo en `static/` para esta vista: todo está inline en `vivo.html`.

## 3. Modelo de datos real (columnas verificadas)

- `guiones`: `id, nombre, estado, creado_en, modificado_en, tiempo_inning, grupo_id, status`
- `elementos_guion`: `id, guion_id, fecha_id, tipo('pregame'|'game'), hora(TIME),
  inning(1-9), medio_inning, contenido, duracion_estimada(SEGUNDOS), encargado,
  orden, creado_en, estado(pendiente|en_curso|completado|reiniciado)`
- `guion_fechas`: fechas de ejecución del guion (`guion_id, fecha`)
- `sincronizaciones`: log de auditoría (`guion_id, usuario_id, tipo, descripcion, timestamps`)
  — se registra UNA fila por cada cambio de estado.

Ordenamiento al renderizar: pregame `ORDER BY hora`; game `ORDER BY inning, medio_inning`.

## 4. Endpoints

| Ruta | Método | Qué hace |
|---|---|---|
| `/en-vivo/` | GET | Lista guiones publicados/en_vivo/finalizados con acciones |
| `/en-vivo/<guion_id>` | GET | **Vista de operación** (rechaza si el guion no está `en_vivo`) |
| `/en-vivo/iniciar/<guion_id>` | GET | Marca `en_vivo`; resetea todos los elementos a `pendiente` y pone el primero `en_curso`. Falla si ya hay otro en vivo |
| `/en-vivo/finalizar/<guion_id>` | GET | Marca `finalizado` y resetea elementos a `pendiente` |
| `/en-vivo/api/sincronizar/<guion_id>` | POST JSON `{estados:[{id,estado}]}` | Valida estados contra whitelist server-side, persiste, registra log/bitácora y **emite socket** `actualizar_estados` |
| `/en-vivo/api/estado-actual/<guion_id>` | GET | Estados actuales de todos los elementos (usado al conectar/reconectar) |
| `/en-vivo/log/<guion_id>` | GET | Log filtrable de sincronizaciones |
| `/en-vivo/api/guiones-por-fecha` | POST JSON `{fecha}` | Guiones de una fecha (auxiliar) |

Toda escritura pasa por `verificar_acceso(EN_VIVO)` (before_request del blueprint) y registra bitácora vía `registrar_bitacora('envivo', ...)`.

## 5. Tiempo real (SocketIO — YA autenticado por sesión Flask-Login)

- Cliente emite `registrar_usuario` con `{pagina, en_vivo_id}` (la identidad la toma el servidor de la sesión, ignorando lo que envíe el cliente).
- Servidor emite `usuarios_actualizados` (presencia global; el cliente filtra `u.en_vivo_id === guionId` para el contador "**N viendo**").
- Al sincronizar, servidor emite `actualizar_estados` `{guion_id, estados:[{id,estado}]}` → todos los clientes pintan el nuevo estado.
- En `reconnect`: re-registrar y llamar `GET /api/estado-actual` para resync.
- Deuda conocida: presencia en dict en memoria (solo válido con 1 worker).

## 6. La vista actual `vivo.html` (qué ve y qué hace el operador)

**Layout**: header sticky (volver, nombre+fechas, pills "N listos / N restantes / N viendo",
toggle tema, botón Finalizar con confirmación SweetAlert, badge ● EN VIVO pulsante) +
sección "Pre-Game" (borde ámbar) y sección "Game" (borde cyan), cada una con filas-grid
`160px 1fr 80px 120px`: hora | contenido | duración | encargado(+botón ↩ retroceder).

**Estados visuales por fila**: normal (pendiente), verde brillante con glow (`en_curso`),
atenuado 35% opacidad (`completado`). Colores vía CSS custom properties con tema
dark/light conmutables (persistido en `localStorage['vivo-theme']`).

**Interacciones**:
- **Doble clic** en un elemento `en_curso` → se completa y el siguiente `pendiente` pasa a `en_curso` (única forma de avanzar; hay un hint textual arriba).
- Botón **↩** por fila → retrocede un paso (completado→en_curso; en_curso→pendiente y reactiva el anterior pendiente).
- **Doble-tap** equivalente en móvil.
- Los cambios se envían por fetch a `/api/sincronizar`; en fallo de red revierte localmente y muestra SweetAlert. Si el servidor responde error de permisos, recarga la página.
- Contadores listos/restantes recalculados en `actualizarColores()` tras cada cambio.

## 7. Restricciones técnicas (NO negociables al rediseñar)

1. **Stack sin build**: Jinja2 + Bootstrap 5 + SweetAlert2 + FontAwesome + socket.io, todo por CDN. Vanilla JS. Puedes mantener eso o introducir un bundle, pero hoy no existe pipeline de compilación.
2. **Contrato del API**: `POST /api/sincronizar/{id}` espera `{estados:[{id, estado}]}`, acepta solo `{'pendiente','en_curso','completado','reiniciado',None}`; respuesta `{'success': true}`. Cambiarlo requiere tocar también controlador y modelo.
3. **Permisos y bitácora**: cualquier ruta nueva dentro del blueprint hereda `verificar_acceso(EN_VIVO)`; las escrituras deben seguir registrando sincronización + bitácora.
4. **Un solo guion en vivo**: nunca permitir iniciar otro mientras haya uno activo.
5. **Reset al iniciar/finalizar**: los elementos vuelven a `pendiente` (comportamiento intencional para re-usar guiones).
6. `hora` es TIME de MySQL → llega como `timedelta` de Python (ver `_fmt12`); `duracion_estimada` está en SEGUNDOS.
7. CSRF: los fetch POST JSON del módulo hoy no envían token (JSON con Content-Type application/json está exento del CSRF de Flask-WTF); si cambias a form-data, incluye `X-CSRFToken`.

## 8. Debilidades UX detectadas (oportunidades del redesign)

1. **Descubribilidad nula**: la acción principal (avanzar el show) es un doble clic oculto explicado solo con un hint de texto. Un operador bajo presión necesita un botón grande e inequívoco.
2. **Sin foco en lo urgente**: todas las filas pesan igual visualmente. Falta modo "solo actual + siguientes 2-3", auto-scroll al elemento en curso y barra de progreso global %.
3. **Sin dimensión temporal real**: no hay reloj "ahora" vs hora programada, ni cuenta atrás/regresiva de la duración estimada del elemento en curso, ni alerta de sobretiempo. La hora mostrada es un rango estático calculado server-side.
4. **Feedback de guardado invisible**: el fetch es fire-and-forget; no sabes si quedó guardado hasta que otro cliente lo refleja. Falta indicador de sincronización (spinner/check/toast sutil).
5. **Sin indicador de conexión**: si SocketIO cae, la vista se queda muda. Necesita badge online/offline + cola de reintentos.
6. **Conflictos entre operadores**: último write gana; no hay bloqueo ni aviso de divergencia. Al menos mostrar toast "otro usuario actualizó este elemento".
7. **Teclado inexistente**: espacio/completa, flechas/navega serían oro para operación con una mano. También accesibilidad (roles ARIA, focus visible, contraste del tema claro).
8. **Finalizar peligroso**: desde index usa `confirm()` nativo; desde vivo.html hay SweetAlert pero no advierte cuántos elementos quedan sin completar.
9. **Log lejano**: ver el historial obliga a salir de la vista; cabe un drawer/panel lateral.
10. **Encargados sin filtro**: en shows grandes, poder filtrar "solo mis elementos" ayudaría a cada persona.
11. **Contexto perdido en móvil**: la grid esconde duración y apila mal; el redo sería mobile-first (el operador está caminando por el estadio con tablet/teléfono).
12. Extras de alto impacto: modo pantalla completa/TV, sonido o vibración háptica al completar, animación de transición entre elementos, confeti/celebración al llegar al 100%, deep-link compartible solo-lectura para pantallas de backstage.

## 9. Cómo verificar cambios

```bash
venv/bin/python run.py   # http://localhost:5001
# Login → permiso EN_VIVO requerido (usuario Superadmin tiene todo)
# 1. /guiones → crear/publicar un guion con elementos pregame y game
# 2. /en-vivo/ → Iniciar
# 3. Abrir /en-vivo/<id> en 2 navegadores → doble clic en uno → el otro debe reflejarlo al instante
# 4. Probar retroceder (↩), finalizar, reconexión de red
```

Tests existentes relacionados: `tests/test_auth.py` (sesión), suite general `venv/bin/pytest -q`
(corre contra BDs `*_test`). No hay tests específicos de en_vivo aún — si agregas endpoints,
agréalos siguiendo el patrón de `tests/test_reportes_filtros.py`.
