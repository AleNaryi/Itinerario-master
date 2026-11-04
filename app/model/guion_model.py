from datetime import datetime, date, time, timedelta
import logging
from app.database import Database, transaction
from app.model.interfaces import CrudInterface
from app.model.validaciones_model import ValidacionesMixin

logger = logging.getLogger(__name__)


def _parsear_duracion(val):
    if not val:
        return 0
    val = str(val).strip()
    if ',' in val:
        partes = val.split(',')
        minutos = int(partes[0]) if partes[0] else 0
        seg_str = partes[1].ljust(2, '0')[:2]
        segundos = int(seg_str)
    else:
        try:
            minutos = int(val)
        except ValueError:
            minutos = 0
        segundos = 0
    return minutos * 60 + segundos


class GuionModel(ValidacionesMixin):
    def __init__(self):
        super().__init__()
        self.db_name = 'estadio_db'
        self.__nombre = None
        self.__tiempo_inning = None
        self.__fecha = None

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def set_nombre(self, valor):
        self.__nombre = valor

    def set_tiempo_inning(self, valor):
        self.__tiempo_inning = valor

    def set_fecha(self, valor):
        self.__fecha = valor

    def _validar_datos_guion(self) -> bool:
        self.limpiar_errores()
        if not self.validar_obligatorio(self.__nombre, 'Nombre'):
            return False
        if not self.validar_longitud(self.__nombre, 3, 50, 'Nombre'):
            return False
        if not self.__fecha:
            self.errores.append('La fecha es obligatoria')
            return False
        return True

    def confirmar_registro(self):
        return self._registrar()

    def _registrar(self):
        if not self._validar_datos_guion():
            return None
        try:
            with transaction(self.db_name):
                db = self._get_db()
                with db.cursor() as cur:
                    cur.execute(
                        "INSERT INTO guiones (nombre, tiempo_inning, estado, status, creado_en) VALUES (%s, %s, 'borrador', 1, NOW())",
                        (self.__nombre, self.__tiempo_inning)
                    )
                    id = cur.lastrowid
                    cur.execute(
                        "INSERT INTO guion_fechas (guion_id, fecha) VALUES (%s, %s)",
                        (id, self.__fecha)
                    )
            return id
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def consultar(self, **filtros):
        try:
            db = self._get_db()
            sql = "SELECT * FROM guiones WHERE 1=1 AND status = 1"
            params = []
            if filtros.get('estado'):
                sql += " AND estado = %s"
                params.append(filtros['estado'])
            sql += " ORDER BY creado_en DESC"
            with db.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def contar(self, **filtros):
        try:
            db = self._get_db()
            sql = "SELECT COUNT(*) as total FROM guiones WHERE 1=1 AND status = 1"
            params = []
            if filtros.get('estado'):
                sql += " AND estado = %s"
                params.append(filtros['estado'])
            with db.cursor() as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
                return row['total'] if row else 0
        except Exception:
            logger.exception('Error de base de datos')
            return 0

    def obtener_por_id(self, id_registro):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM guiones WHERE id = %s AND status = 1", (id_registro,))
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def obtener_fechas(self, guion_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM guion_fechas WHERE guion_id = %s ORDER BY fecha", (guion_id,))
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def _validar_datos_guion_dict(self, datos) -> bool:
        self.limpiar_errores()
        if not self.validar_obligatorio(datos.get('nombre'), 'Nombre'):
            return False
        if not self.validar_longitud(datos.get('nombre', ''), 3, 50, 'Nombre'):
            return False
        if not datos.get('fecha'):
            self.errores.append('La fecha es obligatoria')
            return False
        return True

    def registrar(self, datos):
        if not self._validar_datos_guion_dict(datos):
            return None
        try:
            with transaction(self.db_name):
                db = self._get_db()
                with db.cursor() as cur:
                    cur.execute(
                        "INSERT INTO guiones (nombre, tiempo_inning, estado, status, creado_en) VALUES (%s, %s, 'borrador', 1, NOW())",
                        (datos['nombre'], datos.get('tiempo_inning'))
                    )
                    id = cur.lastrowid
                    cur.execute(
                        "INSERT INTO guion_fechas (guion_id, fecha) VALUES (%s, %s)",
                        (id, datos['fecha'])
                    )
            return id
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def verificar_nombre(self, nombre):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) as total FROM guiones WHERE nombre LIKE %s AND status = 1",
                    (f"{nombre} - %",)
                )
                row = cur.fetchone()
                return row['total'] > 0 if row else False
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def modificar(self, id_registro, datos):
        try:
            with transaction(self.db_name):
                db = self._get_db()
                sets = []
                params = []
                if 'nombre' in datos:
                    sets.append("nombre = %s")
                    params.append(datos['nombre'])
                if 'estado' in datos:
                    sets.append("estado = %s")
                    params.append(datos['estado'])
                if 'tiempo_inning' in datos:
                    sets.append("tiempo_inning = %s")
                    params.append(datos['tiempo_inning'])
                if sets:
                    sets.append("modificado_en = NOW()")
                    params.append(id_registro)
                    with db.cursor() as cur:
                        cur.execute(f"UPDATE guiones SET {', '.join(sets)} WHERE id = %s", params)
                if 'fechas' in datos:
                    with db.cursor() as cur:
                        cur.execute("DELETE FROM guion_fechas WHERE guion_id = %s", (id_registro,))
                        for fecha in datos['fechas']:
                            cur.execute(
                                "INSERT INTO guion_fechas (guion_id, fecha) VALUES (%s, %s)",
                                (id_registro, fecha)
                            )
            return self.obtener_por_id(id_registro)
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def eliminar(self, id_registro):
        try:
            with transaction(self.db_name):
                db = self._get_db()
                with db.cursor() as cur:
                    cur.execute("UPDATE guiones SET status = 0, modificado_en = NOW() WHERE id = %s", (id_registro,))
            return True
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def replicar(self, guion_origen_id, fechas, nombre_base):
        try:
            origen = self.obtener_por_id(guion_origen_id)
            if not origen:
                return []
            elem_model = ElementoGuionModel()
            elementos = elem_model.consultar(guion_id=guion_origen_id)
            ids_creados = []
            with transaction(self.db_name):
                db = self._get_db()
                with db.cursor() as cur:
                    for fecha in fechas:
                        nombre_con_fecha = f"{nombre_base} - {fecha}"
                        cur.execute(
                            "INSERT INTO guiones (nombre, tiempo_inning, estado, status, creado_en) VALUES (%s, %s, 'borrador', 1, NOW())",
                            (nombre_con_fecha, origen['tiempo_inning'])
                        )
                        nuevo_id = cur.lastrowid
                        cur.execute(
                            "INSERT INTO guion_fechas (guion_id, fecha) VALUES (%s, %s)",
                            (nuevo_id, fecha)
                        )
                        for elem in elementos:
                            cur.execute(
                                """INSERT INTO elementos_guion
                                   (guion_id, fecha_id, tipo, hora, inning, medio_inning,
                                    contenido, duracion_estimada, encargado, orden, creado_en)
                                   VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
                                (nuevo_id, elem['tipo'], elem['hora'], elem['inning'],
                                 elem['medio_inning'], elem['contenido'],
                                 elem['duracion_estimada'], elem['encargado'], elem['orden'])
                            )
                        ids_creados.append(nuevo_id)
            return ids_creados
        except Exception:
            logger.exception('Error de base de datos')
            return []


class ElementoGuionModel(ValidacionesMixin):
    def __init__(self):
        super().__init__()
        self.__guion_id = None
        self.__tipo = None
        self.__contenido = None
        self.__duracion_estimada = None
        self.__hora = None
        self.__inning = None
        self.__medio_inning = None
        self.__encargado = None
        self.__orden = None
        self.__fecha_id = None

    def _get_db(self):
        return Database.get_connection('estadio_db')

    def set_guion_id(self, valor):
        self.__guion_id = valor

    def set_tipo(self, valor):
        self.__tipo = valor

    def set_contenido(self, valor):
        self.__contenido = valor

    def set_duracion_estimada(self, valor):
        self.__duracion_estimada = valor

    def set_hora(self, valor):
        self.__hora = valor

    def set_inning(self, valor):
        self.__inning = valor

    def set_medio_inning(self, valor):
        self.__medio_inning = valor

    def set_encargado(self, valor):
        self.__encargado = valor

    def set_orden(self, valor):
        self.__orden = valor

    def set_fecha_id(self, valor):
        self.__fecha_id = valor

    def _validar_datos_elemento(self) -> bool:
        self.limpiar_errores()
        if not self.validar_obligatorio(self.__guion_id, 'Guion'):
            return False
        if not self.validar_obligatorio(self.__tipo, 'Tipo'):
            return False
        if not self.validar_obligatorio(self.__contenido, 'Contenido'):
            return False
        if self.__contenido and not self.validar_longitud(self.__contenido, 5, 500, 'Contenido'):
            return False
        if self.__tipo == 'pregame' and not self.__hora:
            self.errores.append('Para Pre-Game debes indicar una hora')
            return False
        if self.__tipo == 'game' and (not self.__inning or not self.__medio_inning):
            self.errores.append('Para Game debes seleccionar inning y medio')
            return False
        return True

    def confirmar_registro(self):
        return self._registrar()

    def _registrar(self):
        if not self._validar_datos_elemento():
            return None
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """INSERT INTO elementos_guion
                       (guion_id, fecha_id, tipo, hora, inning, medio_inning,
                        contenido, duracion_estimada, encargado, orden, estado, creado_en)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
                    (
                        self.__guion_id, self.__fecha_id,
                        self.__tipo, self.__hora,
                        self.__inning, self.__medio_inning,
                        self.__contenido, self.__duracion_estimada,
                        self.__encargado, self.__orden or 0,
                        None,
                    )
                )
                id = cur.lastrowid
            db.commit()
            return self.obtener_por_id(id)
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def consultar(self, **filtros):
        try:
            db = self._get_db()
            sql = "SELECT * FROM elementos_guion WHERE 1=1"
            params = []
            if filtros.get('guion_id'):
                sql += " AND guion_id = %s"
                params.append(filtros['guion_id'])
            if filtros.get('tipo'):
                sql += " AND tipo = %s"
                params.append(filtros['tipo'])
            sql += " ORDER BY orden"
            with db.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_por_id(self, id_registro):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM elementos_guion WHERE id = %s", (id_registro,))
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def modificar(self, id_registro, datos):
        try:
            sets = []
            params = []
            for campo in ['tipo', 'hora', 'inning', 'medio_inning', 'contenido',
                           'duracion_estimada', 'encargado', 'orden', 'fecha_id', 'estado']:
                if campo in datos:
                    sets.append(f"{campo} = %s")
                    params.append(datos[campo])
            if sets:
                params.append(id_registro)
                db = self._get_db()
                with db.cursor() as cur:
                    cur.execute(f"UPDATE elementos_guion SET {', '.join(sets)} WHERE id = %s", params)
                db.commit()
            return self.obtener_por_id(id_registro)
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def eliminar(self, id_registro):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("DELETE FROM elementos_guion WHERE id = %s", (id_registro,))
            db.commit()
        except Exception:
            logger.exception('Error de base de datos')

    def obtener_ocupados(self, guion_id):
        try:
            elementos = self.consultar(guion_id=guion_id)
            horas_usadas = set()
            innings_usados = {}
            for e in elementos:
                if e['tipo'] == 'pregame' and e['hora']:
                    horas_usadas.add(str(e['hora'])[:5])
                elif e['tipo'] == 'game' and e['inning']:
                    key = f"{e['inning']}-{e['medio_inning']}"
                    innings_usados[key] = e['id']
            return horas_usadas, innings_usados
        except Exception:
            logger.exception('Error de base de datos')
            return set(), {}

    def obtener_ultimo_orden(self, guion_id, tipo):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT MAX(orden) as max_orden FROM elementos_guion WHERE guion_id = %s AND tipo = %s",
                    (guion_id, tipo)
                )
                row = cur.fetchone()
                return row['max_orden'] if row and row['max_orden'] else 0
        except Exception:
            logger.exception('Error de base de datos')
            return 0

    def consultar_excepto(self, guion_id, elemento_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT * FROM elementos_guion WHERE guion_id = %s AND id != %s ORDER BY tipo, orden",
                    (guion_id, elemento_id)
                )
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_por_guion_ordenados(self, guion_id):
        pregame = list(self.consultar(guion_id=guion_id, tipo='pregame'))
        game = list(self.consultar(guion_id=guion_id, tipo='game'))
        pregame.sort(key=lambda e: str(e['hora']) if e['hora'] else '23:59')
        game.sort(key=lambda e: (e['inning'] or 99, e['medio_inning'] or 'zzz'))
        return pregame, game
