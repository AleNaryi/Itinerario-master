---
name: refactor-controladores
description: Patrón de refactorización para controladores Flask de Itinerario — extraer helpers duplicados y dividir archivos gigantes sin romper el MVC. Use when a controller file grows too large, when duplicating logic between controllers (ej. _registrar_bitacora), or when the user says "refactor", "limpiar controlador", "duplicado", "dividir archivo".
---

# Refactor de controladores — Itinerario

Objetivo: menos duplicación, mismos blueprints, mismo estilo MVC. Un refactor NO cambia rutas, nombres de campo ni respuestas JSON.

## Deudas conocidas (atacar cuando se toque el archivo)

1. **`_registrar_bitacora` duplicado en ~15 controladores** (patrocinador, contrato, usuario, etc.). Extraer UNA vez a `app/helpers/` (p. ej. `bitacora_helper.py`) con firma `(accion, titulo, detalle=None)` que use `current_user` + `BitacoraModel`. Reemplazar import en cada controlador; borrar las copias locales.
2. **`reportes_controller.py` (~1.213 líneas):** la cadena if/elif de `_obtener_datos()` (línea ~455) debe despachar a funciones por módulo o a la estructura ya existente en `app/helpers/generators/`. Dividir por módulo: `_datos_contratos`, `_datos_inventario`, ... en archivos separados bajo `app/helpers/reportes_data/` si supera lo razonable.
3. **`_filtros_*` y helpers sueltos del mismo archivo** (`_parsear_fecha`, `_ordenar_datos`, etc.) → candidatos a mover a `app/helpers/reportes_utils.py`.

## Reglas del refactor

- Pasos pequeños y verificables: mover un helper → correr la app/ruta afectada → siguiente.
- No mezclar refactor con features nuevas en el mismo commit.
- Mantener decoradores de permisos exactamente como estaban en cada ruta movida.
- Los modelos NO se tocan salvo que la duplicación esté allí también; mismo criterio.

## Checklist

- [ ] ¿La ruta sigue respondiendo igual antes/después? (mismo status, mismas claves JSON)
- [ ] ¿Los permisos siguen aplicando?
- [ ] ¿Quedó una sola copia del helper extraído?
- [ ] ¿Se eliminaron imports muertos?
