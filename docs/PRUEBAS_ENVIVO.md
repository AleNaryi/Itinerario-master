# PRUEBAS MANUALES — Módulo EN VIVO (vivo.html rediseñado)

Checklist imprimible para cerrar el rediseño. Ejecutar después de cada cambio
importante de `app/view/en_vivo/vivo.html`. Automatizados: `venv/bin/pytest -q`.

## Preparación

```bash
venv/bin/python run.py        # http://localhost:5001
```

1. Iniciar sesión con un usuario **Superadmin** (puede operar).
2. Crear/publicar un guion con ≥4 elementos: 2 pregame + 2 game, con
   `duracion_estimada` corta (ej. 10s) para probar sobretiempo rápido.
3. `/en-vivo/` → **Iniciar** → abre la vista en vivo.
4. Abrir la MISMA vista en 2–3 navegadores/ventanas (A = operador, B y C = observadores).

## 1 · Secuencia y jerarquía

- [ ] El primer elemento aparece como tarjeta verde destacada (hero) con cronómetro `00:00` corriendo.
- [ ] Doble clic/doble toque en la hero → se completa (atenuada, con ✓) y SOLO el siguiente pasa a hero. Nunca salta dos.
- [ ] Intentar doble toque sobre una fila pendiente/completada → sin efecto.
- [ ] Barra SHOW del header: n/m y % suben al completar; al llegar a 100% hay celebración breve.

## 2 · Cronómetro y sobretiempo

- [ ] La hero muestra su cronómetro avanzando cada segundo; la barra de progreso interna crece hasta la duración estimada.
- [ ] Al superar la duración → cambia a `+MM:SS SOBRETIEMPO` en ámbar; el contador NO se detiene.
- [ ] Solo existe UN cronómetro activo (inspeccionar: ningún intervalo acumulado tras completar varios elementos).

## 3 · Retroceso (↩) — invariante: EXACTAMENTE UN elemento en curso

Semántica: *"marqué mal y aún lo debo ejecutar"*.

- [ ] **↩ sobre el actual (en curso)** → el actual vuelve a pendiente y el completado MÁS CERCANO ATRÁS se reactiva como hero. Ejemplo: `1✓ 2● 3○` → ↩ sobre 2 → `1● 2○ 3○`.
- [ ] **↩ sobre un completado** → CASACADA: ese elemento se reactiva y TODO lo posterior cae a pendiente. Ejemplo: `1✓ 2✓ 3● 4○` → ↩ sobre 1 → `1● 2○ 3○ 4○`. Nunca quedan estados ilegales tipo `1● 2✓`.
- [ ] Tras cualquier retroceso existe exactamente UN hero (o cero, solo en el borde del caso C).
- [ ] El cronómetro de la hero reactivada reinicia desde 00:00; los degradados pierden su timer.
- [ ] B y C reflejan la cascada al instante; en A aparece toast "Otro operador actualizó el guion" si el retroceso vino de otro operador.
- [ ] La bitácora (drawer 🕘) registra los elementos reiniciados.
- [ ] Caso borde C: si por algún motivo queda CERO elementos activos, ↩ sobre el primer pendiente lo reactiva (válvula de escape); con un activo existente, ↩ sobre pendientes es no-op.

## 4 · Multiusuario en tiempo real (SocketIO)

- [ ] A completa → B y C lo reflejan AL INSTANTE (sin recargar).
- [ ] B retrocede → A y C lo reflejan; en A aparece toast "Otro operador actualizó el guion".
- [ ] Contador 👥 del header refleja la cantidad de pestañas abiertas.
- [ ] Cerrar B → el contador baja solo.

## 5 · Conexión y offline

- [ ] Chip del header dice ● CONECTADO.
- [ ] Detener el servidor / desconectar WiFi → chip ● SIN CONEXIÓN (o ↻ RECONECTANDO).
- [ ] Sin conexión, marcar un elemento → la UI NO se congela; aparece ⚠ CAMBIOS PENDIENTES: 1.
- [ ] Marcar 2-3 elementos más offline → el contador sube; nada se pierde.
- [ ] Volver la conexión → flush automático, toast ✓ Guardado, badge desaparece, estado reconciliado con el servidor.

## 6 · Bitácora (drawer)

- [ ] Botón 🕘 del header abre drawer lateral con la bitácora del show.
- [ ] Los filtros Todos/Acciones/Eventos navegan DENTRO del drawer (la vista en vivo nunca se pierde).
- [ ] Los marcajes del operador aparecen en la bitácora (requiere fix autorizado del campo `accion`).
- [ ] Cierra con ✕, clic fuera o tecla Esc.

## 7 · Tema dark/light

- [ ] Toggle alterna ambos temas; persiste tras recargar.
- [ ] En LIGHT: textos legibles, hero verde visible, chips/badges/toasts/drawer con contraste correcto. Nada blanco-sobre-blanco.

## 8 · Permisos

- [ ] Usuario Superadmin: puede operar; atajos Espacio/R funcionan.
- [ ] Usuario solo espectador (`envivo.view` sin `envivo.control`): ve todo en tiempo real pero sus intentos de escritura son rechazados por el backend (error visible + estado reconciliado); atajos inoperativos.

## 9 · Finalizar

- [ ] Botón Finalizar → confirmación muestra "Completados: X · Pendientes: Y".
- [ ] Confirmar → regresa a /en-vivo/ con guion finalizado; los elementos quedan reseteados a pendiente (comportamiento esperado).

## 10 · Mobile físico (360–430px vertical)

- [ ] Header en 3 filas compactas, nada aplastado ni cortado.
- [ ] Doble tap completo SIN zoom accidental ni click fantasma; scroll fluido.
- [ ] Auto-scroll centra la hero al cambiar de elemento.
- [ ] Filtro por encargado oculta filas visualmente sin alterar contadores ni secuencia.
- [ ] Girar el teléfono no rompe layout; safe areas respetadas (notch).

## 11 · Desktop (1280–1920px)

- [ ] Lista centrada con buen uso horizontal; hero destacada sin ser gigante.
- [ ] Nada de scroll horizontal; lectura secuencial clara.

## 12 · Casos de error

- [ ] API caída → toast/error sin perder estado local; reintento automático.
- [ ] Doble tap muy rápido → no ejecuta dos veces ni rompe contadores.
- [ ] Recargar página a mitad del show → estado real restaurado desde servidor.
