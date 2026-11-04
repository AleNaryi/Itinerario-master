document.addEventListener('DOMContentLoaded', function () {
    const fab = document.getElementById('auroraChatFab');
    const panel = document.getElementById('auroraChatPanel');
    const closeBtn = document.getElementById('auroraChatClose');
    const messages = document.getElementById('auroraChatMessages');
    const input = document.getElementById('auroraChatInput');
    const sendBtn = document.getElementById('auroraChatSend');
    const suggestions = document.getElementById('auroraChatSuggestions');

    if (!fab || !panel) return;

    function isMobile() {
        return window.innerWidth <= 768;
    }

    fab.addEventListener('click', function () {
        panel.classList.add('aurora-chat-open');
        fab.classList.add('aurora-fab-hidden');
        if (isMobile()) document.body.style.overflow = 'hidden';
        setTimeout(function () { input.focus(); scrollBottom(); }, 320);
    });

    closeBtn.addEventListener('click', function () {
        panel.classList.remove('aurora-chat-open');
        fab.classList.remove('aurora-fab-hidden');
        if (isMobile()) document.body.style.overflow = '';
    });

    sendBtn.addEventListener('click', enviarMensaje);
    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            enviarMensaje();
        }
    });

    suggestions.addEventListener('click', function (e) {
        var btn = e.target.closest('.aurora-suggestion');
        if (!btn) return;
        input.value = btn.dataset.msg;
        enviarMensaje();
    });

    function enviarMensaje() {
        var texto = input.value.trim();
        if (!texto) return;

        appendMsg('usuario', texto);
        input.value = '';
        suggestions.style.display = 'none';

        appendTyping();

        var fd = new FormData();
        fd.append('mensaje', texto);
        fd.append('csrf_token', getCSRF());

        fetch('/asistente/', {
            method: 'POST',
            body: fd,
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                removeTyping();
                if (data.error) {
                    appendMsg('ia', 'Error: ' + data.error);
                } else {
                    appendMsg('ia', data.respuesta);
                }
                scrollBottom();
            })
            .catch(function () {
                removeTyping();
                appendMsg('ia', 'No pude conectarme. Intenta de nuevo.');
            });
    }

    function appendMsg(tipo, texto) {
        var div = document.createElement('div');
        div.className = 'aurora-msg aurora-msg-' + tipo;

        var avatar = document.createElement('div');
        avatar.className = 'aurora-msg-avatar';
        if (tipo === 'ia') {
            avatar.innerHTML = '<img src="/static/img/Logo-blanco.png" alt="Aurora" class="aurora-avatar-img">';
        } else {
            avatar.innerHTML = '<i class="fas fa-user"></i>';
        }

        var bubble = document.createElement('div');
        bubble.className = 'aurora-msg-bubble';
        bubble.innerHTML = markedSimple(texto);

        div.appendChild(avatar);
        div.appendChild(bubble);
        messages.appendChild(div);
    }

    function appendTyping() {
        var div = document.createElement('div');
        div.className = 'aurora-msg aurora-msg-ia aurora-typing-indicator';
        div.id = 'auroraTyping';
        div.innerHTML =
            '<div class="aurora-msg-avatar"><img src="/static/img/Logo-blanco.png" alt="Aurora" class="aurora-avatar-img"></div>' +
            '<div class="aurora-msg-bubble"><span class="aurora-dot"></span><span class="aurora-dot"></span><span class="aurora-dot"></span></div>';
        messages.appendChild(div);
        scrollBottom();
    }

    function removeTyping() {
        var t = document.getElementById('auroraTyping');
        if (t) t.remove();
    }

    function scrollBottom() {
        messages.scrollTop = messages.scrollHeight;
    }

    function getCSRF() {
        var el = document.querySelector('input[name="csrf_token"]');
        return el ? el.value : '';
    }

    function markedSimple(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    /* Keyboard handling for mobile */
    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', function () {
            if (panel.classList.contains('aurora-chat-open')) {
                scrollBottom();
            }
        });
    }

    /* Load history on first open */
    var historialCargado = false;
    fab.addEventListener('click', function () {
        if (historialCargado) return;
        historialCargado = true;
        fetch('/asistente/', { method: 'GET' })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.historial && data.historial.length) {
                    messages.innerHTML = '';
                    data.historial.forEach(function (h) {
                        appendMsg('usuario', h.mensaje_usuario);
                        appendMsg('ia', h.respuesta_ia);
                    });
                    scrollBottom();
                }
            })
            .catch(function () { });
    });
});
