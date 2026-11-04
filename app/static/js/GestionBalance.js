// import { validarCosto, validarFecha, validarHora, validarSelect } from './validacion.js';

// document.addEventListener('DOMContentLoaded', function() {
//     const selectContrato = document.getElementById('selectContrato');
//     const infoContrato = document.getElementById('infoContrato');
//     const nombrePatrocinadorSpan = document.getElementById('nombrePatrocinador');
//     const montoTotalSpan = document.getElementById('montoTotalContrato');
//     const saldoPendienteSpan = document.getElementById('saldoPendienteContrato');
//     const montoPago = document.getElementById('montoPago');

//     if (selectContrato) {
//         selectContrato.addEventListener('change', async function() {
//             const contratoId = this.value;
//             if (contratoId) {
//                 try {
//                     const response = await fetch(`/balance/api/contrato/${contratoId}`);
//                     const data = await response.json();
//                     if (!data.error) {
//                         nombrePatrocinadorSpan.textContent = data.nombre_patrocinador || 'Sin patrocinador';
//                         montoTotalSpan.textContent = data.monto_total.toFixed(2);
//                         saldoPendienteSpan.textContent = data.saldo_pendiente.toFixed(2);
//                         infoContrato.style.display = 'block';
//                         if (montoPago) montoPago.max = data.saldo_pendiente;
//                     }
//                 } catch (err) {
//                     console.error("Error al obtener la información del contrato:", err);
//                 }
//             } else {
//                 infoContrato.style.display = 'none';
//             }
//         });
//     }

//     if (montoPago) {
//         montoPago.addEventListener('blur', function() { validarCosto(this); });
//     }

//     document.addEventListener('click', async function(e) {
//         const btn = e.target.closest('.btn-editar-pago');
//         if (btn) {
//             const pagoId = btn.getAttribute('data-id');
//             try {
//                 const response = await fetch(`/balance/api/pago/${pagoId}`);
//                 const data = await response.json();
                
//                 document.getElementById('edit_pago_id').value = data.id_pago;
//                 document.getElementById('edit_monto').value = data.monto;
//                 document.getElementById('edit_tipo_pago').value = data.tipo_pago;
//                 document.getElementById('edit_referencia').value = data.referencia || '';
//                 document.getElementById('edit_fecha_pago').value = data.fecha_pago.split('/').reverse().join('-');
//                 document.getElementById('edit_hora_pago').value = data.hora_pago;
//                 document.getElementById('edit_notas').value = data.Descripción || '';
                
//                 new bootstrap.Modal(document.getElementById('modalEditarPago')).show();
//             } catch (err) {
//                 console.error("Error al obtener datos del pago:", err);
//             }
//         }
//     });

//     document.addEventListener('click', function(e) {
//         const btn = e.target.closest('.btn-eliminar-pago');
//         if (btn) {
//             const pagoId = btn.getAttribute('data-id');
//             Swal.fire({
//                 title: '¿Eliminar pago?',
//                 text: 'Esta acción no se puede deshacer.',
//                 icon: 'warning',
//                 showCancelButton: true,
//                 confirmButtonColor: '#dc3545',
//                 cancelButtonColor: '#6c757d',
//                 confirmButtonText: 'Sí, eliminar',
//                 cancelButtonText: 'Cancelar'
//             }).then((result) => {
//                 if (result.isConfirmed) {
//                     const form = document.createElement('form');
//                     form.method = 'POST';
//                     form.action = `/balance/eliminar-pago/${pagoId}`;

//                     const csrfInput = document.createElement('input');
//                     csrfInput.type = 'hidden';
//                     csrfInput.name = 'csrf_token';
//                     csrfInput.value = document.querySelector('input[name="csrf_token"]')?.value || '';

//                     form.appendChild(csrfInput);
//                     document.body.appendChild(form);
//                     form.submit();
//                 }
//             });
//         }
//     });

//     const formRegistrar = document.getElementById('formRegistrarPago');
//     if (formRegistrar) {
//         formRegistrar.addEventListener('submit', function(e) {
//             const valContrato = validarSelect(selectContrato);
//             const valMonto = validarCosto(montoPago);
//             const fechaPago = document.querySelector('[name="fecha_pago"]');
//             const horaPago = document.querySelector('[name="hora_pago"]');
//             const valFecha = validarFecha(fechaPago);
//             const valHora = validarHora(horaPago);

//             if (!valContrato || !valMonto || !valFecha || !valHora) {
//                 e.preventDefault();
//                 Swal.fire({
//                     title: 'Error de validación',
//                     text: 'Corrige los campos marcados en rojo.',
//                     icon: 'error',
//                     confirmButtonColor: '#3085d6'
//                 });
//                 return;
//             }

//             e.preventDefault();
//             Swal.fire({
//                 title: '¿Registrar pago?',
//                 text: 'Se registrará un nuevo pago en el sistema.',
//                 icon: 'question',
//                 showCancelButton: true,
//                 confirmButtonColor: '#198754',
//                 cancelButtonColor: '#6c757d',
//                 confirmButtonText: 'Sí, registrar',
//                 cancelButtonText: 'Cancelar'
//             }).then((result) => {
//                 if (result.isConfirmed) {
//                     formRegistrar.submit();
//                 }
//             });
//         });
//     }

//     const formEditar = document.getElementById('formEditarPago');
//     if (formEditar) {
//         formEditar.addEventListener('submit', function(e) {
//             e.preventDefault();
//             Swal.fire({
//                 title: '¿Guardar cambios?',
//                 text: 'Se actualizarán los datos de este pago.',
//                 icon: 'question',
//                 showCancelButton: true,
//                 confirmButtonColor: '#198754',
//                 cancelButtonColor: '#6c757d',
//                 confirmButtonText: 'Sí, guardar',
//                 cancelButtonText: 'Cancelar'
//             }).then((result) => {
//                 if (result.isConfirmed) {
//                     formEditar.submit();
//                 }
//             });
//         });
//     }

//     document.querySelectorAll('.filter-chip').forEach(chip => {
//         chip.addEventListener('click', function() {
//             document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
//             this.classList.add('active');
            
//             const filter = this.getAttribute('data-filter');
//             document.querySelectorAll('.contract-item').forEach(item => {
//                 if (filter === 'all') {
//                     item.style.display = '';
//                 } else {
//                     item.style.display = item.getAttribute('data-status') === filter ? '' : 'none';
//                 }
//             });
//         });
//     });
// });


// import { validarCosto, validarFecha, validarHora, validarSelect } from './validacion.js';

// document.addEventListener('DOMContentLoaded', function() {
//     const selectContrato = document.getElementById('selectContrato');
//     const infoContrato = document.getElementById('infoContrato');
//     const nombrePatrocinadorSpan = document.getElementById('nombrePatrocinador');
//     const montoTotalSpan = document.getElementById('montoTotalContrato');
//     const saldoPendienteSpan = document.getElementById('saldoPendienteContrato');
//     const montoPago = document.getElementById('montoPago');

//     // Manejo del cambio de contrato para el formulario de registro
//     if (selectContrato) {
//         selectContrato.addEventListener('change', async function() {
//             const contratoId = this.value;
//             if (contratoId) {
//                 try {
//                     const response = await fetch(`/balance/api/contrato/${contratoId}`);
//                     const data = await response.json();
//                     if (!data.error) {
//                         if (nombrePatrocinadorSpan) nombrePatrocinadorSpan.textContent = data.nombre_patrocinador || 'Sin patrocinador';
//                         if (montoTotalSpan) montoTotalSpan.textContent = parseFloat(data.monto_total).toFixed(2);
//                         if (saldoPendienteSpan) saldoPendienteSpan.textContent = parseFloat(data.saldo_pendiente).toFixed(2);
//                         if (infoContrato) infoContrato.style.display = 'block';
                        
//                         // Restringir el máximo valor permitible al saldo pendiente real
//                         if (montoPago) montoPago.max = data.saldo_pendiente;
//                     }
//                 } catch (err) {
//                     console.error("Error al obtener la información del contrato:", err);
//                 }
//             } else {
//                 if (infoContrato) infoContrato.style.display = 'none';
//             }
//         });
//     }

//     // Validación interactiva on-blur para el monto de registro
//     if (montoPago) {
//         montoPago.addEventListener('blur', function() { validarCosto(this); });
//     }

//     // Delegación de Eventos: Botón Editar Pago
//     document.addEventListener('click', async function(e) {
//         const btn = e.target.closest('.btn-editar-pago');
//         if (btn) {
//             const pagoId = btn.getAttribute('data-id');
//             try {
//                 const response = await fetch(`/balance/api/pago/${pagoId}`);
//                 const data = await response.json();
                
//                 // Carga segura de los datos estructurales fijos
//                 if (document.getElementById('edit_pago_id')) document.getElementById('edit_pago_id').value = data.id_pago;
//                 if (document.getElementById('edit_monto')) document.getElementById('edit_monto').value = data.monto;
//                 if (document.getElementById('edit_tipo_pago')) document.getElementById('edit_tipo_pago').value = data.tipo_pago;
//                 if (document.getElementById('edit_referencia')) document.getElementById('edit_referencia').value = data.referencia || '';
                
//                 // CONTROL DE SEGURIDAD: Solo setear campos opcionales si existen en el HTML modal
//                 const inputFecha = document.getElementById('edit_fecha_pago');
//                 if (inputFecha && data.fecha_pago) {
//                     let fechaFormateada = data.fecha_pago.includes('/') 
//                         ? data.fecha_pago.split('/').reverse().join('-') 
//                         : data.fecha_pago;
//                     inputFecha.value = fechaFormateada;
//                 }
                
//                 const inputHora = document.getElementById('edit_hora_pago');
//                 if (inputHora) inputHora.value = data.hora_pago || '';

//                 const inputNotas = document.getElementById('edit_notes') || document.getElementById('edit_notas');
//                 if (inputNotas) inputNotas.value = data.descripcion || '';
                
//                 // Desplegar Modal de Bootstrap
//                 const modalEl = document.getElementById('modalEditarPago');
//                 if (modalEl) {
//                     new bootstrap.Modal(modalEl).show();
//                 }
//             } catch (err) {
//                 console.error("Error al obtener datos del pago:", err);
//             }
//         }
//     });

//     // Delegación de Eventos: Botón Eliminar Pago
//     document.addEventListener('click', function(e) {
//         const btn = e.target.closest('.btn-eliminar-pago');
//         if (btn) {
//             const pagoId = btn.getAttribute('data-id');
//             Swal.fire({
//                 title: '¿Eliminar pago?',
//                 text: 'Esta acción no se puede deshacer y recalculará los saldos.',
//                 icon: 'warning',
//                 showCancelButton: true,
//                 confirmButtonColor: '#dc3545',
//                 cancelButtonColor: '#6c757d',
//                 confirmButtonText: 'Sí, eliminar',
//                 cancelButtonText: 'Cancelar'
//             }).then((result) => {
//                 if (result.isConfirmed) {
//                     const form = document.createElement('form');
//                     form.method = 'POST';
//                     form.action = `/balance/eliminar-pago/${pagoId}`;

//                     const csrfInput = document.createElement('input');
//                     csrfInput.type = 'hidden';
//                     csrfInput.name = 'csrf_token';
//                     csrfInput.value = document.querySelector('input[name="csrf_token"]')?.value || '';

//                     form.appendChild(csrfInput);
//                     document.body.appendChild(form);
//                     form.submit();
//                 }
//             });
//         }
//     });

//     // Envío y Validación del Formulario de Registro
//     const formRegistrar = document.getElementById('formRegistrarPago');
//     if (formRegistrar) {
//         formRegistrar.addEventListener('submit', function(e) {
//             const valContrato = validarSelect(selectContrato);
//             const valMonto = validarCosto(montoPago);
//             const fechaPago = document.querySelector('#formRegistrarPago [name="fecha_pago"]');
//             const horaPago = document.querySelector('#formRegistrarPago [name="hora_pago"]');
            
//             const valFecha = fechaPago ? validarFecha(fechaPago) : true;
//             const valHora = horaPago ? validarHora(horaPago) : true;

//             if (!valContrato || !valMonto || !valFecha || !valHora) {
//                 e.preventDefault();
//                 Swal.fire({
//                     title: 'Error de validación',
//                     text: 'Corrige los campos marcados en oro o rojo antes de guardar.',
//                     icon: 'error',
//                     confirmButtonColor: '#3085d6'
//                 });
//                 return;
//             }

//             e.preventDefault();
//             Swal.fire({
//                 title: '¿Registrar pago?',
//                 text: 'Se registrará un nuevo pago en el sistema.',
//                 icon: 'question',
//                 showCancelButton: true,
//                 confirmButtonColor: '#198754',
//                 cancelButtonColor: '#6c757d',
//                 confirmButtonText: 'Sí, registrar',
//                 cancelButtonText: 'Cancelar'
//             }).then((result) => {
//                 if (result.isConfirmed) {
//                     formRegistrar.submit();
//                 }
//             });
//         });
//     }

//     // Envío y Validación del Formulario de Edición (Corregido)
//     const formEditar = document.getElementById('formEditarPago');
//     if (formEditar) {
//         formEditar.addEventListener('submit', function(e) {
//             const editMonto = document.getElementById('edit_monto');
//             const editFecha = document.getElementById('edit_fecha_pago');
//             const editHora = document.getElementById('edit_hora_pago');

//             // Si el elemento existe se valida, si no existe en el HTML pasa por defecto como true
//             const valMonto = editMonto ? validarCosto(editMonto) : true;
//             const valFecha = editFecha ? validarFecha(editFecha) : true;
//             const valHora = editHora ? validarHora(editHora) : true;

//             if (!valMonto || !valFecha || !valHora) {
//                 e.preventDefault();
//                 Swal.fire({
//                     title: 'Error de validación',
//                     text: 'Asegúrate de que los datos modificados sean válidos.',
//                     icon: 'error',
//                     confirmButtonColor: '#3085d6'
//                 });
//                 return;
//             }

//             e.preventDefault();
//             Swal.fire({
//                 title: '¿Guardar cambios?',
//                 text: 'Se actualizarán los datos de este pago.',
//                 icon: 'question',
//                 showCancelButton: true,
//                 confirmButtonColor: '#198754',
//                 cancelButtonColor: '#6c757d',
//                 confirmButtonText: 'Sí, guardar',
//                 cancelButtonText: 'Cancelar'
//             }).then((result) => {
//                 if (result.isConfirmed) {
//                     formEditar.submit();
//                 }
//             });
//         });
//     }

//     // Filtros por chips para el Grid de Contratos
//     document.querySelectorAll('.filter-chip').forEach(chip => {
//         chip.addEventListener('click', function() {
//             document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
//             this.classList.add('active');
            
//             const filter = this.getAttribute('data-filter');
//             document.querySelectorAll('.contract-item').forEach(item => {
//                 if (filter === 'all') {
//                     item.style.display = '';
//                 } else {
//                     item.style.display = item.getAttribute('data-status') === filter ? '' : 'none';
//                 }
//             });
//         });
//     });
// });


import { validarCosto, validarFecha, validarHora, validarSelect } from './validacion.js';

document.addEventListener('DOMContentLoaded', function() {
    const selectContrato = document.getElementById('selectContrato');
    const infoContrato = document.getElementById('infoContrato');
    const nombrePatrocinadorSpan = document.getElementById('nombrePatrocinador');
    const montoTotalSpan = document.getElementById('montoTotalContrato');
    const saldoPendienteSpan = document.getElementById('saldoPendienteContrato');
    const montoPago = document.getElementById('montoPago');

    // ==========================================
    // LÓGICA PARA OCULTAR COMPROBANTE / REFERENCIA
    // ==========================================
    /**
     * Oculta o muestra el contenedor del campo referencia según el método seleccionado.
     * @param {HTMLSelectElement} selectElement - El select del tipo de pago
     * @param {string} inputId - El ID del input de referencia a limpiar/manipular
     */
    function alternarReferencia(selectElement, inputId) {
        if (!selectElement) return;
        
        const inputReferencia = document.getElementById(inputId);
        if (!inputReferencia) return;

        // Buscamos el contenedor col-md-6 o col-md-12 del input para ocultarlo por completo
        const contenedor = inputReferencia.closest('.col-md-6') || inputReferencia.closest('.col-md-12');
        
        if (selectElement.value === 'Efectivo') {
            if (contenedor) contenedor.style.display = 'none';
            inputReferencia.value = ''; // Limpiamos el valor para que no mande basura al backend
            inputReferencia.removeAttribute('required'); // Por si acaso tuviera la propiedad
        } else {
            if (contenedor) contenedor.style.display = 'block';
        }
    }

    // Configurar comportamiento en el Formulario de Registro
    const selectTipoPagoReg = document.querySelector('#formRegistrarPago [name="tipo_pago"]');
    if (selectTipoPagoReg) {
        // Escuchar cambios del usuario
        selectTipoPagoReg.addEventListener('change', function() {
            alternarReferencia(this, 'referencia'); // En registrar el input no tiene ID, se busca por Name o añade id="referencia" en el HTML
        });
        // Ejecutar al cargar por si inicia en Efectivo
        alternarReferencia(selectTipoPagoReg, 'referencia');
    }

    // Configurar comportamiento en el Formulario de Edición
    const selectTipoPagoEdit = document.getElementById('edit_tipo_pago');
    if (selectTipoPagoEdit) {
        selectTipoPagoEdit.addEventListener('change', function() {
            alternarReferencia(this, 'edit_referencia');
        });
    }


    // ==========================================
    // MANEJO DE CONTRATOS Y OTROS EVENTOS
    // ==========================================
    if (selectContrato) {
        selectContrato.addEventListener('change', async function() {
            validarSelect(this);
            const contratoId = this.value;
            if (contratoId) {
                try {
                    const response = await fetch(`/balance/api/contrato/${contratoId}`);
                    const data = await response.json();
                    if (!data.error) {
                        if (nombrePatrocinadorSpan) nombrePatrocinadorSpan.textContent = data.nombre_patrocinador || 'Sin patrocinador';
                        if (montoTotalSpan) montoTotalSpan.textContent = parseFloat(data.monto_total).toFixed(2);
                        if (saldoPendienteSpan) saldoPendienteSpan.textContent = parseFloat(data.saldo_pendiente).toFixed(2);
                        if (infoContrato) infoContrato.style.display = 'block';
                        
                        if (montoPago) montoPago.max = data.saldo_pendiente;
                    }
                } catch (err) {
                    console.error("Error al obtener la información del contrato:", err);
                }
            } else {
                if (infoContrato) infoContrato.style.display = 'none';
            }
        });
    }

    if (montoPago) {
        montoPago.addEventListener('blur', function() { validarCosto(this); });
    }

    const fechaPago = document.querySelector('#formRegistrarPago [name="fecha_pago"]');
    if (fechaPago) {
        fechaPago.addEventListener('blur', function() { validarFecha(this); });
    }
    const horaPago = document.querySelector('#formRegistrarPago [name="hora_pago"]');
    if (horaPago) {
        horaPago.addEventListener('blur', function() { validarHora(this); });
    }

    // Delegación de Eventos: Botón Editar Pago
    document.addEventListener('click', async function(e) {
        const btn = e.target.closest('.btn-editar-pago');
        if (btn) {
            const pagoId = btn.getAttribute('data-id');
            try {
                const response = await fetch(`/balance/api/pago/${pagoId}`);
                const data = await response.json();
                
                if (document.getElementById('edit_pago_id')) document.getElementById('edit_pago_id').value = data.id_pago;
                if (document.getElementById('edit_monto')) document.getElementById('edit_monto').value = data.monto;
                if (document.getElementById('edit_tipo_pago')) document.getElementById('edit_tipo_pago').value = data.tipo_pago;
                if (document.getElementById('edit_referencia')) document.getElementById('edit_referencia').value = data.referencia || '';
                
                // Ejecutar la alternancia justo después de cargar los datos en la edición
                if (selectTipoPagoEdit) {
                    alternarReferencia(selectTipoPagoEdit, 'edit_referencia');
                }

                const inputFecha = document.getElementById('edit_fecha_pago');
                if (inputFecha && data.fecha_pago) {
                    let fechaFormateada = data.fecha_pago.includes('/') 
                        ? data.fecha_pago.split('/').reverse().join('-') 
                        : data.fecha_pago;
                    inputFecha.value = fechaFormateada;
                }
                
                const inputHora = document.getElementById('edit_hora_pago');
                if (inputHora) inputHora.value = data.hora_pago || '';

                const inputNotas = document.getElementById('edit_notes') || document.getElementById('edit_notas');
                if (inputNotas) inputNotas.value = data.descripcion || '';
                
                const modalEl = document.getElementById('modalEditarPago');
                if (modalEl) {
                    new bootstrap.Modal(modalEl).show();
                }
            } catch (err) {
                console.error("Error al obtener datos del pago:", err);
            }
        }
    });

    // Delegación de Eventos: Botón Eliminar Pago
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.btn-eliminar-pago');
        if (btn) {
            const pagoId = btn.getAttribute('data-id');
            Swal.fire({
                title: '¿Eliminar pago?',
                text: 'Esta acción no se puede deshacer y recalculará los saldos.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#dc3545',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    const form = document.createElement('form');
                    form.method = 'POST';
                    form.action = `/balance/eliminar-pago/${pagoId}`;

                    const csrfInput = document.createElement('input');
                    csrfInput.type = 'hidden';
                    csrfInput.name = 'csrf_token';
                    csrfInput.value = document.querySelector('input[name="csrf_token"]')?.value || '';

                    form.appendChild(csrfInput);
                    document.body.appendChild(form);
                    form.submit();
                }
            });
        }
    });

    // Envío y Validación del Formulario de Registro
    const formRegistrar = document.getElementById('formRegistrarPago');
    if (formRegistrar) {
        formRegistrar.addEventListener('submit', function(e) {
            const valContrato = validarSelect(selectContrato);
            const valMonto = validarCosto(montoPago);
            const fechaPago = document.querySelector('#formRegistrarPago [name="fecha_pago"]');
            const horaPago = document.querySelector('#formRegistrarPago [name="hora_pago"]');
            
            const valFecha = fechaPago ? validarFecha(fechaPago) : true;
            const valHora = horaPago ? validarHora(horaPago) : true;

            if (!valContrato || !valMonto || !valFecha || !valHora) {
                e.preventDefault();
                Swal.fire({
                    title: 'Error de validación',
                    text: 'Corrige los campos marcados en rojo antes de guardar.',
                    icon: 'error',
                    confirmButtonColor: '#3085d6'
                });
                return;
            }

            e.preventDefault();
            Swal.fire({
                title: '¿Registrar pago?',
                text: 'Se registrará un nuevo pago en el sistema.',
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#198754',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, registrar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    formRegistrar.submit();
                }
            });
        });
    }

    // Envío y Validación del Formulario de Edición
    const formEditar = document.getElementById('formEditarPago');
    if (formEditar) {
        formEditar.addEventListener('submit', function(e) {
            const editMonto = document.getElementById('edit_monto');
            const editFecha = document.getElementById('edit_fecha_pago');
            const editHora = document.getElementById('edit_hora_pago');

            const valMonto = editMonto ? validarCosto(editMonto) : true;
            const valFecha = editFecha ? validarFecha(editFecha) : true;
            const valHora = editHora ? validarHora(editHora) : true;

            if (!valMonto || !valFecha || !valHora) {
                e.preventDefault();
                Swal.fire({
                    title: 'Error de validación',
                    text: 'Asegúrate de que los datos modificados sean válidos.',
                    icon: 'error',
                    confirmButtonColor: '#3085d6'
                });
                return;
            }

            e.preventDefault();
            Swal.fire({
                title: '¿Guardar cambios?',
                text: 'Se actualizarán los datos de este pago.',
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#198754',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, guardar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    formEditar.submit();
                }
            });
        });
    }

    // Filtros por chips para el Grid de Contratos
    document.querySelectorAll('.filter-chip').forEach(chip => {
        chip.addEventListener('click', function() {
            document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            
            const filter = this.getAttribute('data-filter');
            document.querySelectorAll('.contract-item').forEach(item => {
                if (filter === 'all') {
                    item.style.display = '';
                } else {
                    item.style.display = item.getAttribute('data-status') === filter ? '' : 'none';
                }
            });
        });
    });
});