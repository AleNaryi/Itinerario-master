import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


def enviar_email_recuperacion(destinatario, nombre, token_url):
    asunto = 'Recupera tu contrasena - Itinerario'
    cuerpo_html = f"""\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;font-family:Helvetica,Arial,sans-serif;background:#f4f6f9">
<table style="width:100%;max-width:560px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.06)">
<tr><td style="background:linear-gradient(135deg,#132a60 0%,#2563eb 100%);padding:32px 24px;text-align:center">
<span style="font-size:2.5rem">&#9918;</span>
<h1 style="color:#fff;font-size:1.25rem;margin:8px 0 0;font-weight:700">Recupera tu contrasena</h1>
</td></tr>
<tr><td style="padding:32px 24px">
<p style="color:#334155;font-size:0.95rem;line-height:1.6">Hola <strong>{nombre}</strong>,</p>
<p style="color:#334155;font-size:0.95rem;line-height:1.6">Recibimos una solicitud para restablecer tu contrasena en el <strong>Sistema de Gestion de Itinerario</strong>.</p>
<p style="text-align:center;margin:28px 0">
<a href="{token_url}" style="display:inline-block;background:linear-gradient(135deg,#2563eb 0%,#3b82f6 100%);color:#fff;text-decoration:none;padding:14px 36px;border-radius:12px;font-weight:600;font-size:0.95rem;box-shadow:0 4px 14px rgba(37,99,235,.3)">Restablecer contrasena</a>
</p>
<p style="color:#64748b;font-size:0.8rem;line-height:1.5">Este enlace expira en <strong>15 minutos</strong>. Si no solicitaste este cambio, ignora este mensaje.</p>
</td></tr>
<tr><td style="background:#f8fafc;padding:16px 24px;text-align:center;font-size:0.7rem;color:#94a3b8">
Sistema de Gestion de Itinerario &mdash; Estadio
</td></tr>
</table>
</body>
</html>"""

    msg = MIMEMultipart('alternative')
    msg['Subject'] = asunto
    msg['From'] = os.getenv('MAIL_DEFAULT_SENDER', '')
    msg['To'] = destinatario
    msg.attach(MIMEText(cuerpo_html, 'html'))

    username = os.getenv('MAIL_USERNAME', '')
    password = os.getenv('MAIL_APP_PASSWORD', '')
    sender = os.getenv('MAIL_DEFAULT_SENDER', '')

    if not username or not password or not sender:
        logger.error('MAIL_* vars not set in .env')
        return False

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.set_debuglevel(1 if os.getenv('FLASK_DEBUG') else 0)
        server.starttls()
        server.login(username, password)
        server.sendmail(sender, [destinatario], msg.as_string())
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error('SMTP auth failed: check MAIL_USERNAME and MAIL_APP_PASSWORD')
        return False
    except smtplib.SMTPException as e:
        logger.error(f'SMTP error: {e}')
        return False
    except OSError as e:
        logger.error(f'Network error sending email: {e}')
        return False
