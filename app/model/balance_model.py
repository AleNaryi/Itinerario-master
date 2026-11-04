import pymysql  # O la librería de MySQL que use tu proyecto para capturar el error de BD
import logging

from app.database import Database

# --- SIMULACIÓN DE TRAIT (ValidacionesMixin) ---
class ValidacionesMixin:
    """Clase auxiliar que actúa como el 'trait' de validación solicitado"""
    def validar_monto(self, monto):
        try:
            val = float(monto)
            return val > 0
        except (ValueError, TypeError):
            return False

class Pago(Database, ValidacionesMixin):  
    
    def __init__(self, id_pago=None, id_contrato=None, monto=0, tipo_pago=None,
                 referencia=None, fecha_pago=None, hora_pago=None,
                 registrado_por=None, descripcion=None, estado=0,
                 fecha_registro=None, **kwargs):

        # Atributos encapsulados / privados (con doble guion bajo)
        self.__id_pago = id_pago
        self.__id_contrato = id_contrato
        self.__monto = monto
        self.__tipo_pago = tipo_pago
        self.__referencia = referencia
        self.__fecha_pago = fecha_pago
        self.__hora_pago = hora_pago
        self.__registrado_por = registrado_por
        self.__descripcion = descripcion
        self.__estado = estado
        self.__fecha_registro = fecha_registro
        self.__nombre_patrocinador = kwargs.get('nombre_patrocinador', None)
        self.__id_patrocinador = kwargs.get('id_patrocinador', None)

  
    @property
    def id_pago(self): return self.__id_pago
    
    @property
    def id_contrato(self): return self.__id_contrato
    
    @property
    def monto(self): return self.__monto
    
    @property
    def tipo_pago(self): return self.__tipo_pago
    
    @property
    def referencia(self): return self.__referencia
    
    @property
    def fecha_pago(self): return self.__fecha_pago
    
    @property
    def hora_pago(self): return self.__hora_pago
    
    @property
    def descripcion(self): return self.__descripcion
    
    @property
    def fecha_registro(self): return self.__fecha_registro
    
    @property
    def nombre_patrocinador(self): return self.__nombre_patrocinador

    @property
    def id_patrocinador(self): return self.__id_patrocinador

  
    
    def _get_db(self):
        
        return Database.get_connection('estadio_db')

    def obtener_contratos_activos(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("""
                    SELECT c.id_contrato, c.monto_total, c.estado as contrato_estado,
                           COALESCE(p.nombre_empresa, 'Sin patrocinador') as nombre_patrocinador
                    FROM contrato c
                    LEFT JOIN patrocinadores p ON c.id_patrocinador = p.id_patrocinador
                    WHERE c.estado = 1
                    ORDER BY c.id_contrato
                """)
                return cur.fetchall()  
        except Exception as e:
            logger.exception(f"Error en obtener_contratos_activos: {e}")
            return []

    def obtener_contrato_por_id(self, id_contrato):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("""
                    SELECT c.id_contrato, c.monto_total,
                           COALESCE(p.nombre_empresa, 'Sin patrocinador') as nombre_patrocinador
                    FROM contrato c
                    LEFT JOIN patrocinadores p ON c.id_patrocinador = p.id_patrocinador
                    WHERE c.id_contrato = %s
                """, (id_contrato,))
                return cur.fetchone() 
        except Exception as e:
            logger.exception(f"Error en obtener_contrato_por_id: {e}")
            return None

    def registrar_pago(self, datos):
    
        if not self.validar_monto(datos['monto']):
            print("Validación rechazada: El monto debe ser numérico y mayor a 0.")
            return None

        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("""
                    INSERT INTO pagos (id_contrato, monto, tipo_pago, referencia,
                                       fecha_pago, hora_pago, registrado_por,
                                       Descripcion, estado, fecha_registro)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, NOW())
                """, (
                    datos['id_contrato'], datos['monto'], datos['tipo_pago'],
                    datos.get('referencia'), datos['fecha_pago'], datos['hora_pago'],
                    datos.get('registrado_por'), datos.get('descripcion'),
                ))
                nuevo_id = cur.lastrowid
            db.commit()  # Confirma los datos de forma segura
            return self.obtener_pago_por_id(nuevo_id)
        except Exception as e:
            logger.exception(f"Error al registrar pago en Base de Datos: {e}")
            return None

    def get_total_pagado_by_contrato(self, id_contrato):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT COALESCE(SUM(monto), 0) as total FROM pagos WHERE id_contrato = %s AND estado = 0",
                    (id_contrato,)
                )
                row = cur.fetchone()
                return float(row['total']) if row else 0.0
        except Exception as e:
            logger.exception(f"Error en get_total_pagado_by_contrato: {e}")
            return 0.0

    def get_total_pagado_general(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT COALESCE(SUM(monto), 0) as total FROM pagos WHERE estado = 0")
                row = cur.fetchone()
                return float(row['total']) if row else 0.0
        except Exception as e:
            logger.exception(f"Error en get_total_pagado_general: {e}")
            return 0.0

    def obtener_historial_pagos(self, limit=100, fecha_inicio=None, fecha_fin=None,
                                tipo_pago=None):
        try:
            db = self._get_db()
            sql = """
                    SELECT p.*, c.id_patrocinador,
                           COALESCE(pat.nombre_empresa, 'Sin patrocinador') as nombre_patrocinador
                    FROM pagos p
                    LEFT JOIN contrato c ON p.id_contrato = c.id_contrato
                    LEFT JOIN patrocinadores pat ON c.id_patrocinador = pat.id_patrocinador
                    WHERE p.estado = 0"""
            params = []
            if fecha_inicio:
                sql += " AND p.fecha_pago >= %s"
                params.append(fecha_inicio)
            if fecha_fin:
                sql += " AND p.fecha_pago <= %s"
                params.append(fecha_fin)
            if tipo_pago:
                sql += " AND p.tipo_pago = %s"
                params.append(tipo_pago)
            sql += " ORDER BY p.fecha_registro DESC LIMIT %s"
            params.append(limit)
            with db.cursor() as cur:
                cur.execute(sql, params)
                # Convierte las filas en instancias de la clase Pago
                return [Pago(**r) for r in cur.fetchall()]
        except Exception as e:
            logger.exception(f"Error en obtener_historial_pagos: {e}")
            return []

    def obtener_pago_por_id(self, id_pago):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("""
                    SELECT p.*, COALESCE(pat.nombre_empresa, 'Sin patrocinador') as nombre_patrocinador
                    FROM pagos p
                    LEFT JOIN contrato c ON p.id_contrato = c.id_contrato
                    LEFT JOIN patrocinadores pat ON c.id_patrocinador = pat.id_patrocinador
                    WHERE p.id_pago = %s
                """, (id_pago,))
                row = cur.fetchone()
                return Pago(**row) if row else None
        except Exception as e:
            logger.exception(f"Error en obtener_pago_por_id: {e}")
            return None

    def obtener_top_contratos(self, limit=5):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("""
                    SELECT p.id_contrato, COUNT(*) as total_pagos,
                           COALESCE(pat.nombre_empresa, 'Sin patrocinador') as nombre_patrocinador
                    FROM pagos p
                    JOIN contrato c ON p.id_contrato = c.id_contrato
                    LEFT JOIN patrocinadores pat ON c.id_patrocinador = pat.id_patrocinador
                    WHERE p.estado = 0
                    GROUP BY p.id_contrato
                    ORDER BY total_pagos DESC
                    LIMIT %s
                """, (limit,))
                return cur.fetchall()
        except Exception as e:
            logger.exception(f"Error en obtener_top_contratos: {e}")
            return []

    def modificar_pago(self, pago_id, datos):
        if 'monto' in datos and not self.validar_monto(datos['monto']):
            logger.warning('Validación rechazada: El monto debe ser numérico y mayor a 0.')
            return None
        try:
            pago = self.obtener_pago_por_id(pago_id)
            if not pago:
                return None
            sets = []
            params = []
            for campo in ['monto', 'tipo_pago', 'referencia', 'fecha_pago', 'hora_pago']:
                if campo in datos:
                    sets.append(f"{campo} = %s")
                    params.append(datos[campo])
            if 'descripcion' in datos:
                sets.append("Descripcion = %s")
                params.append(datos['descripcion'])
            
            if sets:
                params.append(pago_id)
                db = self._get_db()
                with db.cursor() as cur:
                    cur.execute(
                        f"UPDATE pagos SET {', '.join(sets)} WHERE id_pago = %s",
                        params
                    )
                db.commit()
            return self.obtener_pago_por_id(pago_id)
        except Exception as e:
            logger.exception(f"Error en modificar_pago: {e}")
            return None

    def eliminar_pago(self, pago_id):
        try:
            pago = self.obtener_pago_por_id(pago_id)
            if not pago:
                return None
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("UPDATE pagos SET estado = 1 WHERE id_pago = %s", (pago_id,))
            db.commit()
            return pago
        except Exception as e:
            logger.exception(f"Error en eliminar_pago: {e}")
            return None


BalanceModel = Pago





logger = logging.getLogger(__name__)
