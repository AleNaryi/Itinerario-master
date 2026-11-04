import re
from datetime import datetime


class ValidacionesMixin:
    def __init__(self):
        self.errores = []

    def validar_obligatorio(self, valor, nombre):
        if not valor or (isinstance(valor, str) and not valor.strip()):
            self.errores.append(f'{nombre} es obligatorio')
            return False
        return True

    def validar_obligatorios(self, campos, datos):
        valido = True
        for campo in campos:
            valor = datos.get(campo) if isinstance(datos, dict) else getattr(datos, campo, None)
            if not valor and valor != 0 and valor is not False:
                self.errores.append(f'El campo {campo} es obligatorio')
                valido = False
        return valido

    def validar_entero_positivo(self, numero, campo):
        try:
            num = int(numero)
            if num <= 0:
                raise ValueError
            return True
        except (TypeError, ValueError):
            self.errores.append(f'El campo {campo} debe ser un número entero positivo')
            return False

    def validar_longitud(self, texto, min_len, max_len, campo):
        texto = str(texto) if texto is not None else ''
        if len(texto.strip()) < min_len:
            self.errores.append(f'El campo {campo} debe tener al menos {min_len} caracteres')
            return False
        if len(texto) > max_len:
            self.errores.append(f'El campo {campo} no puede tener más de {max_len} caracteres')
            return False
        return True

    def validar_fecha(self, fecha, campo='fecha'):
        if not fecha:
            self.errores.append(f'El campo {campo} es obligatorio')
            return False
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(fecha)):
            self.errores.append(f'El formato de {campo} debe ser YYYY-MM-DD')
            return False
        partes = str(fecha).split('-')
        try:
            datetime(int(partes[0]), int(partes[1]), int(partes[2]))
        except ValueError:
            self.errores.append(f'La {campo} no es una fecha válida')
            return False
        return True

    def validar_texto(self, texto, campo):
        if re.search(r'[<>"\'{}()&$%@*=;\/|`~]', str(texto)):
            self.errores.append(f'El campo {campo} contiene caracteres no permitidos')
            return False
        return True

    def validar_fecha_no_futura(self, fecha, campo='fecha'):
        try:
            if datetime.strptime(str(fecha), '%Y-%m-%d') > datetime.now():
                self.errores.append(f'La {campo} no puede ser una fecha futura')
                return False
        except ValueError:
            return False
        return True

    REGEX_EMAIL = re.compile(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$')

    def validar_email(self, email, campo='Email'):
        if not email:
            return True
        if not self.REGEX_EMAIL.match(str(email)):
            self.errores.append(f'El campo {campo} no tiene un formato válido')
            return False
        return True

    REGEX_RIF = re.compile(r'^[JjGgVvEe]-?\d{7,10}$')

    def validar_rif(self, rif, campo='RIF'):
        if not self.REGEX_RIF.match(str(rif or '')):
            self.errores.append(f'El campo {campo} no tiene un formato válido (ej. J-12345678)')
            return False
        return True

    def get_errores(self):
        return self.errores

    def limpiar_errores(self):
        self.errores = []

    def tiene_errores(self):
        return len(self.errores) > 0

    @staticmethod
    def sanitizar_texto(texto):
        return re.sub(r'[<>"\'{}()&$%@*=;\/|`~]', '', str(texto)).strip()
