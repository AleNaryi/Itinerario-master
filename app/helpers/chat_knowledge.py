import re
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ChatKnowledge:
    NOMBRE = 'Aurora'

    GUIAS = {
        'guion': {
            'crear': 'Para crear un guion ve a **Guiones** > clickea el botón "Nuevo Guion", completa el nombre, tiempo por inning y fecha. Luego agrega los elementos (pre-game por tiempo, game por inning).',
            'editar': 'Para editar un guion ve a **Guiones** > busca el guion en la tabla > clickea el ícono de editar en la columna de acciones.',
            'publicar': 'Para publicar un guion ve a **Guiones** > busca el guion > haz clic en "Publicar". El guion pasará a estado publicado y quedará disponible para En Vivo.',
            'replicar': 'Para replicar un guion ve a **Guiones** > selecciona el guion publicado > haz clic en "Replicar" y elige las fechas destino.',
        },
        'inventario': {
            'crear': 'Para registrar un activo ve a **Inventario** > haz clic en "Nuevo Activo", completa nombre, tipo, estado y demás campos.',
            'asignar': 'Para asignar un activo a un usuario ve a **Inventario** > busca el activo > haz clic en "Asignar" y selecciona el usuario.',
            'devolver': 'Para devolver un activo asignado ve a **Inventario** > pestaña de asignaciones > haz clic en "Devolver".',
        },
        'contrato': {
            'crear': 'Para crear un contrato ve a **Contratos** > haz clic en "Nuevo Contrato", selecciona el patrocinador, fechas, tipo y monto.',
            'editar': 'Para editar un contrato ve a **Contratos** > busca el contrato > haz clic en el ícono de editar.',
        },
        'tarea': {
            'crear': 'Para crear una tarea ve a **Gestión de Tareas** > haz clic en "Nueva Tarea", escribe el nombre y la instrucción.',
            'asignar': 'Para asignar una tarea ve a **Gestión de Tareas** > selecciona la tarea > haz clic en "Asignar" y elige el usuario.',
            'completar': 'Para marcar una tarea como completada ve a **Mis Tareas** > haz clic en "Completar" junto a la tarea.',
        },
        'patrocinador': {
            'crear': 'Para registrar un patrocinador ve a **Patrocinadores** > haz clic en "Nuevo Patrocinador", completa RIF, nombre de empresa, contacto y teléfono.',
        },
        'premio': {
            'crear': 'Para registrar un premio ve a **Premios** > haz clic en "Nuevo Premio", escribe nombre, descripción, cantidad y seleccione el patrocinador.',
        },
        'mantenimiento': {
            'ingresar': 'Para ingresar un recurso a mantenimiento ve a **Mantenimiento** > haz clic en "Ingresar a Mantenimiento", selecciona el recurso y escribe el diagnóstico.',
            'reparar': 'Para marcar un recurso como reparado ve a **Mantenimiento** > busca el recurso en estado "En Reparación" > haz clic en "Reparar".',
        },
        'reel': {
            'crear': 'Para crear un reel ve a **Reels** > haz clic en "Nuevo Reel", dale un nombre y guarda. Luego agrega los videos.',
            'agregar_video': 'Para agregar un video a un reel ve a **Reels** > abre el reel > haz clic en "Agregar Video" y completa los datos.',
        },
        'usuario': {
            'crear': 'Para crear un usuario ve a **Usuarios** > haz clic en "Nuevo Usuario", completa nombre, email, cédula y contraseña.',
            'perfil': 'Para ver tu perfil haz clic en tu nombre en la barra lateral inferior > "Mi Perfil".',
        },
        'reporte': {
            'generar': 'Para generar un reporte ve a **Reportes** > selecciona el módulo del dropdown, aplica filtros si lo deseas y haz clic en "Generar PDF".',
        },
        'en_vivo': {
            'iniciar': 'Para iniciar una sesión en vivo ve a **En Vivo** > selecciona el guion y la fecha > haz clic en "Iniciar En Vivo".',
        },
    }

    MODULO_KEYWORDS = {
        'guiones': ['guion', 'guiones', 'script', 'scripts', 'elemento', 'elementos', 'inning', 'pregame', 'game'],
        'inventario': ['inventario', 'activo', 'activos', 'recurso', 'recursos', 'asignar activo', 'devolver activo'],
        'contratos': ['contrato', 'contratos', 'vigente', 'vencido', 'borrador'],
        'patrocinadores': ['patrocinador', 'patrocinadores', 'sponsor', 'empresa'],
        'premios': ['premio', 'premios', 'regalo', 'entregar premio'],
        'tareas': ['tarea', 'tareas', 'asignar tarea', 'completar tarea', 'pendiente'],
        'mantenimiento': ['mantenimiento', 'reparar', 'reparación', 'recurso dañado', 'baja'],
        'reels': ['reel', 'reels', 'video', 'videos'],
        'usuarios': ['usuario', 'usuarios', 'cuenta', 'perfil', 'contraseña'],
        'bitacora': ['bitacora', 'actividad', 'historial', 'sesión', 'sesiones', 'qué hicieron'],
        'balance': ['pago', 'pagos', 'balance', 'monto', 'deuda', 'saldo'],
        'reportes': ['reporte', 'reportes', 'pdf', 'generar reporte', 'exportar'],
        'en_vivo': ['en vivo', 'vivo', 'directo', 'transmisión'],
    }

    ACCION_KEYWORDS = {
        'contar': ['cuántos', 'cuantas', 'cuántas', 'hay', 'existen', 'total', 'cantidad', 'numero', 'número'],
        'estados': ['estado', 'estados', 'estatus', 'vigente', 'vencido', 'borrador', 'publicado', 'pendiente', 'completada', 'disponible', 'en_mantenimiento', 'en reparación', 'dañado'],
        'reciente': ['reciente', 'últimos', 'últimas', 'hoy', 'ayer', 'esta semana', 'este mes', 'actividad'],
        'guia': ['cómo', 'como', 'guía', 'guia', 'ayuda', 'paso a paso', 'instrucciones', 'manual', 'enseña', 'explica'],
        'saludo': ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'hey', 'saludos', 'qué tal', 'que tal'],
        'agradecimiento': ['gracias', 'te agradezco', 'muchas gracias', 'agradecido'],
        'despedida': ['adiós', 'adios', 'hasta luego', 'nos vemos', 'chao', 'bye'],
        'identidad': ['quién eres', 'quien eres', 'qué eres', 'que eres', 'tu nombre', 'cómo te llamas', 'como te llamas'],
    }

    @classmethod
    def procesar(cls, mensaje, usuario):
        msg = mensaje.lower().strip()
        intencion = cls._detectar_intencion(msg)

        if intencion['tipo'] == 'saludo':
            return cls._responder_saludo(usuario)
        if intencion['tipo'] == 'identidad':
            return cls._responder_identidad()
        if intencion['tipo'] == 'agradecimiento':
            return cls._responder_agradecimiento()
        if intencion['tipo'] == 'despedida':
            return cls._responder_despedida()
        if intencion['tipo'] == 'guia':
            return cls._responder_guia(msg, intencion)
        if intencion['tipo'] == 'contar':
            return cls._responder_contar(intencion, usuario)
        if intencion['tipo'] == 'estados':
            return cls._responder_estados(intencion)
        if intencion['tipo'] == 'reciente':
            return cls._responder_reciente(intencion, usuario)
        if intencion['tipo'] == 'contexto_cruzado':
            return cls._responder_contexto_cruzado(msg, intencion, usuario)

        return cls._responder_default(msg)

    @classmethod
    def _detectar_intencion(cls, msg):
        result = {'tipo': 'default', 'modulos': [], 'accion': None}

        for accion, keywords in cls.ACCION_KEYWORDS.items():
            for kw in keywords:
                if kw in msg:
                    result['accion'] = accion
                    result['tipo'] = accion
                    break
            if result['accion']:
                break

        for modulo, keywords in cls.MODULO_KEYWORDS.items():
            for kw in keywords:
                if kw in msg:
                    if modulo not in result['modulos']:
                        result['modulos'].append(modulo)
                    break

        if len(result['modulos']) >= 2:
            result['tipo'] = 'contexto_cruzado'

        if result['tipo'] == 'guia' and result['modulos']:
            result['tipo'] = 'guia'

        return result

    @classmethod
    def _responder_saludo(cls, usuario):
        nombre = usuario.nombre if usuario else 'usuario'
        hora = datetime.now().hour
        if hora < 12:
            saludo = 'Buenos días'
        elif hora < 18:
            saludo = 'Buenas tardes'
        else:
            saludo = 'Buenas noches'
        return {
            'respuesta': f'{saludo}, **{nombre}**. Soy **{cls.NOMBRE}**, tu asistente del sistema Itinerario. Puedo ayudarte con información sobre los módulos, estados, conteos y guías de uso. ¿En qué te puedo ayudar?',
            'intencion': 'saludo',
            'confianza': 1.0,
        }

    @classmethod
    def _responder_identidad(cls):
        return {
            'respuesta': f'Soy **{cls.NOMBRE}**, la asistente inteligente del sistema **Itinerario** del Estadio Antonio Herrera Gutiérrez. Puedo consultarte datos del sistema, guiarte en cómo usar los módulos y darte un resumen de la actividad reciente. ¿Qué necesitas saber?',
            'intencion': 'identidad',
            'confianza': 1.0,
        }

    @classmethod
    def _responder_agradecimiento(cls):
        return {
            'respuesta': f'De nada. Si necesitas algo más, aquí estoy.',
            'intencion': 'agradecimiento',
            'confianza': 1.0,
        }

    @classmethod
    def _responder_despedida(cls):
        return {
            'respuesta': f'¡Hasta luego! Que tengas un excelente día.',
            'intencion': 'despedida',
            'confianza': 1.0,
        }

    @classmethod
    def _responder_guia(cls, msg, intencion):
        if not intencion['modulos']:
            modulos_disponibles = ', '.join(cls.GUIAS.keys())
            return {
                'respuesta': f'Puedo guiarte en estos módulos: **{modulos_disponibles}**. Dime cuál te interesa y te explico los pasos.',
                'intencion': 'guia',
                'confianza': 0.6,
            }

        modulo = intencion['modulos'][0]
        guias_modulo = cls.GUIAS.get(modulo, {})

        for accion, texto in guias_modulo.items():
            if accion in msg or any(p in msg for p in [accion.replace('_', ' ')]):
                return {
                    'respuesta': texto,
                    'intencion': f'guia_{modulo}_{accion}',
                    'confianza': 0.9,
                }

        pasos = '\n'.join([f'- **{a.replace("_", " ").title()}**: {t.split(".")[0]}.' for a, t in guias_modulo.items()])
        return {
            'respuesta': f'En el módulo de **{modulo.title()}** puedo ayudarte con:\n{pasos}\n\n¿Qué acción específica necesitas?',
            'intencion': f'guia_{modulo}',
            'confianza': 0.7,
        }

    @classmethod
    def _responder_contar(cls, intencion, usuario):
        if not intencion['modulos']:
            return {
                'respuesta': '¿De qué módulo quieres saber el conteo? Puedo consultarte: guiones, inventario, contratos, patrocinadores, premios, tareas, reels o usuarios.',
                'intencion': 'contar',
                'confianza': 0.5,
            }

        modulo = intencion['modulos'][0]
        try:
            if modulo == 'guiones':
                from app.model.guion_model import GuionModel
                total = GuionModel().contar()
                return {'respuesta': f'Hay **{total}** guion(es) registrado(s) en el sistema.', 'intencion': 'contar_guiones', 'confianza': 0.95}

            if modulo == 'inventario':
                from app.model.inventario_model import InventarioModel
                datos = InventarioModel().consultar()
                total = len(datos)
                disponibles = sum(1 for d in datos if d.get('estado_nombre') == 'Disponible')
                return {'respuesta': f'Hay **{total}** activo(s) en inventario. **{disponibles}** están disponibles.', 'intencion': 'contar_inventario', 'confianza': 0.95}

            if modulo == 'contratos':
                from app.model.contrato_model import ContratoModel
                contratos = ContratoModel().consultar()
                total = len(contratos)
                vigentes = sum(1 for c in contratos if c.get('estatus') == 'Vigente')
                vencidos = sum(1 for c in contratos if c.get('estatus') == 'Vencido')
                borrador = sum(1 for c in contratos if c.get('estatus') == 'Borrador')
                return {'respuesta': f'Hay **{total}** contrato(s): **{vigentes}** vigentes, **{vencidos}** vencidos, **{borrador}** en borrador.', 'intencion': 'contar_contratos', 'confianza': 0.95}

            if modulo == 'patrocinadores':
                from app.model.patrocinador_model import PatrocinadorModel
                datos = PatrocinadorModel().consultar()
                return {'respuesta': f'Hay **{len(datos)}** patrocinador(es) registrado(s).', 'intencion': 'contar_patrocinadores', 'confianza': 0.95}

            if modulo == 'premios':
                from app.model.premio_model import PremioModel
                datos = PremioModel().consultar()
                return {'respuesta': f'Hay **{len(datos)}** premio(s) registrado(s).', 'intencion': 'contar_premios', 'confianza': 0.95}

            if modulo == 'tareas':
                from app.model.tarea_model import TareasAsignadasModel
                if usuario:
                    pendientes = TareasAsignadasModel().contar_pendientes(usuario.id)
                    return {'respuesta': f'Tienes **{pendientes}** tarea(s) pendiente(s).', 'intencion': 'contar_tareas', 'confianza': 0.95}
                total = len(TareasAsignadasModel().consultar())
                return {'respuesta': f'Hay **{total}** tarea(s) asignada(s) en el sistema.', 'intencion': 'contar_tareas', 'confianza': 0.9}

            if modulo == 'reels':
                from app.model.reels_model import ReelModel
                datos = ReelModel().consultar()
                return {'respuesta': f'Hay **{len(datos)}** reel(s) registrado(s).', 'intencion': 'contar_reels', 'confianza': 0.95}

            if modulo == 'usuarios':
                from app.model.auth_model import UsuarioModel
                datos = UsuarioModel().consultar()
                activos = sum(1 for u in datos if u.get('activo'))
                return {'respuesta': f'Hay **{len(datos)}** usuario(s): **{activos}** activo(s).', 'intencion': 'contar_usuarios', 'confianza': 0.95}

            if modulo == 'bitacora':
                from app.model.bitacora_model import ActividadModel
                hoy = datetime.now().strftime('%Y-%m-%d')
                datos = ActividadModel().consultar(fecha_desde=hoy, limite=100)
                return {'respuesta': f'Hay **{len(datos)}** registro(s) de actividad de hoy.', 'intencion': 'contar_bitacora', 'confianza': 0.9}

            if modulo == 'balance':
                from app.model.balance_model import Pago
                pagos = Pago().consultar()
                total = sum(float(p.monto) for p in pagos if p.monto)
                return {'respuesta': f'Hay **{len(pagos)}** pago(s) registrado(s) por un total de **${total:,.2f}**.', 'intencion': 'contar_balance', 'confianza': 0.9}

        except Exception:
            logger.exception('Error no controlado')
            return {'respuesta': f'No pude obtener los datos de **{modulo}** en este momento. Intenta de nuevo.', 'intencion': 'error', 'confianza': 0.3}

        return {'respuesta': f'El módulo **{modulo}** no está disponible para conteo.', 'intencion': 'contar', 'confianza': 0.4}

    @classmethod
    def _responder_estados(cls, intencion):
        if not intencion['modulos']:
            return {
                'respuesta': '¿De qué módulo quieres conocer los estados? Puedo consultarte: contratos, inventario, guiones o tareas.',
                'intencion': 'estados',
                'confianza': 0.5,
            }

        modulo = intencion['modulos'][0]
        try:
            if modulo == 'contratos':
                from app.model.contrato_model import ContratoModel
                contratos = ContratoModel().consultar()
                vigentes = [c for c in contratos if c.get('estatus') == 'Vigente']
                vencidos = [c for c in contratos if c.get('estatus') == 'Vencido']
                borrador = [c for c in contratos if c.get('estatus') == 'Borrador']
                resp = f'**Contratos por estado:**\n'
                resp += f'- Vigentes: **{len(vigentes)}**\n'
                resp += f'- Vencidos: **{len(vencidos)}**\n'
                resp += f'- Borrador: **{len(borrador)}**'
                if vencidos:
                    resp += '\n\n⚠️ Tienes contratos vencidos que podrían necesitar atención.'
                return {'respuesta': resp, 'intencion': 'estados_contratos', 'confianza': 0.95}

            if modulo == 'inventario':
                from app.model.inventario_model import InventarioModel
                datos = InventarioModel().consultar()
                estados = {}
                for d in datos:
                    e = d.get('estado_nombre', 'Desconocido')
                    estados[e] = estados.get(e, 0) + 1
                resp = '**Activos por estado:**\n'
                for e, c in sorted(estados.items()):
                    resp += f'- {e}: **{c}**\n'
                return {'respuesta': resp, 'intencion': 'estados_inventario', 'confianza': 0.95}

            if modulo == 'guiones':
                from app.model.guion_model import GuionModel
                borrador = GuionModel().contar(estado='Borrador')
                publicado = GuionModel().contar(estado='Publicado')
                return {'respuesta': f'**Guiones por estado:**\n- Borrador: **{borrador}**\n- Publicados: **{publicado}**', 'intencion': 'estados_guiones', 'confianza': 0.95}

            if modulo == 'mantenimiento':
                from app.model.mantenimiento_model import RecursoModel
                recursos = RecursoModel().consultar()
                estados = {}
                for r in recursos:
                    e = r.get('estado_nombre', 'Desconocido')
                    estados[e] = estados.get(e, 0) + 1
                resp = '**Recursos por estado:**\n'
                for e, c in sorted(estados.items()):
                    resp += f'- {e}: **{c}**\n'
                return {'respuesta': resp, 'intencion': 'estados_mantenimiento', 'confianza': 0.95}

        except Exception:
            logger.exception('Error no controlado')
            return {'respuesta': f'No pude obtener los estados de **{modulo}**. Intenta de nuevo.', 'intencion': 'error', 'confianza': 0.3}

        return {'respuesta': f'El módulo **{modulo}** no tiene estados configurados para consulta.', 'intencion': 'estados', 'confianza': 0.4}

    @classmethod
    def _responder_reciente(cls, intencion, usuario):
        try:
            from app.model.bitacora_model import ActividadModel
            hoy = datetime.now().strftime('%Y-%m-%d')
            registros = ActividadModel().consultar(fecha_desde=hoy, limite=10)

            if not registros:
                return {'respuesta': 'No hay actividad registrada hoy.', 'intencion': 'reciente', 'confianza': 0.9}

            resp = '**Actividad de hoy:**\n'
            for r in registros[:8]:
                nombre = r.get('usuario', {})
                if isinstance(nombre, dict):
                    nombre = nombre.get('nombre', 'Usuario')
                accion = r.get('accion', r.get('tipo_accion', ''))
                modulo = r.get('modulo', '')
                resp += f'- **{nombre}** — {accion} ({modulo})\n'

            if len(registros) > 8:
                resp += f'\n_y {len(registros) - 8} registro(s) más._'

            return {'respuesta': resp, 'intencion': 'reciente', 'confianza': 0.9}

        except Exception:
            logger.exception('Error no controlado')
            return {'respuesta': 'No pude obtener la actividad reciente.', 'intencion': 'error', 'confianza': 0.3}

    @classmethod
    def _responder_contexto_cruzado(cls, msg, intencion, usuario):
        modulos = intencion['modulos']

        if 'patrocinadores' in modulos and 'contratos' in modulos:
            try:
                from app.model.patrocinador_model import PatrocinadorModel
                from app.model.contrato_model import ContratoModel
                patrocinadores = PatrocinadorModel().consultar()
                contratos = ContratoModel().consultar()
                con_vigente = set()
                for c in contratos:
                    if c.get('estatus') == 'Vigente':
                        con_vigente.add(c.get('id_patrocinador'))
                total_con_vigente = sum(1 for p in patrocinadores if p.get('id_patrocinador') in con_vigente)
                return {
                    'respuesta': f'Hay **{len(patrocinadores)}** patrocinador(es) en total. **{total_con_vigente}** tienen contrato(s) vigente(s).',
                    'intencion': 'cruzado_patrocinadores_contratos',
                    'confianza': 0.9,
                }
            except Exception:
                logger.exception('Error no controlado')
                return {'respuesta': 'No pude cruzar los datos de patrocinadores y contratos.', 'intencion': 'error', 'confianza': 0.3}

        if 'tareas' in modulos and 'usuarios' in modulos:
            try:
                from app.model.tarea_model import TareasAsignadasModel
                todas = TareasAsignadasModel().consultar_todas()
                pendientes = [t for t in todas if t.get('Estado') != 'Completada']
                return {
                    'respuesta': f'Hay **{len(pendientes)}** tarea(s) pendiente(s) asignada(s) a usuarios en el sistema.',
                    'intencion': 'cruzado_tareas_usuarios',
                    'confianza': 0.9,
                }
            except Exception:
                logger.exception('Error no controlado')
                return {'respuesta': 'No pude cruzar los datos de tareas y usuarios.', 'intencion': 'error', 'confianza': 0.3}

        resp = f'Puedo consultarte individualmente sobre: **{"**, **".join(modulos)}**. Dime cuál te interesa y te doy los datos.'
        return {'respuesta': resp, 'intencion': 'contexto_cruzado', 'confianza': 0.5}

    @classmethod
    def _responder_default(cls, msg):
        return {
            'respuesta': 'No estoy segura de entender tu pregunta. Puedo ayudarte con:\n'
                         '- **Conteos**: "¿Cuántos guiones hay?"\n'
                         '- **Estados**: "¿Qué contratos están vigentes?"\n'
                         '- **Actividad**: "¿Qué hicieron los usuarios hoy?"\n'
                         '- **Guías**: "¿Cómo creo un guion?"\n\n'
                         'Intenta reformular tu pregunta.',
            'intencion': 'default',
            'confianza': 0.2,
        }
