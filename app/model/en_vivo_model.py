from datetime import datetime, date, time, timedelta
import logging
from app.database import Database, transaction

logger = logging.getLogger(__name__)


class SincronizacionModel:
    def _get_db(self):
        return Database.get_connection('seguridad')

    def registrar(self, guion_id, usuario_id, tipo, descripcion=None):
        try:
            from datetime import date, time, datetime
            hoy = date.today()
            ahora = datetime.now().time()
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """INSERT INTO sincronizaciones
                       (guion_id, usuario_id, nombre, descripcion,
                        fecha_sincronizacion, hora_sincronizacion, estado, created_at)
                       VALUES (%s, %s, %s, %s, %s, %s, 'success', NOW())""",
                    (guion_id, usuario_id, tipo, descripcion, hoy, ahora)
                )
                id = cur.lastrowid
            db.commit()
            return id
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def consultar(self, guion_id, filtro='todos', limite=100):
        try:
            from datetime import datetime, timedelta
            db = self._get_db()
            sql = """SELECT s.*, u.nombre as usuario_nombre
                     FROM sincronizaciones s
                     LEFT JOIN usuarios u ON s.usuario_id = u.id
                     WHERE s.guion_id = %s"""
            params = [guion_id]
            if filtro == 'acciones':
                sql += " AND s.nombre IN ('iniciar', 'finalizar')"
            elif filtro == 'eventos':
                sql += " AND s.nombre = 'sincronizar'"
            sql += " ORDER BY s.fecha_sincronizacion DESC, s.hora_sincronizacion DESC LIMIT %s"
            params.append(limite)
            with db.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
            for r in rows:
                fecha = r.get('fecha_sincronizacion')
                if isinstance(fecha, str):
                    from datetime import date
                    r['fecha_sincronizacion'] = date.fromisoformat(fecha)
                elif isinstance(fecha, datetime):
                    r['fecha_sincronizacion'] = fecha.date()
                hora = r.get('hora_sincronizacion')
                if isinstance(hora, timedelta):
                    hora = (datetime.min + hora).time()
                elif isinstance(hora, datetime):
                    hora = hora.time()
                if hora:
                    ampm = 'AM' if hora.hour < 12 else 'PM'
                    h12 = hora.hour % 12 or 12
                    r['fecha_formateada'] = f"{r['fecha_sincronizacion'].strftime('%d/%m/%Y')} {h12}:{hora.minute:02d} {ampm}"
                else:
                    r['fecha_formateada'] = r['fecha_sincronizacion'].strftime('%d/%m/%Y')
            return rows
        except Exception:
            logger.exception('Error de base de datos')
            return []


class EnVivoModel:
    def _get_db(self):
        return Database.get_connection('estadio_db')

    def obtener_en_vivo_actual(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM guiones WHERE estado = 'en_vivo' AND status = 1 LIMIT 1")
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def consultar_guiones_disponibles(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT * FROM guiones WHERE estado IN ('publicado', 'en_vivo', 'finalizado') AND status = 1 ORDER BY modificado_en DESC"
                )
                guiones = cur.fetchall()
            if guiones:
                ids = [g['id'] for g in guiones]
                placeholders = ', '.join(['%s'] * len(ids))
                with db.cursor() as cur:
                    cur.execute(f"SELECT * FROM guion_fechas WHERE guion_id IN ({placeholders}) ORDER BY fecha", ids)
                    fechas_map = {}
                    for fr in cur.fetchall():
                        gid = fr['guion_id']
                        if gid not in fechas_map:
                            fechas_map[gid] = []
                        fechas_map[gid].append(fr)
                for g in guiones:
                    g['fechas'] = fechas_map.get(g['id'], [])
            return guiones
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def iniciar(self, guion_id):
        try:
            with transaction('estadio_db'):
                db = self._get_db()
                with db.cursor() as cur:
                    cur.execute(
                        """UPDATE guiones SET estado = 'en_vivo', modificado_en = NOW(), inicio_show = NOW()
                           WHERE id = %s AND estado != 'en_vivo' AND NOT EXISTS (
                               SELECT 1 FROM guiones WHERE estado = 'en_vivo' AND id != %s
                           )""",
                        (guion_id, guion_id)
                    )
                    if cur.rowcount == 0:
                        return False
                    cur.execute(
                        "UPDATE elementos_guion SET estado = 'pendiente', inicio_curso = NULL WHERE guion_id = %s",
                        (guion_id,)
                    )
                    cur.execute("SELECT * FROM elementos_guion WHERE guion_id = %s ORDER BY orden LIMIT 1", (guion_id,))
                    primero = cur.fetchone()
                    if primero:
                        cur.execute(
                            "UPDATE elementos_guion SET estado = 'en_curso', inicio_curso = NOW() WHERE id = %s",
                            (primero['id'],)
                        )
            return True
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def finalizar(self, guion_id):
        try:
            with transaction('estadio_db'):
                db = self._get_db()
                with db.cursor() as cur:
                    cur.execute(
                        "UPDATE guiones SET estado = 'finalizado', modificado_en = NOW(), inicio_show = NULL WHERE id = %s",
                        (guion_id,)
                    )
                    cur.execute(
                        "UPDATE elementos_guion SET estado = 'pendiente', inicio_curso = NULL WHERE guion_id = %s",
                        (guion_id,)
                    )
            return True
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def obtener_elementos_en_vivo(self, guion_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM guion_fechas WHERE guion_id = %s ORDER BY fecha", (guion_id,))
                fechas = cur.fetchall()
                cur.execute("SELECT * FROM elementos_guion WHERE guion_id = %s AND tipo = 'pregame' ORDER BY hora", (guion_id,))
                pregame = cur.fetchall()
                cur.execute("SELECT * FROM elementos_guion WHERE guion_id = %s AND tipo = 'game' ORDER BY inning, medio_inning", (guion_id,))
                game = cur.fetchall()
            return fechas, pregame, game
        except Exception:
            logger.exception('Error de base de datos')
            return [], [], []

    def sincronizar_estados(self, guion_id, estados):
        try:
            descs = []
            with transaction('estadio_db'):
                db = self._get_db()
                with db.cursor() as cur:
                    for item in estados:
                        eid = item.get('id')
                        estado_str = item.get('estado')
                        accion = item.get('accion')
                        if eid and estado_str:
                            cur.execute("SELECT tipo, hora, inning, medio_inning, contenido, estado FROM elementos_guion WHERE id = %s", (int(eid),))
                            elem = cur.fetchone()
                            if elem and elem['estado'] != estado_str:
                                # reloj del elemento: entra a en_curso -> arranca; sale -> se limpia
                                if estado_str == 'en_curso':
                                    cur.execute(
                                        "UPDATE elementos_guion SET estado = %s, inicio_curso = NOW() WHERE id = %s",
                                        (estado_str, int(eid))
                                    )
                                else:
                                    cur.execute(
                                        "UPDATE elementos_guion SET estado = %s, inicio_curso = NULL WHERE id = %s",
                                        (estado_str, int(eid))
                                    )
                                if accion:
                                    descs.append(self._fmt_evento_log(elem, accion))
            return descs
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def _fmt_evento_log(self, elem, accion):
        INNING_NAMES = {1: '1ro', 2: '2do', 3: '3ro', 4: '4to',
                        5: '5to', 6: '6to', 7: '7mo', 8: '8vo', 9: '9no'}
        contenido = (elem['contenido'][:40] + '..') if len(elem['contenido']) > 40 else elem['contenido']
        if elem['tipo'] == 'pregame' and elem['hora']:
            h = elem['hora']
            if isinstance(h, timedelta):
                h = (datetime.min + h).time()
            ampm = 'AM' if h.hour < 12 else 'PM'
            h12 = h.hour % 12 or 12
            label = f"{h12}:{h.minute:02d} {ampm}"
        elif elem['tipo'] == 'game' and elem['inning']:
            iname = INNING_NAMES.get(elem['inning'], elem['inning'])
            medio = elem['medio_inning'].capitalize() if elem['medio_inning'] else ''
            label = f"{iname}° {medio}"
        else:
            label = contenido
            contenido = ''
        verbo = 'completado' if accion == 'completar' else 'reiniciado'
        return f"{label} - {contenido} {verbo}"

    def obtener_estado_actual(self, guion_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT id, estado, inicio_curso FROM elementos_guion WHERE guion_id = %s", (guion_id,))
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def guiones_por_fecha(self, fecha):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """SELECT g.id, g.nombre, COUNT(e.id) as elementos
                       FROM guiones g
                       JOIN guion_fechas gf ON g.id = gf.guion_id
                       LEFT JOIN elementos_guion e ON g.id = e.guion_id
                       WHERE gf.fecha = %s AND g.estado = 'publicado' AND g.status = 1
                       GROUP BY g.id, g.nombre""",
                    (fecha,)
                )
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []
