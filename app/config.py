import os

DATABASE_CONFIG = {
    'estadio_db': {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME_ESTADIO', 'estadio_db'),
        'charset': 'utf8mb4',
    },
    'seguridad': {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME_SEGURIDAD', 'seguridad'),
        'charset': 'utf8mb4',
    }
}

MAIL_CONFIG = {
    'username': os.getenv('MAIL_USERNAME', ''),
    'password': os.getenv('MAIL_APP_PASSWORD', ''),
    'default_sender': os.getenv('MAIL_DEFAULT_SENDER', ''),
}

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'app', 'static', 'uploads', 'premios')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
