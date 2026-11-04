import { validarNombre, validarTiempoInning, quitarInvalido } from './validacion.js';

function getCSRF() {
    return document.querySelector('input[name="csrf_token"]').value;
}

document.addEventListener('DOMContentLoaded', function() {
    initCalendar();
    initElementoForm();
    initDeleteConfirmations();
    initGuionForm();
});

function initGuionForm() {
    const guionForm = document.getElementById('guionForm');
    if (!guionForm) return;

    const esReplicar = document.getElementById('fechas') !== null;
    const action = esReplicar ? 'replicar' : 'crear';

    const nombreInput = document.getElementById('nombre_base') || document.getElementById('nombre');
    if (nombreInput) {
        nombreInput.addEventListener('input', function() { validarNombre(this); });
        nombreInput.addEventListener('blur', function() { validarNombre(this); });
    }

    const nombreDuplicado = document.getElementById('nombre');
    if (nombreDuplicado) {
        nombreDuplicado.addEventListener('blur', async function() {
            const idInput = document.getElementById('id');
            if (idInput && idInput.value) return;
            const nombre = this.value.trim();
            if (!nombre || !validarNombre(this)) return;
            const res = await fetch('/guiones/verificar-nombre', {
                method: 'POST',
                body: new URLSearchParams({ nombre: nombre, csrf_token: getCSRF() })
            });
            const data = await res.json();
            if (data.error) return;
            const feedback = this.parentElement.querySelector('.invalid-feedback');
            if (data.existe) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
                if (feedback) feedback.textContent = 'Este nombre ya existe en la base de datos';
            } else if (this.classList.contains('is-invalid')) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
                if (feedback) feedback.textContent = '';
            }
        });
    }

    const tiempoInput = document.getElementById('tiempo_inning');
    if (tiempoInput) {
        tiempoInput.addEventListener('input', function() { validarTiempoInning(this); });
        tiempoInput.addEventListener('blur', function() { validarTiempoInning(this); });
    }

    guionForm.addEventListener('submit', function(e) {
        if (typeof updateDisplay === 'function') updateDisplay();
        const nombre = document.getElementById('nombre') || document.getElementById('nombre_base');
        if (nombre && !validarNombre(nombre)) {
            e.preventDefault();
            Swal.fire({
                title: 'Error de validación',
                text: 'El nombre debe tener al menos 2 caracteres.',
                icon: 'error',
                confirmButtonColor: '#3085d6'
            });
            return;
        }
        if (typeof selectedDates !== 'undefined' && selectedDates.length === 0) {
            e.preventDefault();
            Swal.fire({
                title: 'Fechas requeridas',
                text: 'Debes seleccionar al menos una fecha.',
                icon: 'warning',
                confirmButtonColor: '#3085d6'
            });
            return;
        }

        e.preventDefault();
        Swal.fire({
            title: esReplicar ? '¿Replicar guión?' : '¿Crear guión?',
            text: esReplicar ? 'Se duplicará el guión en las fechas seleccionadas.' : 'Se creará un nuevo guión en el sistema.',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#198754',
            cancelButtonColor: '#6c757d',
            confirmButtonText: esReplicar ? 'Sí, replicar' : 'Sí, crear',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                HTMLFormElement.prototype.submit.call(guionForm);
            }
        });
    });
}

function initCalendar() {
    const modalEl = document.getElementById('calendarModal');
    if (!modalEl) return;

    let selectedDates = [];
    if (typeof window.existingFechas !== 'undefined' && window.existingFechas.length) {
        selectedDates = [...window.existingFechas];
    }
    let currentDate = new Date();
    let currentMonth = currentDate.getMonth();
    let currentYear = currentDate.getFullYear();
    
    const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                       'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    
    const modal = new bootstrap.Modal(modalEl);
    
    document.getElementById('openCalendar')?.addEventListener('click', function() {
        renderCalendar();
        modal.show();
    });
    
    function renderCalendar() {
        document.getElementById('monthYear').textContent = `${monthNames[currentMonth]} ${currentYear}`;
        
        const firstDay = new Date(currentYear, currentMonth, 1).getDay();
        const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
        const today = new Date();
        
        let html = '';
        
        for (let i = 0; i < firstDay; i++) {
            html += '<div class="calendar-day empty"></div>';
        }
        
        for (let day = 1; day <= daysInMonth; day++) {
            const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const isSelected = selectedDates.includes(dateStr);
            const isToday = (day === today.getDate() && 
                           currentMonth === today.getMonth() && 
                           currentYear === today.getFullYear());
            
            let classes = 'calendar-day';
            if (isSelected) classes += ' selected';
            if (isToday) classes += ' today';
            
            html += `<div class="${classes}" data-date="${dateStr}">${day}</div>`;
        }
        
        document.getElementById('calendarDays').innerHTML = html;
        document.getElementById('selectedCount').textContent = `${selectedDates.length} fecha${selectedDates.length !== 1 ? 's' : ''}`;
        
        document.querySelectorAll('.calendar-day:not(.empty)').forEach(dayEl => {
            dayEl.addEventListener('click', function() {
                const date = this.dataset.date;
                const index = selectedDates.indexOf(date);
                
                if (index > -1) {
                    selectedDates.splice(index, 1);
                } else {
                    selectedDates.push(date);
                }
                
                renderCalendar();
                updateDisplay();
            });
        });
    }
    
    function updateDisplay() {
        const display = document.getElementById('fechasDisplay');
        const hidden = document.getElementById('fechas');
        
        if (selectedDates.length === 0) {
            if (display) display.value = '';
            if (hidden) hidden.value = '';
        } else {
            const sorted = [...selectedDates].sort();
            if (display) {
                display.value = sorted.map(d => {
                    const parts = d.split('-');
                    return `${parts[2]}/${parts[1]}/${parts[0]}`;
                }).join(', ');
            }
            if (hidden) {
                hidden.value = sorted.join(',');
            }
        }
    }
    
    document.getElementById('prevMonth')?.addEventListener('click', function() {
        currentMonth--;
        if (currentMonth < 0) { currentMonth = 11; currentYear--; }
        renderCalendar();
    });
    
    document.getElementById('nextMonth')?.addEventListener('click', function() {
        currentMonth++;
        if (currentMonth > 11) { currentMonth = 0; currentYear++; }
        renderCalendar();
    });
    
    modalEl.addEventListener('hidden.bs.modal', function() {
        updateDisplay();
    });
    
    window.updateDisplay = updateDisplay;
    window.selectedDates = selectedDates;
    
    updateDisplay();
}

function initElementoForm() {
    const tipoSelect = document.getElementById('tipoSelect');
    const pregameFields = document.getElementById('pregameFields');
    const gameFields = document.getElementById('gameFields');
    const horaInput = document.getElementById('horaInput');
    const inningSelect = document.getElementById('inningSelect');
    const medioSelect = document.getElementById('medioSelect');
    const horaWarning = document.getElementById('horaWarning');
    const inningWarning = document.getElementById('inningWarning');
    const horasUsadas = window.horasUsadas || [];
    const inningsUsados = window.inningsUsados || {};
    const editingId = window.editingElementId || null;
    const duracionInput = document.getElementById('duracion_estimada');
    const tiempoInning = window.tiempoInning || null;
    
    function autoFillDuracion() {
        if (!duracionInput || !tiempoInning) return;
        const mins = Math.floor(tiempoInning / 60);
        const secs = tiempoInning % 60;
        duracionInput.value = mins + ',' + (secs > 0 ? secs : '0');
        duracionInput.readOnly = true;
    }
    
    function toggleFields() {
        const tipo = tipoSelect ? tipoSelect.value : 'pregame';
        if (tipo === 'game') {
            if (pregameFields) pregameFields.style.display = 'none';
            if (gameFields) gameFields.style.display = 'block';
            autoFillDuracion();
        } else {
            if (pregameFields) pregameFields.style.display = 'block';
            if (gameFields) gameFields.style.display = 'none';
            if (duracionInput) duracionInput.readOnly = false;
        }
        checkConflictos();
    }
    
    function checkConflictos() {
        const tipo = tipoSelect ? tipoSelect.value : 'pregame';
        if (horaWarning) horaWarning.style.display = 'none';
        if (inningWarning) inningWarning.style.display = 'none';
        
        if (tipo === 'pregame' && horaInput && horaInput.value) {
            if (horasUsadas.includes(horaInput.value) && !isEditingHora(horaInput.value)) {
                if (horaWarning) horaWarning.style.display = 'block';
                horaInput.classList.add('is-invalid');
            } else {
                horaInput.classList.remove('is-invalid');
            }
        }
        
        if (tipo === 'game' && inningSelect && inningSelect.value && medioSelect && medioSelect.value) {
            const clave = inningSelect.value + '-' + medioSelect.value;
            if (inningsUsados[clave] && inningsUsados[clave] !== editingId) {
                if (inningWarning) inningWarning.style.display = 'block';
                if (inningSelect) inningSelect.classList.add('is-invalid');
                if (medioSelect) medioSelect.classList.add('is-invalid');
            } else {
                if (inningSelect) inningSelect.classList.remove('is-invalid');
                if (medioSelect) medioSelect.classList.remove('is-invalid');
            }
        }
    }
    
    function isEditingHora(hora) {
        if (!editingId) return false;
        var form = document.getElementById('elementoForm');
        if (!form) return false;
        var currentHora = form.querySelector('input[name="hora"]');
        return currentHora && currentHora.value === hora;
    }
    
    if (tipoSelect) {
        tipoSelect.addEventListener('change', toggleFields);
    }
    if (horaInput) {
        horaInput.addEventListener('change', checkConflictos);
        horaInput.addEventListener('input', checkConflictos);
    }
    if (inningSelect) {
        inningSelect.addEventListener('change', checkConflictos);
    }
    if (medioSelect) {
        medioSelect.addEventListener('change', checkConflictos);
    }
    
    var form = document.getElementById('elementoForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            var tipo = tipoSelect ? tipoSelect.value : 'pregame';
            
            if (tipo === 'pregame' && (!horaInput || !horaInput.value)) {
                e.preventDefault();
                Swal.fire({
                    title: 'Error',
                    text: 'Debes indicar una hora para Pre-Game',
                    icon: 'warning',
                    confirmButtonColor: '#3085d6'
                });
                return;
            }
            
            if (tipo === 'game' && (!inningSelect || !inningSelect.value || !medioSelect || !medioSelect.value)) {
                e.preventDefault();
                Swal.fire({
                    title: 'Error',
                    text: 'Debes seleccionar inning y medio para Game',
                    icon: 'warning',
                    confirmButtonColor: '#3085d6'
                });
                return;
            }

            e.preventDefault();
            var submitter = e.submitter;
            const esEditar = window.editingElementId !== undefined && window.editingElementId !== null;
            Swal.fire({
                title: esEditar ? '¿Guardar cambios?' : '¿Agregar elemento?',
                text: esEditar ? 'Se actualizarán los datos de este elemento.' : 'Se agregará un nuevo elemento al guión.',
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#198754',
                cancelButtonColor: '#6c757d',
                confirmButtonText: esEditar ? 'Sí, guardar' : 'Sí, agregar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    if (submitter) {
                        var input = document.createElement('input');
                        input.type = 'hidden';
                        input.name = submitter.name;
                        input.value = submitter.value;
                        form.appendChild(input);
                    }
                    HTMLFormElement.prototype.submit.call(form);
                }
            });
        });
    }
    
    toggleFields();
}

function initDeleteConfirmations() {
    document.querySelectorAll('a[data-confirm]').forEach(function(link) {
        const mensaje = link.getAttribute('data-confirm');
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            Swal.fire({
                title: 'Confirmar',
                text: mensaje,
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#dc3545',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = href;
                }
            });
        });
    });
}
