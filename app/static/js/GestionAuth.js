import { validarEmail, validarPassword, validarTextoCaptcha, validarConfirmPassword, agregarInvalido } from './validacion.js';

document.addEventListener('DOMContentLoaded', function() {
    initLoginForm();
    initForgotForm();
    initCambiarPassword();
});

function initLoginForm() {
    const form = document.getElementById('loginForm');
    if (!form) return;

    const email = form.querySelector('[name="email"]');
    const password = form.querySelector('[name="password"]');
    const captcha = document.getElementById('captcha_text');
    const btnLogin = document.getElementById('btnLogin');
    const loading = document.getElementById('loginLoading');
    const logo = document.getElementById('loadingLogo');
    const title = document.getElementById('loadingTitle');
    const track = document.getElementById('loadingTrack');
    const barFill = document.getElementById('loadingBarFill');
    const balls = document.querySelectorAll('.loading-baseball');

    if (email) {
        email.addEventListener('input', function() { validarEmail(this); });
        email.addEventListener('blur', function() { validarEmail(this); });
    }
    if (password) {
        password.addEventListener('input', function() { validarPassword(this); });
        password.addEventListener('blur', function() { validarPassword(this); });
    }
    if (captcha) {
        captcha.addEventListener('input', function() { validarTextoCaptcha(this); });
        captcha.addEventListener('blur', function() { validarTextoCaptcha(this); });
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        var valido = true;
        if (email) { if (!validarEmail(email)) valido = false; }
        if (password) { if (!validarPassword(password)) valido = false; }
        if (captcha) { if (!validarTextoCaptcha(captcha)) valido = false; }
        if (!valido || !btnLogin || !loading) return;

        btnLogin.disabled = true;
        var origText = btnLogin.innerHTML;
        btnLogin.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verificando...';

        var data = new URLSearchParams();
        if (email) data.append('email', email.value);
        if (password) data.append('password', password.value);
        if (captcha) data.append('captcha_text', captcha.value);
        data.append('csrf_token', form.querySelector('[name="csrf_token"]').value);

        fetch('/auth/validate-login', {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: data.toString()
        })
        .then(function(r) { return r.json(); })
        .then(function(resp) {
            if (resp.valid) {
                // All confirmed — show loading and submit
                btnLogin.disabled = true;
                btnLogin.innerHTML = origText;
                loading.classList.add('show');

                requestAnimationFrame(function() {
                    logo.classList.add('show');
                    setTimeout(function() { title.classList.add('show'); }, 150);
                    setTimeout(function() { track.classList.add('show'); }, 300);
                    var current = 0;
                    var total = balls.length;
                    var interval = setInterval(function() {
                        if (current >= total) {
                            clearInterval(interval);
                            barFill.style.width = '100%';
                            HTMLFormElement.prototype.submit.call(form);
                            return;
                        }
                        balls[current].classList.add('active');
                        current++;
                        barFill.style.width = (current / total) * 100 + '%';
                    }, 500);
                });
            } else {
                btnLogin.disabled = false;
                btnLogin.innerHTML = origText;
                if (resp.field === 'captcha' && captcha) {
                    agregarInvalido(captcha, resp.message);
                } else if (resp.field === 'credentials') {
                    if (email) agregarInvalido(email, resp.message);
                    if (password) agregarInvalido(password, '');
                }
            }
        })
        .catch(function() {
            // AJAX failed — submit directly as fallback
            btnLogin.disabled = false;
            btnLogin.innerHTML = origText;
            HTMLFormElement.prototype.submit.call(form);
        });
    });
}

function initForgotForm() {
    const form = document.getElementById('forgotForm');
    if (!form) return;

    const email = form.querySelector('[name="email"]');
    const captcha = document.getElementById('captcha_text');

    if (email) {
        email.addEventListener('input', function() { validarEmail(this); });
        email.addEventListener('blur', function() { validarEmail(this); });
    }
    if (captcha) {
        captcha.addEventListener('input', function() { validarTextoCaptcha(this); });
        captcha.addEventListener('blur', function() { validarTextoCaptcha(this); });
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        var valido = true;
        if (email) {
            if (!validarEmail(email)) valido = false;
        }
        if (captcha) {
            if (!validarTextoCaptcha(captcha)) valido = false;
        }
        if (valido) {
            form.submit();
        }
    });
}

function initCambiarPassword() {
    const form = document.querySelector('form:has(#password_nueva)');
    if (!form) return;

    const actual = document.getElementById('password_actual');
    const nueva = document.getElementById('password_nueva');
    const confirmar = document.getElementById('confirmar_password');
    const submitBtn = form.querySelector('[type="submit"]');

    if (nueva) {
        nueva.addEventListener('input', function() { validarPassword(this); });
        nueva.addEventListener('blur', function() { validarPassword(this); });
    }
    if (confirmar) {
        confirmar.addEventListener('input', function() { validarConfirmPassword(nueva, this); });
        confirmar.addEventListener('blur', function() { validarConfirmPassword(nueva, this); });
    }

    if (submitBtn) {
        submitBtn.addEventListener('click', function(e) {
            const valActual = actual && actual.value;
            const valNueva = nueva ? validarPassword(nueva) : false;
            const valConfirm = confirmar ? validarConfirmPassword(nueva, confirmar) : false;

            if (!valActual || !valNueva || !valConfirm) {
                e.preventDefault();
                Swal.fire({
                    title: '❌ Error de validación',
                    text: 'Corrige los campos marcados en rojo.',
                    icon: 'error',
                    confirmButtonColor: '#3085d6'
                });
            }
        });
    }
}
