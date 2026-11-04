function getCSRF() {
    const el = document.querySelector('input[name="csrf_token"]');
    return el ? el.value : '';
}

function renderTipos(tipos) {
    const tbody = document.getElementById('tbodyTipos');
    if (!tipos.length) {
        tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted py-3">No hay tipos registrados</td></tr>';
        return;
    }
    tbody.innerHTML = tipos.map(t => `
        <tr>
            <td class="fw-semibold">${escHtml(t.nombre)}</td>
            <td class="text-muted">${escHtml(t.descripcion || '—')}</td>
            <td class="text-center">
                <button class="btn btn-sm btn-warning me-1 btn-editar-tipo" data-id="${t.id}" data-nombre="${escHtml(t.nombre)}" data-descripcion="${escHtml(t.descripcion || '')}" title="Editar">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger btn-eliminar-tipo" data-id="${t.id}" data-nombre="${escHtml(t.nombre)}" title="Eliminar">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function escHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

async function cargarTipos() {
    try {
        const res = await fetch('/inventario/api/tipos', {
            headers: { 'X-CSRFToken': getCSRF() }
        });
        const tipos = await res.json();
        renderTipos(tipos);
    } catch (e) {
        document.getElementById('tbodyTipos').innerHTML = '<tr><td colspan="3" class="text-center text-danger py-3">Error al cargar tipos</td></tr>';
    }
}

function resetForm() {
    document.getElementById('tipoId').value = '';
    document.getElementById('tipoNombre').value = '';
    document.getElementById('tipoDescripcion').value = '';
    document.getElementById('tipoNombre').classList.remove('is-invalid');
    document.getElementById('tituloFormTipo').innerHTML = '<i class="fas fa-plus-circle me-1 text-success"></i> Nuevo Tipo';
    document.getElementById('btnGuardarTipo').innerHTML = '<i class="fas fa-save me-1"></i> Guardar';
    document.getElementById('btnCancelarTipo').style.display = 'none';
}

function editarTipo(id, nombre, descripcion) {
    document.getElementById('tipoId').value = id;
    document.getElementById('tipoNombre').value = nombre;
    document.getElementById('tipoDescripcion').value = descripcion;
    document.getElementById('tipoNombre').classList.remove('is-invalid');
    document.getElementById('tituloFormTipo').innerHTML = '<i class="fas fa-edit me-1 text-warning"></i> Editar Tipo';
    document.getElementById('btnGuardarTipo').innerHTML = '<i class="fas fa-save me-1"></i> Actualizar';
    document.getElementById('btnCancelarTipo').style.display = 'inline-block';
    document.getElementById('tipoNombre').focus();
}

document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('modalTipos');
    if (!modal) return;

    modal.addEventListener('show.bs.modal', cargarTipos);
    modal.addEventListener('hidden.bs.modal', resetForm);

    document.getElementById('btnNuevoTipo').addEventListener('click', resetForm);

    document.getElementById('btnCancelarTipo').addEventListener('click', resetForm);

    document.getElementById('tbodyTipos').addEventListener('click', async function (e) {
        const btn = e.target.closest('button');
        if (!btn) return;

        if (btn.classList.contains('btn-editar-tipo')) {
            editarTipo(btn.dataset.id, btn.dataset.nombre, btn.dataset.descripcion);
        }

        if (btn.classList.contains('btn-eliminar-tipo')) {
            const result = await Swal.fire({ title: '¿Eliminar tipo?', text: `¿Eliminar el tipo "${btn.dataset.nombre}"?`, icon: 'warning', showCancelButton: true, confirmButtonColor: '#dc3545', confirmButtonText: 'Eliminar', cancelButtonText: 'Cancelar' });
            if (!result.isConfirmed) return;
            try {
                const res = await fetch(`/inventario/api/tipos/eliminar/${btn.dataset.id}`, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCSRF() }
                });
                const data = await res.json();
                if (data.success) {
                    await Swal.fire({ icon: 'success', title: 'Tipo eliminado', text: `"${btn.dataset.nombre}" eliminado`, timer: 2000, showConfirmButton: false });
                    cargarTipos();
                } else {
                    Swal.fire({ icon: 'error', title: 'Error', text: data.errores.join(', ') });
                }
            } catch (e) {
                Swal.fire({ icon: 'error', title: 'Error', text: 'Error al eliminar tipo' });
            }
        }
    });

    document.getElementById('formTipo').addEventListener('submit', async function (e) {
        e.preventDefault();
        const nombre = document.getElementById('tipoNombre').value.trim();
        const descripcion = document.getElementById('tipoDescripcion').value.trim();
        const id = document.getElementById('tipoId').value;

        if (!nombre) {
            document.getElementById('tipoNombre').classList.add('is-invalid');
            return;
        }
        document.getElementById('tipoNombre').classList.remove('is-invalid');

        const esCreacion = !id;
        const confirm = await Swal.fire({
            title: esCreacion ? '¿Crear tipo?' : '¿Guardar cambios?',
            text: esCreacion ? `Crear tipo "${nombre}"` : `Actualizar tipo "${nombre}"`,
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: esCreacion ? '#28a745' : '#ffc107',
            confirmButtonText: esCreacion ? 'Crear' : 'Actualizar',
            cancelButtonText: 'Cancelar'
        });
        if (!confirm.isConfirmed) return;

        const url = id ? `/inventario/api/tipos/editar/${id}` : '/inventario/api/tipos/crear';
        const formData = new URLSearchParams();
        formData.append('nombre', nombre);
        formData.append('descripcion', descripcion);

        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCSRF()
                },
                body: formData
            });
            const data = await res.json();
            if (data.success) {
                await Swal.fire({
                    icon: 'success',
                    title: esCreacion ? 'Tipo creado' : 'Tipo actualizado',
                    text: `"${nombre}" ${esCreacion ? 'creado' : 'actualizado'} correctamente`,
                    timer: 2000,
                    showConfirmButton: false
                });
                resetForm();
                cargarTipos();
            } else {
                Swal.fire({ icon: 'error', title: 'Error', text: data.errores.join(', ') });
            }
        } catch (err) {
            Swal.fire({ icon: 'error', title: 'Error', text: 'Error al guardar tipo' });
        }
    });
});
