document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[onclick*="confirm("]').forEach(function(link) {
        const originalOnclick = link.getAttribute('onclick');
        const match = originalOnclick && originalOnclick.match(/confirm\('(.+?)'\)/);
        if (match) {
            const mensaje = match[1];
            link.removeAttribute('onclick');
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const href = this.getAttribute('href');
                Swal.fire({
                    title: '¿Confirmar?',
                    text: mensaje,
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#dc3545',
                    confirmButtonText: 'Sí, continuar',
                    cancelButtonText: 'Cancelar'
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.href = href;
                    }
                });
            });
        }
    });
});
