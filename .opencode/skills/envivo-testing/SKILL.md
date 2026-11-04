---
name: envivo-testing
description: Protocolo de pruebas del módulo EN VIVO — secuencia y retroceso, multi-navegador con SocketIO, móvil/touch, offline, tema, permisos y finalización con pendientes; incluye correr venv/bin/pytest -q. Use when testing changes to app/view/en_vivo/, before closing any envivo task, or when the user says "probar en vivo", "testing envivo".
---

# envivo-testing

Nada se da por terminado sin este protocolo.

## Funcionales

1. **Secuencia**: iniciar guion → primer elemento `en_curso` → doble toque completa y avanza UNO. Verificar que es imposible saltar elementos.
2. **Retroceso** (botón ↩): completado→en_curso; en_curso→pendiente reactivando el anterior pendiente.
3. **SocketIO multiusuario**: 2–3 navegadores con el mismo guion; A completa → B y C lo reflejan AL INSTANTE. Probar también A completa / B retrocede / C observa.
4. **Permisos**: usuario con `envivo.control` opera; espectador ve todo pero sus escrituras son rechazadas por el backend (la UI muestra el error y se reconcilia).
5. **Finalizar** con elementos pendientes: confirmación debe mostrar completados vs pendientes; tras finalizar los elementos vuelven a `pendiente`.
6. **Tema**: dark/light conmutables, persistente tras recargar, contraste correcto en ambos.

## Resiliencia

7. **Offline**: cortar red → marcar elemento → aparece CAMBIOS PENDIENTES → volver la red → flush automático y reconciliación sin perder acciones.
8. **Reconexión socket**: matar/restaurar servidor; la UI se re-registra, consulta estado-actual y descarta estados viejos.
9. **Doble tap rápido/accidental**: no doble ejecución ni zoom accidental en móvil.

## Automatizado

```bash
venv/bin/python run.py      # arranque dev :5001
venv/bin/pytest -q          # suite contra BDs *_test
```

Registrar cualquier hallazgo como Problema/Impacto/Riesgo/Recomendación/Archivo.
