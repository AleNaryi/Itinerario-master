import { validarNombre, validarSelect } from './validacion.js';

function getCSRF() {
    const el = document.querySelector('input[name="csrf_token"]');
    return el ? el.value : '';
}

function escHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function recargarTodo() {
    const params = new URLSearchParams();
    params.append('accion', 'consultar');
    params.append('csrf_token', getCSRF());
    fetch('/premio/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRF() },
        body: params
    })
    .then(r => r.json())
    .then(data => {
        if (data.pendientes) {
            renderCatalogo(data.pendientes);
            document.getElementById('kpi-pendientes').textContent = data.pendientes.length;
        }
        if (data.entregados) {
            renderSalidas(data.entregados);
            document.getElementById('kpi-entregados').textContent = data.entregados.length;
        }
    });
}

function renderCatalogo(pendientes) {
    const contenedor = document.getElementById('contenedor-catalogo');
    const vacio = document.getElementById('catalogo-vacio');
    if (!contenedor) return;
    if (!pendientes.length) {
        contenedor.innerHTML = '';
        vacio.classList.remove('d-none');
        return;
    }
    vacio.classList.add('d-none');
    contenedor.innerHTML = pendientes.map(p => {
        const foto = p.foto && p.foto !== 'default-premio.png'
            ? `<div style="height:130px;overflow:hidden;border-radius:12px 12px 0 0;"><img src="/static/uploads/premios/${escHtml(p.foto)}" style="width:100%;height:100%;object-fit:cover;" alt="${escHtml(p.nombre)}" onerror="this.parentElement.innerHTML='<div class=d-flex align-items-center justify-content-center bg-light style=height:130px><i class=fas fa-box-open fa-2x text-muted opacity-25></i></div>'"></div>`
            : '<div class="d-flex align-items-center justify-content-center bg-light" style="height:130px;border-radius:12px 12px 0 0;"><i class="fas fa-box-open fa-2x text-muted opacity-25"></i></div>';
        const restante = (p.cantidad || 1) - (p.cantidad_entregada || 0);
        return `<div class="col tarjeta-item-pos" data-nombre="${escHtml(p.nombre.toLowerCase())}">
            <div class="card h-100 premio-card border-0 position-relative" style="cursor:pointer;"
                 data-id="${p.id}" data-nombre="${escHtml(p.nombre)}"
                 data-patrocinador-id="${p.id_patrocinador || ''}"
                 data-patrocinador-nombre="${escHtml(p.patrocinador_nombre || '')}"
                 data-descripcion="${escHtml(p.descripcion || '')}"
                 data-foto="${escHtml(p.foto || '')}"
                 data-cantidad="${p.cantidad || 1}" data-cantidad-entregada="${p.cantidad_entregada || 0}">
                <div class="position-absolute top-0 end-0 m-2 d-flex gap-1" style="z-index:10;">
                    <button type="button" class="btn btn-action btn-action-edit btn-editar-premio" data-id="${p.id}" title="Editar"><i class="fas fa-pen"></i></button>
                    <button type="button" class="btn btn-action btn-action-danger btn-eliminar-premio" data-id="${p.id}" data-nombre="${escHtml(p.nombre)}" title="Eliminar"><i class="fas fa-trash"></i></button>
                </div>
                ${foto}
                <div class="card-body p-3">
                    <h6 class="fw-bold text-dark mb-1 text-truncate" style="font-size:0.88rem;" title="${escHtml(p.nombre)}">${escHtml(p.nombre)}</h6>
                    <p class="text-muted small mb-1 text-truncate" style="font-size:0.75rem;"><i class="fas fa-building me-1"></i>${escHtml(p.patrocinador_nombre || 'Stock Libre')}</p>
                    <span class="badge bg-info bg-opacity-10 text-info mb-2" style="font-size:0.7rem;"><i class="fas fa-cube me-1"></i>Disponibles: ${restante} / ${p.cantidad || 1}</span>
                    <button type="button" class="btn btn-action btn-action-success btn-entregar-premio w-100"
                            data-id="${p.id}" data-nombre="${escHtml(p.nombre)}" data-foto="${escHtml(p.foto || '')}"
                            data-patrocinador-id="${p.id_patrocinador || ''}"
                            data-cantidad="${p.cantidad || 1}" data-cantidad-entregada="${p.cantidad_entregada || 0}">
                        <i class="fas fa-truck me-1"></i>Entregar
                    </button>
                </div>
            </div>
        </div>`;
    }).join('');
}

function renderSalidas(entregados) {
    const tbody = document.getElementById('tabla-salidas');
    if (!tbody) return;
    if (!entregados.length) {
        tbody.closest('.table-responsive').insertAdjacentHTML('afterend',
            '<div class="text-center py-5 text-muted" id="salidas-vacio"><i class="fas fa-inbox fa-3x mb-3 opacity-25"></i><p class="mb-0">No hay entregas registradas</p></div>');
        tbody.closest('.table-responsive').remove();
        return;
    }
    const oldVacio = document.getElementById('salidas-vacio');
    if (oldVacio) oldVacio.remove();

    tbody.innerHTML = entregados.map(p => {
        const foto = p.foto && p.foto !== 'default-premio.png'
            ? `<img src="/static/uploads/premios/${escHtml(p.foto)}" style="width:40px;height:40px;object-fit:cover;border-radius:8px;" alt="${escHtml(p.nombre)}" onerror="this.style.display='none'">`
            : '<div class="bg-light d-flex align-items-center justify-content-center" style="width:40px;height:40px;border-radius:8px;"><i class="fas fa-image text-muted opacity-25"></i></div>';
        const fecha = p.fecha_entrega ? new Date(p.fecha_entrega).toLocaleString('es', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—';
        return `<tr>
            <td class="fw-semibold">${escHtml(p.nombre)}</td>
            <td>${foto}</td>
            <td>${escHtml(p.patrocinador_nombre || '—')}</td>
            <td><span class="badge bg-secondary">${p.cantidad_entregada || 1} / ${p.cantidad || 1}</span></td>
            <td>${escHtml(p.entregado_por || '—')}</td>
            <td class="text-muted small">${fecha}</td>
            <td>
                <button type="button" class="btn btn-action btn-action-primary btn-ver-entrega"
                    data-nombre="${escHtml(p.nombre)}" data-foto="${escHtml(p.foto || '')}"
                    data-patrocinador="${escHtml(p.patrocinador_nombre || '')}"
                    data-usuario="${escHtml(p.entregado_por || '')}"
                    data-fecha="${fecha}"
                    data-descripcion="${escHtml(p.descripcion || 'Sin notas registradas.')}"
                    data-cantidad="${p.cantidad_entregada || 1}"
                    title="Ver detalle"><i class="fas fa-eye"></i></button>
            </td>
        </tr>`;
    }).join('');
}

/* === Abrir modal crear === */
function abrirCrear() {
    document.getElementById('modalTitle').innerHTML = '<i class="fas fa-gift me-2"></i>Registrar Premio';
    document.getElementById('btnAccion').innerHTML = '<i class="fas fa-save me-1"></i>Guardar';
    document.getElementById('accion-premio').value = 'registrar';
    document.getElementById('premio-id').value = '';
    document.getElementById('formPremio').reset();
    document.getElementById('premio-cantidad').value = 1;
    document.getElementById('foto-actual-container').style.display = 'none';
    const preview = document.getElementById('foto-preview-container');
    if (preview) preview.style.display = 'none';
    const btnTomar = document.getElementById('btn-tomar-foto');
    const btnExaminar = document.getElementById('btn-examinar-foto');
    if (btnTomar) btnTomar.style.display = '';
    if (btnExaminar) btnExaminar.style.display = '';
    const modal = new bootstrap.Modal(document.getElementById('modalPremio'));
    modal.show();
}

/* === Abrir modal editar === */
function abrirEditar(id) {
    const params = new URLSearchParams();
    params.append('accion', 'obtener');
    params.append('id', id);
    params.append('csrf_token', getCSRF());
    fetch('/premio/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRF() },
        body: params
    })
    .then(r => r.json())
    .then(p => {
        if (p.error) { Swal.fire('Error', p.error, 'error'); return; }
        document.getElementById('modalTitle').innerHTML = '<i class="fas fa-edit me-2"></i>Editar Premio';
        document.getElementById('btnAccion').innerHTML = '<i class="fas fa-save me-1"></i>Actualizar';
        document.getElementById('accion-premio').value = 'editar';
        document.getElementById('premio-id').value = p.id;
        document.getElementById('premio-nombre').value = p.nombre;
        document.getElementById('premio-descripcion').value = p.descripcion || '';
        document.getElementById('premio-cantidad').value = p.cantidad || 1;

        const selectPat = document.getElementById('premio-patrocinador');
        for (let i = 0; i < selectPat.options.length; i++) {
            if (selectPat.options[i].value == p.id_patrocinador) {
                selectPat.selectedIndex = i;
                break;
            }
        }

        const fotoContainer = document.getElementById('foto-actual-container');
        if (p.foto && p.foto !== 'default-premio.png') {
            document.getElementById('foto-actual-img').src = '/static/uploads/premios/' + p.foto;
            fotoContainer.style.display = 'block';
        } else {
            fotoContainer.style.display = 'none';
        }

        const preview = document.getElementById('foto-preview-container');
        if (preview) { preview.style.display = 'none'; document.getElementById('foto-preview-img').src = ''; }
        const btnTomar = document.getElementById('btn-tomar-foto');
        const btnExaminar = document.getElementById('btn-examinar-foto');
        if (btnTomar) btnTomar.style.display = '';
        if (btnExaminar) btnExaminar.style.display = '';

        const modal = new bootstrap.Modal(document.getElementById('modalPremio'));
        modal.show();
    })
    .catch(err => console.error('Error:', err));
}

/* === Abrir modal entregar === */
function abrirEntregar(id, nombre, foto, patId, cantidad, cantidadEntregada) {
    document.getElementById('entrega-id-premio').value = id;
    document.getElementById('entrega-nombre-premio').textContent = '🎁 ' + nombre;

    const fotoContainer = document.getElementById('entrega-foto-container');
    const fotoImg = document.getElementById('entrega-foto-img');
    if (foto && foto !== 'default-premio.png') {
        fotoImg.src = '/static/uploads/premios/' + foto;
        fotoContainer.style.display = 'block';
    } else {
        fotoContainer.style.display = 'none';
    }

    const selectPat = document.getElementById('entrega-patrocinador');
    selectPat.value = patId || '';

    const restante = (cantidad || 1) - (cantidadEntregada || 0);
    const cantidadInput = document.getElementById('entrega-cantidad');
    cantidadInput.max = restante;
    cantidadInput.value = 1;
    document.getElementById('entrega-cantidad-info').textContent = `Disponibles: ${restante}`;

    document.getElementById('entrega-descripcion').value = '';

    const modal = new bootstrap.Modal(document.getElementById('modalEntrega'));
    modal.show();
}

/* === Event delegation === */
document.addEventListener('click', function(e) {
    const btnEditar = e.target.closest('.btn-editar-premio');
    if (btnEditar) {
        e.stopPropagation();
        const id = btnEditar.dataset.id;
        Swal.fire({
            title: 'Editar Premio',
            text: '¿Deseas editar este premio?',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#198754',
            confirmButtonText: 'Sí, editar',
            cancelButtonText: 'Cancelar'
        }).then(result => { if (result.isConfirmed) abrirEditar(id); });
        return;
    }

    const btnEliminar = e.target.closest('.btn-eliminar-premio');
    if (btnEliminar) {
        e.stopPropagation();
        const id = btnEliminar.dataset.id;
        const nombre = btnEliminar.dataset.nombre;
        Swal.fire({
            title: '¿Eliminar premio?',
            html: `¿Estás seguro de eliminar <strong>${escHtml(nombre)}</strong>?`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        }).then(result => {
            if (result.isConfirmed) {
                const params = new URLSearchParams();
                params.append('accion', 'eliminar');
                params.append('id', id);
                params.append('csrf_token', getCSRF());
                fetch('/premio/', {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCSRF() },
                    body: params
                })
                .then(r => r.json())
                .then(data => {
                    if (data.error) { Swal.fire('Error', data.error, 'error'); return; }
                    Swal.fire({ icon: 'success', title: 'Eliminado', text: data.mensaje, timer: 1500, showConfirmButton: false });
                    recargarTodo();
                });
            }
        });
        return;
    }

    const btnEntregar = e.target.closest('.btn-entregar-premio');
    if (btnEntregar) {
        e.stopPropagation();
        const id = btnEntregar.dataset.id;
        const nombre = btnEntregar.dataset.nombre;
        const foto = btnEntregar.dataset.foto;
        const patId = btnEntregar.dataset.patrocinadorId;
        const cantidad = parseInt(btnEntregar.dataset.cantidad) || 1;
        const cantidadEntregada = parseInt(btnEntregar.dataset.cantidadEntregada) || 0;
        const restante = cantidad - cantidadEntregada;
        if (restante <= 0) {
            Swal.fire('Sin stock', 'No hay unidades disponibles para entregar.', 'info');
            return;
        }
        Swal.fire({
            title: '¿Procesar entrega?',
            html: `Se entregará <strong>${escHtml(nombre)}</strong>`,
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#198754',
            confirmButtonText: 'Sí, entregar',
            cancelButtonText: 'Cancelar'
        }).then(result => {
            if (result.isConfirmed) abrirEntregar(id, nombre, foto, patId, cantidad, cantidadEntregada);
        });
        return;
    }

    const btnVer = e.target.closest('.btn-ver-entrega');
    if (btnVer) {
        e.stopPropagation();
        const nombre = btnVer.dataset.nombre;
        const foto = btnVer.dataset.foto;
        const patrocinador = btnVer.dataset.patrocinador;
        const usuario = btnVer.dataset.usuario;
        const fecha = btnVer.dataset.fecha;
        const descripcion = btnVer.dataset.descripcion;

        document.getElementById('ver-nombre').textContent = '🎁 ' + nombre;

        const fotoContainer = document.getElementById('ver-foto-container');
        const fotoPlaceholder = document.getElementById('ver-foto-placeholder');
        const fotoImg = document.getElementById('ver-foto-img');
        if (foto && foto !== 'default-premio.png') {
            fotoImg.src = '/static/uploads/premios/' + foto;
            fotoContainer.style.display = 'block';
            fotoPlaceholder.style.display = 'none';
        } else {
            fotoContainer.style.display = 'none';
            fotoPlaceholder.style.display = 'block';
        }

        document.getElementById('ver-patrocinador').textContent = patrocinador || '—';
        document.getElementById('ver-usuario').textContent = usuario || '—';
        document.getElementById('ver-cantidad').textContent = btnVer.dataset.cantidad || '1';
        document.getElementById('ver-fecha').textContent = fecha || '—';
        document.getElementById('ver-descripcion').textContent = descripcion;

        const modal = new bootstrap.Modal(document.getElementById('modalVerEntrega'));
        modal.show();
    }
});

/* === Buscador === */
document.getElementById('pos-buscador').addEventListener('input', function(e) {
    const busqueda = e.target.value.toLowerCase();
    document.querySelectorAll('.tarjeta-item-pos').forEach(t => {
        const nombre = t.getAttribute('data-nombre');
        t.style.display = nombre.includes(busqueda) ? 'block' : 'none';
    });
});

/* === Submit forms === */
document.addEventListener('DOMContentLoaded', function() {
    const fotoInput = document.getElementById('premio-foto-input');
    const btnTomar = document.getElementById('btn-tomar-foto');
    const btnExaminar = document.getElementById('btn-examinar-foto');
    const previewContainer = document.getElementById('foto-preview-container');
    const previewImg = document.getElementById('foto-preview-img');
    const btnQuitar = document.getElementById('btn-quitar-foto');

    if (btnTomar && fotoInput) {
        btnTomar.addEventListener('click', function() {
            fotoInput.setAttribute('capture', 'environment');
            fotoInput.click();
        });
    }
    if (btnExaminar && fotoInput) {
        btnExaminar.addEventListener('click', function() {
            fotoInput.removeAttribute('capture');
            fotoInput.click();
        });
    }
    if (fotoInput) {
        fotoInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImg.src = e.target.result;
                    previewContainer.style.display = 'block';
                    if (btnTomar) btnTomar.style.display = 'none';
                    if (btnExaminar) btnExaminar.style.display = 'none';
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    if (btnQuitar) {
        btnQuitar.addEventListener('click', function() {
            fotoInput.value = '';
            previewContainer.style.display = 'none';
            previewImg.src = '';
            if (btnTomar) btnTomar.style.display = '';
            if (btnExaminar) btnExaminar.style.display = '';
        });
    }

    const nombreInput = document.getElementById('premio-nombre');
    if (nombreInput) {
        nombreInput.addEventListener('input', function() { validarNombre(this); });
        nombreInput.addEventListener('blur', function() { validarNombre(this); });
    }

    const patSelect = document.getElementById('premio-patrocinador');
    if (patSelect) {
        patSelect.addEventListener('change', function() { validarSelect(this); });
    }

    /* Botón "Registrar Nuevo Premio" */
    document.getElementById('btnNuevoPremio').addEventListener('click', function() {
        abrirCrear();
    });

    /* Form crear/editar */
    document.getElementById('formPremio').addEventListener('submit', function(e) {
        e.preventDefault();
        if (!validarNombre(nombreInput)) {
            Swal.fire('Error', 'El nombre debe tener al menos 2 caracteres.', 'error');
            return;
        }
        const cantidadInput = document.getElementById('premio-cantidad');
        const cantidad = parseInt(cantidadInput.value);
        if (!cantidad || cantidad < 1) {
            Swal.fire('Error', 'La cantidad debe ser al menos 1.', 'error');
            cantidadInput.focus();
            return;
        }
        const esEdicion = document.getElementById('accion-premio').value === 'editar';
        Swal.fire({
            title: esEdicion ? '¿Guardar cambios?' : '¿Crear premio?',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#198754',
            confirmButtonText: esEdicion ? 'Sí, guardar' : 'Sí, crear',
            cancelButtonText: 'Cancelar'
        }).then(result => {
            if (!result.isConfirmed) return;
            const fd = new FormData(this);
            fetch('/premio/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCSRF() },
                body: fd
            })
            .then(r => r.json())
            .then(data => {
                if (data.error) { Swal.fire('Error', data.error, 'error'); return; }
                bootstrap.Modal.getInstance(document.getElementById('modalPremio')).hide();
                Swal.fire({ icon: 'success', title: esEdicion ? 'Actualizado' : 'Creado', text: data.mensaje, timer: 1500, showConfirmButton: false });
                recargarTodo();
            });
        });
    });

    /* Form entregar */
    document.getElementById('formEntrega').addEventListener('submit', function(e) {
        e.preventDefault();
        const idPremio = document.getElementById('entrega-id-premio').value;
        const idPat = document.getElementById('entrega-patrocinador').value;
        const cantidadEntregar = parseInt(document.getElementById('entrega-cantidad').value);
        if (!idPremio || !idPat) {
            Swal.fire('Error', 'Selecciona un patrocinador.', 'error');
            return;
        }
        if (!cantidadEntregar || cantidadEntregar < 1) {
            Swal.fire('Error', 'La cantidad debe ser al menos 1.', 'error');
            return;
        }
        const fd = new FormData(this);
        fetch('/premio/', {
            method: 'POST',
            headers: { 'X-CSRFToken': getCSRF() },
            body: fd
        })
        .then(r => r.json())
        .then(data => {
            if (data.error) { Swal.fire('Error', data.error, 'error'); return; }
            bootstrap.Modal.getInstance(document.getElementById('modalEntrega')).hide();
            Swal.fire({ icon: 'success', title: 'Entregado', text: data.mensaje, timer: 1500, showConfirmButton: false });
            recargarTodo();
        });
    });
});
