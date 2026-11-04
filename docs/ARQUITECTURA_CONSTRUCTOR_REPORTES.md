# ARQUITECTURA — Constructor de Reportes Profesionales (Itinerario)

**Fecha:** 2026-08-25 · **Estado:** diseño definitivo. **NO se ha implementado nada.**
**Base:** exclusivamente `docs/AUDITORIA_REPORTES.md` + código real (referencias `archivo:línea` verificadas en la auditoría).
**Garantía de compatibilidad:** la tabla actual, los KPIs actuales, el PDF actual y los filtros progresivos actuales se conservan íntegros. El constructor es una capa nueva al lado, que reutiliza los mismos cimientos.

---

## 0. Principios rectores

1. **El flujo actual es la categoría "Resumen general".** Cada módulo del constructor ofrece como primera opción su análisis actual (OBTENEDORES → preview → PDF) sin tocar una línea. Lo nuevo vive AL LADO.
2. **Todo identificador SQL nace del catálogo o no existe.** El motor nunca interpola un nombre de campo/columna que no venga validado contra el catálogo declarativo (riesgo R1 de la auditoría).
3. **Una sola fuente de verdad por concepto.** Las columnas duplicadas hoy (COLUMNAS_PREVIEW en controller + columns en JS) y las distribuciones dispersas convergen hacia el catálogo. Los flujos viejos NO se reescriben para esto; solo lo nuevo lo consume.
4. **Cero dependencias nuevas.** Gráficos = `reportlab.graphics.charts` (ya instalado); export CSV = `csv` stdlib; frontend sin build step ni librerías (barras CSS/SVG inline si hace falta).
5. **Declarativo donde cambia mucho, imperativo donde importa poco.** Ver §4.

---

## 1. Modelo de navegación (el wizard)

8 pasos; cada uno filtrado por el catálogo; el usuario nunca ve más de una decisión por pantalla:

```
1. MÓDULO          grid existente (MODULOS_DISPONIBLES, controller:18)  [igual a hoy]
2. CATEGORÍA       ¿Qué quieres analizar?      ← catalogo[modulo].categorias
3. DIMENSIÓN       ¿Por qué agrupar?           ← categoria.dimensiones  (opcional:
                                                 "Detalle fila a fila" siempre disponible)
4. FILTROS         panel progresivo EXISTENTE   ← _filtros_<modulo> + whitelist del catálogo
5. MÉTRICAS        checkboxes (con defaults)    ← categoria.metricas
6. VISUALIZACIÓN   opciones válidas según forma de datos ← visualizaciones + reglas de validez
7. COMPARACIÓN     ninguna | período anterior | A vs B (dos valores de la dimensión)
8. RESULTADO       preview dataset genérico + Exportar (PDF/CSV)
```

Reglas de navegación:
- Pasos 3/5/6/7 pueden venir con defaults sensatos ("Siguiente, Siguiente, Resultado" en 3 clicks).
- La categoría **"Resumen general"** salta directamente al flujo actual (pasos 3-7 ocultos): es literalmente el camino de hoy.
- Volver atrás nunca pierde selecciones; cambiar categoría resetea dimensión/métricas (no son compatibles entre categorías).

### Contrato API nuevo (solo 3 endpoints; los existentes intactos)

| Endpoint | Método | Entrada | Salida |
|---|---|---|---|
| `/reportes/catalogo/<modulo>` | GET | — | Config completa del wizard para ese módulo (desde catálogo Python) |
| `/reportes/construir` | POST | `{modulo, categoria, dimension?, tiempo_grano?, metricas[], filtros{}, comparacion?}` | Dataset genérico JSON |
| `/reportes/construir/exportar` | POST | igual + `{formato: pdf\|csv}` | Archivo |

CSRF + `verificar_acceso` blueprint-level, idéntico a hoy.

---

## 2. El dataset genérico (contrato motor ↔ presentación)

Único intercambio entre ejecución y presentación. Todo presentador (tabla HTML, KPI cards, gráfico reportlab, CSV, PDF) consume exactamente esta forma:

```json
{
  "modulo": "contratos",
  "categoria": "ingresos",
  "dimension": {"id": "patrocinador", "label": "Patrocinador"},
  "columnas": [
    {"key": "dimension", "label": "Patrocinador", "tipo": "texto"},
    {"key": "suma_monto", "label": "Monto facturado", "tipo": "moneda"},
    {"key": "num_contratos", "label": "Contratos", "tipo": "entero"}
  ],
  "filas": [
    {"dimension": "Empresa A", "suma_monto": 150000, "num_contratos": 3}
  ],
  "totales": {"suma_monto": 900000, "num_contratos": 21},
  "serie": null,
  "comparacion": {
    "modo": "periodo_anterior",
    "filas_previas": [...],
    "variaciones": {"suma_monto": "+12%"}
  },
  "meta": {"filtros_aplicados": {...}, "generado_en": "...", "limit_alcanzado": false}
}
```

- `serie` ≠ null cuando la dimensión es temporal (`{grano: "mes", puntos: [{periodo:"2026-01", valores:{...}}]}`).
- `tipo` de columna (`moneda/entero/pct/duracion/texto/fecha`) gobierna el formato en TODOS los presentadores — mata el hardcodeo de MONEY_KEYS en JS (GestionReportes.js:334).
- `meta.limit_alcanzado` avisa truncamiento (nunca silencioso, lección de los LIMIT 500).

---

## 3. Los 10 catálogos

### 3.1 Catálogo de MÓDULOS
Evita tocar `MODULOS_DISPONIBLES` (controller:18). Nuevo dict que lo referencia:

```python
MODULO_BUILDER = {
    'contratos': {
        'nombre': 'Contratos', 'icono': 'fa-file-contract',
        'descripcion': 'Contratos de patrocinio: montos, vigencias, niveles.',
        'permiso': None,            # None => hereda reportes.dashboard (hoy)
        'exportaciones': ['pdf', 'csv'],
        'categorias': {...},        # ver 3.2
    },
    ...
}
```

### 3.2 Catálogo de CATEGORÍAS (por módulo)
Cada categoría declara SU esqueleto SQL (FROM+JOIN) — así el motor nunca adivina relaciones. Es la pieza clave que permite que "Ingresos" consulte `pagos JOIN contrato JOIN patrocinadores` mientras "Contratos" consulta solo `contrato JOIN patrocinadores`, con FKs reales verificadas (estadio_db.sql:862-930):

```python
'categorias': {
    'resumen': {'tipo': 'legado'},   # ← ejecuta el flujo ACTUAL tal cual (OBTENEDORES)
    'ingresos': {
        'nombre': 'Ingresos', 'icono': 'fa-money-bill',
        'descripcion': 'Pagos recibidos contra contratos',
        'fuente': 'pagos_por_patrocinador',   # clave de FUENTES_SQL (§5)
        'dimensiones': ['patrocinador', 'tipo_pago', 'mes', 'trimestre'],
        'metricas': ['monto_suma', 'pago_promedio', 'pagos_conteo'],
        'filtros': ['fecha', 'patrocinador', 'tipo_pago', 'monto'],
        'visualizaciones_validas': ['tabla', 'barras_h', 'linea', 'torta'],
        'comparaciones_validas': ['periodo_anterior', 'a_vs_b'],
        'orden_default': '-monto_suma',       # métrica descendente
    },
    ...
}
```

### 3.3 Catálogo de DIMENSIONES (por módulo)
Tres tipos, todos mapeados a columnas reales del esquema:

```python
DIMENSIONES = {
    # entidad: columna etiquetada vía JOIN/FK real
    'patrocinador': {'tipo': 'entidad', 'sql': 'p.nombre_empresa',
                     'join_requerido': 'patrocinadores', 'label': 'Patrocinador'},
    # categórico con mapa de etiquetas (código guardado ≠ label mostrada)
    'nivel': {'tipo': 'mapa', 'sql': 'c.tipo',
              'mapa': {'1': 'Bronce', '2': 'Plata', '3': 'Oro'}, 'label': 'Nivel'},
    # temporal: columna fecha + granularidad elegible en wizard
    'mes': {'tipo': 'temporal', 'sql': 'c.fecha_inicio',
            'granos': ['mes'], 'label': 'Por mes'},
    ...
}
```

### 3.4 Catálogo de FILTROS
NO reinventa los filtros progresivos: los **declara** para cerrar el hueco de whitelist de la auditoría (D4/R5). Cada filtro referencia el handler AJAX existente y define coerción server-side:

```python
FILTROS = {
    'patrocinador': {'handler_ajax': '_filtros_contratos', 'coercion': 'int_opcional',
                     'where': 'c.id_patrocinador = %s'},
    'monto': {'tipo': 'rango', 'sql': 'c.monto_total', 'coercion': 'float'},
    'fecha': {'tipo': 'rango_fecha', 'sql': 'c.fecha_inicio'},   # campo por defecto del módulo
    ...
}
```

Los `_filtros_*` del controller siguen siendo quienes alimentan los selects AJAX (no se duplican opciones).

### 3.5 Catálogo de MÉTRICAS
Agregación + formato. Solo campos numéricos/contables reales (auditoría §15):

```python
METRICAS = {
    'monto_suma':   {'agg': 'SUM', 'sql': 'c.monto_total', 'formato': 'moneda',
                     'label': 'Monto total'},
    'monto_promedio': {'agg': 'AVG', 'sql': 'c.monto_total', 'formato': 'moneda'},
    'contratos_conteo': {'agg': 'COUNT', 'sql': '*', 'formato': 'entero'},
    'dias_promedio': {'agg': 'AVG', 'sql': 'DATEDIFF(COALESCE(m.fecha_salida, CURDATE()), m.fecha_ingreso)',
                      'formato': 'decimal_1', 'label': 'Días prom. en taller'},
}
```

### 3.6 Catálogo de AGRUPACIONES
Comportamientos sobre la dimensión (no nuevos datos):

| Agrupación | Efecto |
|---|---|
| `todos` | Una fila total (sin GROUP BY de dimensión) |
| `por_valor` | Fila por valor de dimensión |
| `top_n` (n=5..20) | Top N + fila "Otros" consolidada |
| `temporal` | Buckets día/semana/mes/año vía DATE_FORMAT (MySQL), con rango continuo (meses vacíos incluidos) |
| `detalle` | Sin agregación: filas crudas paginadas (usa SELECT directo, es el modo "tabla") |

### 3.7 Catálogo de VISUALIZACIONES

| ID | Motor | Validez automática |
|---|---|---|
| `tabla` | HTML actual + PDF tabla | siempre |
| `kpi_cards` | grid existente kpiCards | solo agrupación `todos` |
| `torta` | `reportlab.graphics Pie` (PDF) / leyenda barras CSS (preview) | ≤8 valores de dimensión |
| `barras_h` / `barras_v` | HorizontalBarChart/VerticalBarChart / divs CSS | 1-2 métricas |
| `linea` | LineChart (PDF) / SVG polilínea inline (preview) | solo dimensión temporal |

El preview usa representación CSS/SVG mínima (sin librerías); el PDF usa reportlab nativo. Regla de la skill reportes-pdf respetada.

### 3.8 Catálogo de COMPARACIONES

| Modo | Implementación |
|---|---|
| `ninguna` | default |
| `periodo_anterior` | re-ejecuta con ventana desplazada — MISMA lógica ya probada del controller L606-618, ahora sobre el motor nuevo |
| `a_vs_b` | dos valores de la misma dimensión como WHERE adicional (ej. Bronce vs Oro); solo si `comparaciones_validas` lo incluye |

### 3.9 Configuración de REPORTES (plantillas guardadas)

- Un reporte construido = tupla declarativa serializable: `{modulo, categoria, dimension, tiempo_grano, metricas, filtros, visualizacion, comparacion}`.
- Persistencia: **tabla nueva `reportes_plantillas`** (esquema `seguridad`, junto a `reportes_generados`: usuario_id, nombre, config JSON, creado_en). ⚠️ Requiere migración de BD autorizada por el usuario (regla AGENTS.md). Alternativa cero-migración mientras tanto: guardar como JSON en `reportes_generados.filtros` con marcador `tipo='plantilla'`.
- "Aplicar plantilla" = precargar el wizard en ese punto.
- Los PDF generados siguen registrándose en `reportes_generados` igual que hoy (base_report.py:368 intacto).

### 3.10 Catálogo de EXPORTACIONES
`pdf` (existe) · `csv` (stdlib, fase 2 del constructor) · `excel` explícitamente diferido (requeriría openpyxl — solo si hay necesidad real).

---

## 4. ¿Configuración declarativa por módulo? — SÍ, pero en backend

**Decisión:** sí, configuración declarativa tipo `MODULE_REPORT_CONFIG`, viviendo en **Python** (`app/helpers/reportes_catalogo.py` — nuevo), NO en JavaScript.

Razones (derivadas del código real):
1. **Seguridad:** los whitelists de identificadores SQL deben vivir del lado servidor (auditoría R1). Un catálogo JS es sugerencia de UI; uno Python es frontera de validez.
2. **Una sola fuente:** hoy las columnas existen duplicadas (controller COLUMNAS_PREVIEW L390 vs JS columns). El backend sirve el catálogo por `/reportes/catalogo/<modulo>` y el frontend deja de hardcodear estructura — solo renderiza.
3. **Coherencia con lo existente:** `OBTENEDORES` (data.py:734) y `FILTROS_HANDLERS` (controller:359) YA son registros declarativos-en-Python; el catálogo extiende ese patrón en vez de inventar otro.
4. **Testeable:** tests de consistencia introspectan el catálogo contra `*_test` (toda métrica/dimensión existe como columna real) — imposible con config JS.

Lo que permanece **imperativo**: el motor SQL parametrizado (la construcción de la query es lógica, no datos) y los `_filtros_*` AJAX existentes (se consumen, no se duplican).

`MODULE_CONFIG` de GestionReportes.js **se mantiene** para los flujos legados ("Resumen general"); el wizard nuevo recibe su configuración servida, no escrita a mano.

### Esquema completo de la entrada por módulo

```python
REPORT_BUILDER_CONFIG = {
    '<modulo>': {
        'nombre': str, 'icono': str, 'descripcion': str,
        'permiso': str | None,
        'exportaciones': ['pdf', 'csv'],
        'campo_fecha_default': str,             # p.ej. 'c.fecha_inicio'
        'categorias': {
            '<cat>': {
                'nombre', 'descripcion', 'icono',
                'tipo': 'legado' | 'constructor',
                'fuente': '<clave de FUENTES_SQL>',
                'dimensiones': [...], 'metricas': [...], 'filtros': [...],
                'agrupaciones': [...], 'visualizaciones_validas': [...],
                'comparaciones_validas': [...], 'orden_default': str,
                'metricas_default': [...],       # preseleccionadas en el wizard
            }
        },
    },
}

FUENTES_SQL = {   # esqueletos FROM/JOIN — SOLO FKs reales verificadas
    'contratos': "FROM contrato c JOIN patrocinadores p ON c.id_patrocinador = p.id_patrocinador",
    'pagos_por_patrocinador': "FROM pagos pg JOIN contrato c ON pg.id_contrato = c.id_contrato "
                              "JOIN patrocinadores p ON c.id_patrocinador = p.id_patrocinador",
    'recursos': "FROM recursos r LEFT JOIN tipo_recurso t ON r.tipo_id = t.id "
                "LEFT JOIN estado_recurso e ON r.estado_id = e.id",
    ...
    # WHERE fijo de soft-delete por tabla va aparte (SOFT_DELETE = {'guiones': 'status=1', ...})
}
```

Campos exigidos por el usuario (nombre/descripción/icono/categorías/dimensiones/filtros/métricas/agrupaciones/visualizaciones/columnas/permisos/exportaciones): todos cubiertos — `columnas` deriva de dimensión+métricas elegidas (dataset genérico), por eso no se declara estática.

**Extensibilidad:** añadir un análisis nuevo = añadir una entrada al dict (categoría/dimensión/métrica). El motor, wizard, PDF y CSV no cambian.

---

## 5. Motor de ejecución (backend, imperativo)

```
POST /reportes/construir
 1. validar modulo ∈ MODULO_BUILDER, categoria ∈ config, tipo != 'legado'
 2. validar dimension/metricas/filtros ⊆ categoria (catálogo = única fuente de identificadores)
 3. armar SQL:
      SELECT <dim_sql [AS dim]> , <AGG(sql) AS metrica_k>...
      <FUENTES_SQL[categoria.fuente]>
      WHERE <soft_delete fijo> AND <filtros whitelisteados con %s>
      GROUP BY <dim | bucket temporal>
      ORDER BY <orden_default | elección> LIMIT <500 duro de salvaguarda>
 4. ejecutar (PyMySQL DictCursor — sin ORM, convención AGENTS.md)
 5. completar buckets temporales vacíos; fila "Otros" si top_n
 6. totales = SUM de la serie (o segunda query sin GROUP BY si agrupación=todos)
 7. comparación: re-ejecutar con ventana desplazada / filtro A/B
 8. devolver dataset genérico (+ meta.limit_alcanzado, filtros_aplicados)
```

Reglas duras: parámetros de VALOR siempre `%s`; identificadores solo desde catálogo; `LIMIT` de salvaguarda visible en `meta`; timeout consciente del worker único eventlet (consultas acotadas por fechas obligatorias en series grandes).

**Compatibilidad legado:** `categoria.tipo == 'legado'` desvía a `_obtener_datos()` actual — mismo código, cero riesgo.

---

## 6. Motor de presentación

Un solo consumidor abstracto (dataset genérico) con 4 salidas:

| Salida | Implementación |
|---|---|
| Preview HTML | stepper wizard reutilizando el panel/kpiGrid/tabla actuales de dashboard.html; barras/línea en CSS/SVG inline |
| PDF | NUEVO `ConstructorReport(BaseReportGenerator)` — consume dataset; usa `_seccion_distribucion/_top_destacados` existentes para tortas/barras + charts reportlab para líneas; respeta contrato `opciones` de la skill (orientación/columnas/agrupar) |
| CSV | `csv` stdlib desde `columnas+filas` |
| Plantilla | serialización del request (§3.9) |

El PDF actual (`<Modulo>Report`) sigue usándose SIN CAMBIOS para las categorías legadas.

---

## 7. Reparto backend / frontend / SQL / config / PDF

| Capa | Vive en | Contenido |
|---|---|---|
| Config (declarativa) | `app/helpers/reportes_catalogo.py` (nuevo) | MODULO_BUILDER, categorías, dimensiones, filtros, métricas, FUENTES_SQL, soft-deletes |
| Backend | `reportes_controller.py` (ampliar, no romper) | 3 endpoints nuevos + despacho legado/constructor |
| Ejecución | `app/helpers/reportes_constructor.py` (nuevo) | armado SQL whitelistado, buckets temporales, comparaciones, límites |
| SQL | MySQL | GROUP BY/DATE_FORMAT/DATEDIFF; índices de fecha recomendados (⚠️ migración BD requiere autorización: `pagos.fecha_pago`, `actividad_usuario.created_at`, `mantenimientos.fecha_ingreso`, `contrato.fecha_inicio`) |
| Frontend | `GestionReportes.js` + `dashboard.html` (ampliar) | stepper, render desde catálogo servido, preview dataset; MODULE_CONFIG intacto para legado |
| PDF | `app/helpers/generators/constructor_report.py` (nuevo) + base_report.py (hook `_secciones_extra` ya previsto en auditoría D5) | dataset → story reportlab |

---

## 8. Matriz funcional por módulo (categorías nuevas a declarar)

Solo categorías CONSTRUCTOR (todas tienen además "Resumen general" legado). Dimensiones/métricas tomadas exclusivamente de campos verificados (auditoría §14-15):

| Módulo | Categoría | Dimensiones | Métricas | Series |
|---|---|---|---|---|
| contratos | Ingresos (pagos) | patrocinador, tipo_pago, mes | SUM/AVG monto, COUNT | ✓ fecha_pago |
| contratos | Vencimientos | patrocinador, estatus | COUNT, días restantes AVG | ✗ |
| contratos | Rendimiento (por nivel) | nivel(Bronce/Plata/Oro) | SUM monto, COUNT, % cartera | ✗ |
| balance* | Cobranza | patrocinador(vía contrato), tipo_pago, mes | SUM/AVG/COUNT monto | ✓★ |
| tareas | Carga laboral | usuario asignado, estado | COUNT, % completadas | ⚠️ sin fecha cierre |
| guiones | Producción | encargado, estado, mes | COUNT elementos, SUM duración | ✓ creado_en |
| inventario | Valorización | tipo, estado | SUM/AVG costo, COUNT | ✗ |
| premios | Entregas | patrocinador, estado, mes | SUM cantidades, tasa entrega | ✓ fecha_entrega |
| mantenimiento | Taller | recurso, estado, mes ingreso | dias_en_taller AVG/MAX, COUNT | ✓ |
| usuarios | Planta | departamento, rol | COUNT activos/inactivos | ✓ altas mensuales |
| reels | Contenido | patrocinador, mes | COUNT videos, SUM duración | ✓ creado_en |
| bitácora | Actividad | usuario, acción, módulo, día | COUNT | ✓★ diaria |
| patrocinadores | Cartera | tipo_contrato, estado | COUNT | ✗ (sin fecha propia) |

\* *balance hereda el fix previo de su LIMIT 500/startswith (auditoría F0/D9) antes de entrar al constructor.*

---

## 9. Flujo ejemplo end-to-end (caso pedido, con objetos reales del diseño)

```
GET /reportes/catalogo/contratos
→ {categorias:[resumen(legado), ingresos, vencimientos, rendimiento], ...}

Usuario: "Ingresos" → GET implícito: wizard muestra dimensiones=['patrocinador','tipo_pago','mes']
Usuario: "Por patrocinador" → filtros (panel _filtros_contratos actual) → métricas
  [✓ monto_suma (default)] [ ] pago_promedio [✓ pagos_conteo]
→ Visualización: barras_h → Comparación: período anterior
→ POST /reportes/construir
{modulo:'contratos', categoria:'ingresos', dimension:'patrocinador',
 metricas:['monto_suma','pagos_conteo'], filtros:{fecha_inicio:'2026-01-01', fecha_fin:'2026-06-30'},
 comparacion:'periodo_anterior'}

SQL generado (identificadores 100% del catálogo):
SELECT p.nombre_empresa AS dim, SUM(c.monto_total)... -- ¡NO!: fuente pagos →
SELECT p.nombre_empresa AS dim, SUM(pg.monto) AS monto_suma, COUNT(*) AS pagos_conteo
FROM pagos pg JOIN contrato c ON pg.id_contrato=c.id_contrato
JOIN patrocinadores p ON c.id_patrocinador=p.id_patrocinador
WHERE pg.fecha_pago BETWEEN %s AND %s GROUP BY dim ORDER BY monto_suma DESC LIMIT 500

→ dataset genérico → preview (barras CSS + tabla) → exportar PDF (ConstructorReport
  con torta top-5 + comparativa vs H2-2025) o CSV.
```

---

## 10. Decisiones de diseño explícitas

| Decisión | Elección | Por qué |
|---|---|---|
| ¿Config declarativa? | Sí, Python-side | Seguridad (whitelist SQL), una sola fuente, patrón OBTENEDORES ya existente, testeable contra *_test |
| ¿Catálogo también en JS? | No — se SIRVE por endpoint | Evita tercera copia de columnas (deuda D6 de la auditoría) |
| Wizard propio o ampliar panel? | Ampliar dashboard.html con stepper | ~30 usuarios no analistas; reusa UI conocida (riesgo R6) |
| Gráficos en preview | CSS/SVG mínimo | Sin deps ni build; charts ricos solo en PDF (reportlab nativo) |
| Categorías con esqueleto SQL propio | Sí (FUENTES_SQL) | "Ingresos" y "Contratos" tienen FROM distintos; el motor no adivina relaciones |
| Soft-delete | Constante por tabla en el catálogo | Flags heterogéneos documentados (status/eliminado/estatus/estado) — error clásico ya ocurrido |
| Plantillas | Tabla nueva (requiere OK de migración) o marcador en reportes_generados | Decisión del usuario antes de F-final |
| Excel | Diferido | openpyxl = dep nueva; CSV cubre el 90% |

## 11. Qué NO cambia (lista dura)

`MODULOS_DISPONIBLES` · rutas `/filtros/<modulo>`·`/preview`·`/generar`·`/descargar`·`/eliminar` · `OBTENEDORES` y sus firmas · `MODULE_CONFIG` (legado) · `_filtros_*` handlers · `BaseReportGenerator.generate()/save()` · los 12 `<Modulo>Report` · tabla/KPIs/PDF/filtros progresivos visibles hoy · permisos y CSRF · `ReporteModel`.

---

*Siguiente paso cuando apruebes: F0 de blindaje de la auditoría (whitelists de filtros, orden numérico, LIMIT 500) y luego el catálogo con piloto bitácora+contratos.*
