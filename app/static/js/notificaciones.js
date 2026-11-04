/* Notificaciones in-app: campana global estilo red social.
   Fuente de verdad = servidor (/notificaciones/api); el socket solo avisa en vivo. */
(function () {
    var badge = document.getElementById('notifBadge');
    var lista = document.getElementById('notifLista');
    var btnTodas = document.getElementById('btnLeerTodas');
    var btnCampana = document.getElementById('btnNotificaciones');
    if (!badge || !lista || !btnCampana) return;

    function csrf() {
        var el = document.getElementById('globalCsrfToken');
        return el ? el.value : '';
    }

    var count = parseInt(badge.textContent, 10) || 0;

    function setCount(n) {
        count = Math.max(n, 0);
        badge.textContent = count > 99 ? '99+' : count;
        badge.hidden = count <= 0;
    }

    function fila(n) {
        var clase = 'notif-item' + (n.leida ? '' : ' sin-leer') + (n.tipo ? ' ' + n.tipo : '');
        return '<button type="button" class="' + clase + '" data-id="' + n.id + '" data-url="' + escapeHtml(n.url || '') + '">' +
            '<span class="ni-icono"><i class="fas ' + (n.icono || 'fa-bell') + '"></i></span>' +
            '<span class="ni-cuerpo">' +
            '<div class="ni-titulo">' + escapeHtml(n.titulo || '') + '</div>' +
            '<div class="ni-mensaje">' + escapeHtml(n.mensaje || '') + '</div>' +
            '<div class="ni-hace">' + escapeHtml(n.hace || '') + '</div>' +
            '</span></button>';
    }

    // los textos vienen del servidor propio; igual escapamos por hábito
    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, function (c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
        });
    }

    function render(items) {
        if (!items.length) {
            lista.innerHTML = '<div class="notif-empty"><i class="far fa-bell-slash me-1"></i>Sin notificaciones</div>';
            return;
        }
        lista.innerHTML = items.map(fila).join('');
    }

    function cargar() {
        fetch('/notificaciones/api')
            .then(function (r) { return r.json(); })
            .then(function (d) {
                setCount(d.count || 0);
                render(d.items || []);
            })
            .catch(function () { /* sin conexión: se reintenta al abrir la campana */ });
    }

    btnCampana.addEventListener('show.bs.dropdown', cargar);
    cargar();

    // clic en una notificación: marcar leída y navegar a su destino.
    // Navegar dentro de .finally(): si se navega de inmediato el navegador
    // cancela el POST y la notificación vuelve a aparecer sin leer.
    lista.addEventListener('click', function (e) {
        var item = e.target.closest('.notif-item');
        if (!item) return;
        var id = item.getAttribute('data-id');
        var url = item.getAttribute('data-url');
        var estabaSinLeer = item.classList.contains('sin-leer');
        if (estabaSinLeer) {
            item.classList.remove('sin-leer');
            setCount(count - 1);
        }
        fetch('/notificaciones/leer', {
            method: 'POST',
            headers: { 'X-CSRFToken': csrf(), 'Content-Type': 'application/x-www-form-urlencoded' },
            body: 'id=' + encodeURIComponent(id)
        }).catch(function () {})
          .then(function () { if (url) window.location.href = url; });
    });

    if (btnTodas) {
        btnTodas.addEventListener('click', function () {
            fetch('/notificaciones/leer-todas', {
                method: 'POST',
                headers: { 'X-CSRFToken': csrf() }
            }).catch(function () {});
            setCount(0);
            lista.querySelectorAll('.sin-leer').forEach(function (el) { el.classList.remove('sin-leer'); });
        });
    }

    // aviso en vivo: badge arriba + toast esquina superior derecha
    if (window.appSocket) {
        window.appSocket.on('notificacion_nueva', function (n) {
            setCount(count + 1);
            if (window.Swal) {
                Swal.mixin({
                    toast: true, position: 'top-end', showConfirmButton: false,
                    timer: 4500, timerProgressBar: true
                }).fire({
                    icon: n && n.tipo === 'tarea_completada' ? 'success' : 'info',
                    title: n && n.titulo ? n.titulo + ': ' + n.mensaje : 'Nueva notificación'
                });
            }
        });
    }
})();
