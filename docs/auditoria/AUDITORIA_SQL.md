# AUDITORÍA SQL — Itinerario

Fecha: 2026-09-01
Metodología: Revisión manual de todos los modelos en app/model/*.py, helpers/reportes_*.py

---

## 1. SQL INJECTION

**Estado: LIMPIO**

Todas las queries usan `%s` parametrizado. Los f-strings en SQL son solo para identificadores de columnas/tablas, nunca para valores de usuario.

La única referencia a f-string en SQL es `tarea_model.py:242` con `esquema_seg` que viene de `DATABASE_CONFIG`, no de input del usuario.

---

## 2. ÍNDICES FALTANTES

| Tabla | Índice faltante | Queries afectadas | Impacto |
|-------|----------------|-------------------|---------|
| `guiones` | `idx_estado` en `estado` | en_vivo_model WHERE estado='en_vivo', guion_model WHERE estado=%s | MEDIO |
| `tareas_asignadas` | `idx_usuario_estado` en `(id_usuario, Estatus)` | tarea_model:144,184,292 | MEDIO |
| `actividad_usuario` | `idx_created_at` en `created_at` | bitacora_model:50 ORDER BY created_at | MEDIO |
| `sincronizaciones` | `idx_guion_fecha` en `(guion_id, fecha_sincronizacion)` | en_vivo_model:40-46 | MEDIO |

---

## 3. N+1 QUERIES (CRÍTICO)

### 3a. `_cargar_nombres_usuario` — bitacora_model.py:16-28

```python
for uid in user_ids:
    user = user_model.obtener_por_id(uid)  # 1 query por usuario
```
- **Impacto:** HIGH — 100 actividades de 10 usuarios = 10 queries extra
- **Fix:** `SELECT id, nombre FROM usuarios WHERE id IN (...)`

### 3b. `_cargar_relaciones` — mantenimiento_model.py:177-198

```python
for m in mantenimientos:
    # 3 queries por mantenimiento
    # + 1 query por item de historial
```
- **Impacto:** HIGH — 50 mantenimientos con 3 historiales = 200 queries
- **Fix:** JOIN único para todas las relaciones

### 3c. `obtener_premios_entregados` — premio_model.py:170-196

```python
for p in premios:
    user = um.obtener_por_id(p['entregado_por'])  # 1 query por premio
```
- **Impacto:** MEDIUM — LIMIT 100 pero peor caso 100 queries

### 3d. Reels consultar — reels_model.py:33-44

```python
for reel in reels:
    reel['videos'] = self._obtener_videos(reel['id'])  # 1 query por reel
```
- **Impacto:** MEDIUM — 50 reels = 50 queries extra

### 3e. `_datos_guiones` — reportes_data.py:210

```python
fechas = model.obtener_fechas(d['id'])  # 1 query por guion en loop
```
- **Impacto:** MEDIUM

---

## 4. SELECT * EXPONE PASSWORD_HASH

| Archivo | Línea | Tabla |
|---------|-------|-------|
| usuario_model.py | 110 | `SELECT * FROM usuarios` |
| auth_model.py | 71 | `SELECT * FROM usuarios WHERE 1=1` |
| auth_model.py | 124 | `SELECT * FROM usuarios WHERE id = %s` |

- **Impacto:** MEDIUM — password_hash se incluye en resultados y puede llegar a templates
- **Fix:** Seleccionar columnas explícitas excluyendo password_hash

---

## 5. TRANSACCIONES FALTANTES

### 5a. reels_model.py:142-143 — DELETE sin transacción

```python
cur.execute("DELETE FROM videos WHERE reel_id = %s", (id,))
cur.execute("DELETE FROM reels WHERE id = %s", (id,))
```
- **Impacto:** HIGH — Si el segundo DELETE falla, videos huérfanos sin padre
- **Fix:** Envolver en `with transaction():`

### 5b. dashboard_visibilidad save — rol_model.py:596-610

```python
cur.execute("DELETE FROM dashboard_visibilidad WHERE rol_id = %s", (rol_id,))
for mk in MODULOS_DASHBOARD:
    cur.execute("INSERT INTO dashboard_visibilidad ...")
```
- **Impacto:** MEDIUM — Si algún INSERT falla, se pierde toda la visibilidad

### 5c. balance_model.py:262-270 — commit manual

```python
db.commit()  # En vez de transaction()
```
- **Impacto:** MEDIUM — Funciona pero bypass del context manager

---

## 6. QUERIES SIN LÍMITE

| Archivo | Línea | Tabla | Impacto |
|---------|-------|-------|---------|
| usuario_model.py | 110 | usuarios | MEDIO |
| bitacora_model.py | 33 | actividad_usuario | HIGH (crece indefinidamente) |
| patrocinador_model.py | 102 | patrocinadores | BAJO |
| reels_model.py | 37 | reels | BAJO |

---

## 7. OPTIMIZACIÓN DE QUERIES

### 7a. reportes_data.py:147-166 — Carga completa para fecha mínima

Carga TODO el dataset en Python solo para encontrar `MIN(fecha)`. Debería ser `SELECT MIN(campo) FROM tabla`.

### 7b. reportes_data.py:707-734 — 9 queries para resumen

Una por módulo. Podrían ser 9 COUNT queries en vez de cargar datasets completos.

### 7c. tarea_model.py:465-473 — Join en Python

Carga tareas y asignadas por separado, luego hace join en Python. Debería ser un JOIN SQL.

---

## 8. PROBLEMA DE DISEÑO

`balance_model.py:16` — `Pago(Database, ValidacionesMixin)` hereda de `Database`. `Pago` es una clase de datos, no un gestor de BD. Expone `get_connection()` como método de cada instancia `Pago`.

---

## RESUMEN PRIORIZADO

| Prioridad | Hallazgo | Fix |
|-----------|---------|-----|
| P0 | N+1 en bitacora (cargar_nombres_usuario) | Batch query |
| P0 | N+1 en mantenimiento (cargar_relaciones) | JOIN único |
| P0 | DELETE sin transacción en reels | transaction() |
| P1 | Índice faltante en guiones.estado | ALTER TABLE ADD INDEX |
| P1 | Índice faltante en tareas_asignadas | Composite index |
| P1 | Índice en actividad_usuario.created_at | ADD INDEX |
| P1 | Sin LIMIT en bitacora | Default LIMIT 500 |
| P1 | password_hash en SELECT * | Columnas explícitas |
| P2 | rango_fechas_defecto carga todo | SELECT MIN |
| P2 | N+1 en reels (videos) | JOIN batch |
| P2 | N+1 en premios (entregado_por) | Batch lookup |
| P3 | Pago hereda Database | Eliminar herencia |
