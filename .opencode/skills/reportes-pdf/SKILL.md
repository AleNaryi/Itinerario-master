---
name: reportes-pdf
description: Motor de reportes PDF personalizables de Itinerario (reportlab). Use when improving or extending PDF generation, adding customization options (orientation, columns, charts, grouping, totals), touching base_report.py, *_report.py generators, GestionReportes.js or the /reportes/generar route. Trigger words: "reporte", "PDF", "generador", "personalizar reporte".
---

# Reportes PDF personalizables — Itinerario

Estado actual: PDF rígido e idéntico para todos los casos — cabecera fija → tarjetas KPI en grilla fija → tabla completa → distribuciones → pie (`BaseReportGenerator.generate` en `app/helpers/generators/base_report.py`). Objetivo: que el cliente configure el PDF al generarlo.

## Arquitectura del flujo (no romperla)

```
GestionReportes.js (MODULE_CONFIG) → POST /reportes/generar
  → reportes_controller.generar() (línea ~1132)
  → _obtener_datos(modulo, filtros) → (datos, kpis)
  → <Modulo>Report(current_user).generate(datos, filtros, kpis)  ← PUNTO ÚNICO DE EXTENSIÓN
  → .save() → static/reportes/YYYY/MM + ReporteModel (bitácora)
```

La personalización se hace ampliando **solo** `base_report.py`; los 12 generadores heredan gratis. Contexto adicional de filtros/KPIs pendientes por módulo: `.opencode/reportes-context.md`.

## Contrato del dict `opciones`

`generate(datos, filtros=None, kpis=None, opciones=None)` — todo opcional, defaults = comportamiento actual:

| Clave | Valores | Efecto |
|---|---|---|
| `orientacion` | `'vertical'` (default) / `'horizontal'` | `landscape(letter)`; columnas anchas lo necesitan |
| `titulo` / `subtitulo` | string | Reemplazan/complementan `self.TITULO` |
| `periodo` | string | Texto legible del rango bajo el título ("Enero – Marzo 2026") |
| `columnas` | lista de keys de `COLUMNAS` | Subconjunto visible, en el orden pedido |
| `incluir` | dict de bools: `kpis`, `tabla`, `distribuciones`, `graficos` | Secciones on/off |
| `agrupar_por` | key de columna | Agrupa filas + fila de subtotal por grupo |
| `top_n` | entero > 0 | Primeros N tras ordenar |
| `logo` | ruta relativa validada | Logo en cabecera (default: logo institucional si existe) |

## Receta para agregar una opción (end-to-end)

1. **Backend** (`base_report.py`): aceptar `opciones=None`, normalizar con `opciones = opciones or {}`, aplicar con `.get()` y defaults. Si la opción altera layout (orientación), configurarla ANTES de crear el `SimpleDocTemplate`.
2. **Controlador** (`generar()`): leer de `request.form` (JSON en campo `opciones` o campos sueltos `opt_*`) y **validar por whitelist** antes de pasarla. Nunca confiar en el cliente: claves desconocidas se descartan, tipos se coerzan (`top_n = int(top_n)` con try).
3. **Frontend**: panel "Opciones del PDF" en `dashboard.html` + manejo en `GestionReportes.js` (agregar los campos al POST). Opciones globales (orientación, logo, incluir/*) fuera de `MODULE_CONFIG`; las específicas por módulo dentro.
4. **Verificar**: PDF generado empieza con `%PDF-`, abre sin error, y SIN opciones produce byte-a-byte el mismo resultado de siempre.

## Gráficos: nativo de reportlab, cero dependencias nuevas

Usar `reportlab.graphics.charts` (ya instalado con reportlab): `Pie` para distribuciones, `VerticalBarChart`/`HorizontalBarChart` para comparativas. Envolver en `Drawing` y agregar al story donde hoy va `_seccion_distribucion`. Regla: **prohibido agregar matplotlib u otra librería** para esto.

```python
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
```

## Orden de construcción recomendado

1. Firma `opciones` + whitelist en controlador (infraestructura).
2. `orientacion` + `titulo`/`subtitulo`/`periodo` (baratos, alto impacto visual).
3. `incluir.*` (secciones on/off).
4. `columnas` (subconjunto desde `COLUMNAS`).
5. `top_n` + `agrupar_por` con subtotales.
6. Gráficos torta/barras alimentados por las distribuciones que ya calculan los KPIs.
7. Logo/portada opcional.

## Checklist

- [ ] ¿Sin opciones el PDF queda igual que antes?
- [ ] ¿`opciones` pasó por whitelist server-side?
- [ ] ¿Gráficos con reportlab nativo (sin deps nuevas)?
- [ ] ¿`save()` sigue registrando en bitácora igual?
