from PIL import Image
import io

MAX_WIDTH = 800
QUALITY = 85


def optimizar_imagen(file_storage):
    """Optimiza imagen subida: redimensiona + convierte a JPEG + comprime."""
    img = Image.open(file_storage)

    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        new_height = int(img.height * ratio)
        img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=QUALITY, optimize=True)
    buffer.seek(0)

    return buffer
