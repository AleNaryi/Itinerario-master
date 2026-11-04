# AUDITORÍA DE PERFORMANCE — Itinerario

Fecha: 2026-09-01
Metodología: Análisis estático de código, revisión de queries, assets

---

## BACKEND

### N+1 Queries (CRÍTICO)

| Ubicación | Queries por item | Impacto |
|-----------|-----------------|---------|
| bitacora_model._cargar_nombres_usuario | 1 SELECT por usuario distinto | HIGH |
| mantenimiento_model._cargar_relaciones | 3+ SELECT por mantenimiento + N historial | HIGH |
| premio_model.obtener_premios_entregados | 1 SELECT por premio (limit 100) | MEDIUM |
| reels_model.consultar | 1 SELECT por reel | MEDIUM |
| reportes_data._datos_guiones | 1 SELECT por guion | MEDIUM |

### Queries sin límite

| Ubicación | Tabla | Riesgo |
|-----------|-------|--------|
| bitacora_model:33 | actividad_usuario | HIGH — crece indefinidamente |
| usuario_model:110 | usuarios | MEDIUM |
| patrocinador_model:102 | patrocinadores | LOW |

### Carga innecesaria de datos

| Ubicación | Problema |
|-----------|---------|
| reportes_data:147-166 | Carga TODO el dataset para encontrar MIN(fecha) |
| reportes_data:707-734 | 9 queries que cargan datasets completos para COUNT |
| reportes_data:63-68 | Carga TODOS los usuarios (incluyendo password_hash) para sanitizar |

---

## FRONTEND

### Archivos grandes sin code splitting

| Archivo | Líneas | Problema |
|---------|--------|----------|
| vivo.html | 1100+ | CSS + JS inline, sin cache |
| GestionReportes.js | 802 | Un archivo para todo el módulo reportes |
| ReportesConstructor.js | 586 | Wizard completo en un archivo |
| GestionBalance.js | 658 | 60% es código muerto |

### Assets sin optimizar

| Asset | Problema |
|-------|---------|
| Font import duplicado | head.html + dashboard.css cargan la misma fuente |
| SocketIO CDN sin SRI | Sin verificación de integridad |
| vivo.html CSS inline | 550 líneas que debieran ser archivo externo |

### Duplicación JS

| Función | Archivos donde está duplicada |
|---------|------------------------------|
| `getCSRF()` | GestionInventario, GestionBalance, ReportesConstructor, GestionTarea, GestionGuion, vivo.html |

---

## BASE DE DATOS

### Índices faltantes

| Tabla | Columna | Queries afectadas |
|-------|---------|-------------------|
| guiones | estado | en_vivo lookup en cada carga |
| tareas_asignadas | (id_usuario, Estatus) | Múltiples en tarea_model |
| actividad_usuario | created_at | ORDER BY en bitácora |
| sincronizaciones | (guion_id, fecha) | Sort en en_vivo_model |

### Connexiones

- autocommit=True globalmente → cada transaction() debe toggle
- Connection leak teórico en bitacora_model:103 (retorna raw connection)
- `Pago` hereda de `Database` — expone get_connection() innecesariamente

---

## RECOMENDACIONES PRIORIZADAS

| # | Acción | Impacto | Esfuerzo |
|---|--------|---------|----------|
| 1 | Fix N+1 en bitacora y mantenimiento | HIGH | MEDIO |
| 2 | Agregar índices faltantes | MEDIUM | BAJO |
| 3 | Extraer vivo.html CSS/JS a archivos externos | MEDIUM | MEDIO |
| 4 | Eliminar código muerto en GestionBalance.js | LOW | BAJO |
| 5 | Deduplicar getCSRF() | LOW | BAJO |
| 6 | Agregar LIMIT por defecto a bitacora | MEDIUM | BAJO |
| 7 | SELECT explícito sin password_hash | MEDIUM | BAJO |
| 8 | fix rango_fechas_defecto (SELECT MIN) | MEDIUM | BAJO |

---

## NOTA

No se realizó medición de tiempo de carga real (no hay baseline establecido). Las mejoras deben medirse ANTES y DESPUÉS para verificar impacto.
