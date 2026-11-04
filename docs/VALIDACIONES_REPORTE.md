# Reporte de Validaciones — Backend / Frontend / JavaScript

**Fecha:** 2025-08-25 · **Alcance:** auditoría de solo lectura de las 3 capas de validación en los 11 módulos con escritura de datos.
**Método:** lectura de código (`app/static/js/validaciones/`, `app/view/`, `app/model/`, `app/controller/`) + suite de tests como evidencia base.
**Suite:** `venv/bin/pytest -q` → **63 passed** al auditar · **71 passed** tras las correcciones (ver §8).

> Regla del proyecto (AGENTS.md): las validaciones JS son solo UX y NO sustituyen la validación server-side. Este reporte marca dónde esa regla se incumple de facto.

---

## 0. ACTUALIZACIÓN — Correcciones aplicadas (misma fecha)

Tras la auditoría se corrigieron los hallazgos priorizados (§7). Estado:

| Ítem | Estado | Cambio |
|------|--------|--------|
| C1 contrato | ✅ Corregido | `self.errores` en vez de `self._errores`; fechas pasan por `validar_fecha` (`contrato_model.py`). Test de regresión en `tests/test_validaciones.py`. |
| C2 balance | ✅ Corregido | `float(monto)` protegido + check >0; re-chequeo de saldo disponible en edición (descuenta lo ya pagado y devuelve el margen del pago editado); `modificar_pago` llama `validar_monto`; guards `isdigit()` para ids (`balance_controller.py`, `balance_model.py`). |
| C3 reel | ✅ Corregido | `registrar/modificar` validan nombre (2–50) vía `_validar_nombre`; `duracion_segundos` y `orden` con casts seguros y fallback en `agregar-video` (`reels_model.py`, `reels_controller.py`). Tests incluidos. |
| C4 guion | ✅ Corregido | Whitelist `tipo in ('pregame','game')` en agregar/editar elemento; parses de hora/inning envueltos en try→flash; `date.fromisoformat` de replicar protegido (`guion_controller.py`). |
| C5 inventario | ✅ Corregido | Costo validado (>0, numérico, opcional) en `_validar_datos_recurso`; `fecha_devolucion_esperada` validada con `fromisoformat`; guards `isdigit()` en asignaciones (`inventario_model.py`, `inventario_controller.py`). Tests incluidos. |
| C6 rol | ✅ Corregido | Cast `int(pid)` solo para dígitos + escritura de rol+permisos dentro de `transaction('seguridad')` en `/crear` y en `RolPermisoModel.actualizar_permisos` (`rol_controller.py`, `rol_model.py`). |
| M1/M2 email/RIF | ✅ Parcial | Nuevos helpers `validar_email`/`validar_rif` en el mixin central; aplicados en usuario (email) y patrocinador (RIF + email opcional). Tests incluidos. Teléfono/contacto siguen sin validar server-side (queda documentado). |
| B1 JS muertos | ✅ Borrados | Eliminados: GestionGuion/Balance/Premio/Tarea/Reel Validacion.js (cero referencias). Vivos: Usuario, Inventario, Patrocinador, Contrato, Rol. |
| M3 premio | ✅ Corregido | `id_patrocinador` obligatorio + entero positivo en `_validar_datos_premio`; descripción limitada a 500 (como el maxlength del form); `cantidad_entregar` e `id_patrocinador` de entrega validados con `isdigit` antes del cast (`premio_model.py`, `premio_controller.py`). Tests incluidos. |
| M4 mantenimiento | ✅ Corregido | `fecha_ingreso` pasa por `validar_fecha`; nota de historial limitada a 500 en controller (`mantenimiento_model.py`, `mantenimiento_controller.py`). Test incluido. |
| M5 formAsignarTarea | ✅ Corregido | `novalidate` removido + `required` en select de tarea (nativo ahora bloquea envío vacío); empleados/departamento siguen sin required porque es relación "y/o" — lo cubre el JS inline existente. |
| M6 inventario crear/editar | ✅ Corregido | Removido `novalidate`: sus `required` nativos ahora funcionan en cliente sin cargar JS. |
| B5 HTML balance | ✅ Corregido | Atributo colgante `...>` eliminado del input referencia (`balance/dashboard.html:279`). |
| B6 fallback fechas | ✅ Corregido | Fecha/hora de pago inválida ahora rechaza con flash en registrar y editar pago (antes se sustituía silenciosamente por hoy/ahora). |

**Decisiones sobre lo restante:**
- **B2** (`validar_texto`/`sanitizar_texto` sin usar): **se decide NO aplicarlos masivamente** — rechazarían entradas legítimas (@ en emails, paréntesis en nombres). Los huecos reales detrás de B2 ya se cerraron con validaciones por campo y límites de longitud. Helpers quedan disponibles para casos puntuales.
- **B3**: resuelto de facto al borrar el archivo duplicado (B1).
- **B4**: sin acción práctica — `crear_rol.html` tiene un único formulario, y `editar_rol.html` solo contiene checkboxes (no hay campos que validar).
- Pendiente menor documentado: patrocinador teléfono/contacto sin límite server-side (bajo riesgo, columnas TEXT/varchar generosas).

---

## 1. Resumen ejecutivo

- **Backend:** patrón dominante correcto — validación centralizada en `_validar_datos_*()` antes del INSERT/UPDATE usando `ValidacionesMixin`. Pero hay **6 huecos críticos**, dos de ellos con validación *rota en runtime* (contrato) o *muerta* (reels).
- **Frontend:** casi todos los formularios usan `novalidate` + atributos HTML; los `required` sin JS detrás son letra muerta en cliente. 3 formularios quedan totalmente desprotegidos en cliente.
- **JavaScript:** de 10 archivos de validación, **solo 4+1 están vivos** (Usuario, Inventario, Patrocinador, Contrato vía su `Gestion*.js`; Rol auto-conectado en `crear_rol.html`). **5 archivos son muertos**: nadie los importa (Guion, Balance, Premio, Tarea, Reel). Falsa sensación de cobertura.

---

## 2. Hallazgos CRÍTICOS (verificados línea a línea)

### C1. Contrato — validación rota en runtime (500 en vez de rechazo)
`app/model/contrato_model.py:62-73`: `_validar_datos_contrato()` hace `self._errores.append(...)` pero el mixin expone `self.errores`. Cuando intenta rechazar `fecha_fin < fecha_inicio` o un monto inválido lanza `AttributeError` → HTTP 500, en vez de devolver False. Además las fechas nunca pasan por `validar_fecha` (comparación lexicográfica de strings crudos).

### C2. Balance — editar pago sin validar monto ni nada
`app/controller/balance_controller.py:166`: `'monto': float(monto)` sin try → basura = 500. `Pago.modificar_pago()` (`balance_model.py:214-238`) NO llama `validar_monto` (solo existe en `registrar_pago`, L109): dinero editable sin check >0 ni re-chequeo de saldo. Además `balance_model.py:7-14` define su **propia copia local** de `ValidacionesMixin` (solo `validar_monto`), incompatible con el mixin central.

### C3. Reel — validación del modelo muerta para el flujo real
`ReelModel._validar_datos_recurso()` existe (`reels_model.py:60-67`) pero solo lo invocan `confirmar_registro()/confirmar_modificacion()` (L70,75); las rutas llaman a `registrar(datos)` (L89) y `modificar(id, datos)` (L102), que **no validan nada**. En videos: `duracion_segundos` y `orden` llegan crudos del form/JSON a BD (`reel_controller.py:167-168`), nombre de video sin límite.

### C4. Guion/elementos — 500s por parsing sin try + tipo sin whitelist
`guion_controller.py`: `int(hp[0])` (L101-102), `int(inning_str)` (L103) y `date.fromisoformat` en replicar (L316) explotan con input malformado → 500. `tipo` de elemento acepta cualquier valor distinto de pregame/game (sin whitelist, L83-86). `encargado`/`medio_inning` texto libre sin límite. `ElementoGuionModel.modificar()` (`guion_model.py:388`) persiste **sin ninguna validación del mixin**.

### C5. Inventario — costo y asignaciones sin filtro
`inventario_model.py:105-111`: `costo` llega al INSERT sin ninguna validación (negativos OK, "abc" revienta en BD). Asignaciones (`registrar_asignacion`, L309): `fecha_devolucion_esperada` string crudo a BD, `notas` sin límite; casts `int()` sin try en `inventario_controller.py:217,252,263` → 500.

### C6. Rol — permisos crudos y escritura sin transacción
`rol_controller.py:153-157`: loop de INSERT de `rol_permiso` con `pid` crudo del formulario (sin cast/existencia) y **sin transacción**: si falla a mitad, el rol queda creado con permisos parciales. Igual en `RolPermisoModel` (`rol_model.py:383-387`). Contraste: la edición de permisos de usuario SÍ castea `int(p)` (`rol_model.py:524,531`).

---

## 3. Hallazgos MEDIOS

| # | Hallazgo | Referencia |
|---|----------|-----------|
| M1 | Usuario: email validado por longitud pero **sin formato email** server-side (JS sí valida formato → frontend más estricto que backend) | `usuario_model.py:66,70` |
| M2 | Patrocinador: `rif` obligatorio pero sin formato/longitud; `telefono`, `email`, `nombre_contacto` sin NADA server-side (JS valida teléfono/email opcionales); `encargado_id` sin verificar existencia del usuario | `patrocinador_model.py:67,87` |
| M3 | Premio: `id_patrocinador` crudo del form a INSERT/UPDATE; `descripcion` largo ilimitado; `cantidad_entregar` con `int()` sin try → 500 | `premio_model.py:66-67,119,240-241`; `premio_controller.py:113` |
| M4 | Mantenimiento: `fecha_ingreso` sin `validar_fecha` (formato malo = excepción BD logueada); nota de historial sin límite máximo. No existe JS de validación para este módulo (aceptable: server-first, pero documentado aquí) | `mantenimiento_model.py:127`; `mantenimiento_controller.py:104-107` |
| M5 | Tarea: `formAsignarTarea` tiene **cero required en HTML** pese a labels con "\*"; solo el handler JS inline lo salva | `gestion_tarea/dashboard.html`; `GestionTarea.js` |
| M6 | Inventario `crear.html`/`editar.html`: `novalidate` + `required` letra muerta y **sin cargar ningún JS** → en cliente nada impide envío vacío; única defensa = servidor (con hueco C5) | `inventario/crear.html`, `editar.html` |

---

## 4. Hallazgos BAJOS

| # | Hallazgo | Referencia |
|---|----------|-----------|
| B1 | 5 archivos JS de validación muertos: `GestionGuionValidacion.js`, `GestionBalanceValidacion.js`, `GestionPremioValidacion.js`, `GestionTareaValidacion.js`, `GestionReelValidacion.js` — cero imports/referencias en todo `app/`. Sugieren cobertura que no existe | `app/static/js/validaciones/` |
| B2 | `validar_texto`/`sanitizar_texto` del mixin **jamás invocados** en ningún módulo — no hay sanitización de caracteres especiales server-side | `validaciones_model.py:59-85` |
| B3 | `GestionReelValidacion.js` duplica inline `mostrarError/mostrarValido` en vez de usar `validacion.js` | `GestionReelValidacion.js:3-15` |
| B4 | `GestionRolValidacion.js` engancha el PRIMER `form[novalidate]` de la página y solo está cargado en `crear_rol.html` (no en editar) | `crear_rol.html:95` |
| B5 | Bug HTML: atributo colgante `...>` en input referencia | `balance/dashboard.html:279` |
| B6 | Fechas/hora de pago en balance: `strptime` con **fallback silencioso** a hoy/ahora (dato corrupto entra sin aviso) | `balance_controller.py:108-113,158-163` |

---

## 5. Matriz por módulo × capa

| Módulo | JS (client UX) | HTML nativa | Backend (server-side) | Veredicto |
|--------|----------------|-------------|----------------------|-----------|
| Usuario | ✓ vivo (`GestionUsuarioValidacion.js`) | ✓ required+maxlength (+novalidate) | ✓ sólido (falta formato email, M1) | **OK menor** |
| Tarea | ✗ muerto (JS inline en GestionTarea.js) | parcial (asignar sin required, M5) | ✓ sólido (whitelists, ids filtrados) | **OK menor** |
| Rol | ~ solo crear_rol.html | ✓ crear; edición solo checkboxes | ⚠️ C6 | **Hueco** |
| Patrocinador | ✓ vivo | ✓ | ⚠️ M2 | **Hueco medio** |
| Premio | ✗ muerto | parcial (patrocinador select sin required) | ⚠️ M3 | **Hueco medio** |
| Mantenimiento | — (no existe) | n/a | ⚠️ M4 | **Hueco medio** |
| Guion | ✗ muerto (inline en GestionGuion.js) | crear/editar ✓; elementos ✗ | 🔴 C4 | **Crítico** |
| Inventario | ~ vivo solo dashboard/asignar; crear/editar SIN JS | ✓ pero letra muerta en crear/editar | 🔴 C5 | **Crítico** |
| Reel | ✗ muerto (inline en template) | parcial (duración sin pattern) | 🔴 C3 | **Crítico** |
| Balance | ✗ muerto (inline en GestionBalance.js) | ✓ únicos forms con validación NATIVA activa (pattern) | 🔴 C2 | **Crítico** |
| Contrato | ✓ vivo (único con comparación entre campos) | ✓ | 🔴 C1 | **Crítico** |

---

## 6. Inventario de helpers disponibles vs uso real

`app/model/validaciones_model.py` (`ValidacionesMixin`):

| Helper | Firma | Uso real |
|--------|-------|----------|
| `validar_obligatorio(s)` | `(valor, nombre)` / `(campos, datos)` | Amplio uso ✓ |
| `validar_longitud` | `(texto, min, max, campo)` | Amplio uso ✓ |
| `validar_entero_positivo` | `(numero, campo)` | Solo inventario |
| `validar_fecha` | `(fecha, campo)` — YYYY-MM-DD + fecha real | Solo inventario |
| `validar_fecha_no_futura` | `(fecha, campo)` | Solo inventario |
| `validar_texto` | rechaza `<>"'{}()&$%@*=;/\|~` | **Nunca usado** |
| `sanitizar_texto` (static) | elimina `<>/` y recorta | **Nunca usado** |
| `get_errores / limpiar_errores / tiene_errores` | — | Amplio uso ✓ (contrato usa nombre equivocado, C1) |

Helpers JS compartidos (`app/static/js/validacion.js` + `RegExp.js`): regex de nombre 2–50, email, cédula 6–10, RIF `[JGVE]-?\d{7,10}`, costo >0 con ≤2 decimales, fecha YYYY-MM-DD ≤ hoy, hora HH:MM, select no-vacío. 9 de 10 archivos delegan aquí; Reel duplica inline.

---

## 7. Recomendaciones priorizadas (para cuando se decida corregir)

1. **C1 contrato:** `self._errores` → `self.errores` (3 líneas) + pasar fechas por `validar_fecha`. Añadir test de regresión.
2. **C2 balance:** try/except en `float(monto)` del controller + llamar `validar_monto` en `modificar_pago` (+ re-chequeo de saldo).
3. **C3 reel:** que `registrar/modificar` invoquen `_validar_datos_recurso`; validar `duracion_segundos`/`orden` en controller.
4. **C4 guion:** envolver parses en try (400 con flash en vez de 500) + whitelist de `tipo`.
5. **C5 inventario:** validar costo (>0, numérico) en `_validar_datos_recurso`; validar formato de `fecha_devolucion_esperada`.
6. **C6 rol:** cast `int(pid)` + transacción única para rol+permisos.
7. **B1:** borrar los 5 archivos JS muertos o conectarlos (decidir por módulo).
8. **M1/M2:** formato email/RIF server-side donde el JS ya lo exige.

---
*Generado por auditoría automatizada + verificación manual línea a línea. Fuente de verdad: el código referenciado.*
