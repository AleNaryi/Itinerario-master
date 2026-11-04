"""Tests de validaciones puras — sin BD, sin app."""
from app.model.validaciones_model import ValidacionesMixin


class V(ValidacionesMixin):
    pass


def _nuevo():
    return V()


def test_obligatorio_rechaza_vacio_y_espacios():
    v = _nuevo()
    assert not v.validar_obligatorio('', 'x')
    assert not v.validar_obligatorio('   ', 'x')
    assert not v.validar_obligatorio(None, 'x')
    assert v.validar_obligatorio('dato', 'x')


def test_obligatorios_acumula_errores():
    v = _nuevo()
    assert not v.validar_obligatorios(['a', 'b'], {'a': 'ok'})
    assert len(v.get_errores()) == 1
    # 0 y False cuentan como presentes
    assert v.validar_obligatorios(['cero'], {'cero': 0})


def test_entero_positivo():
    v = _nuevo()
    assert v.validar_entero_positivo('5', 'n')
    assert not v.validar_entero_positivo(0, 'n')
    assert not v.validar_entero_positivo(-3, 'n')
    assert not v.validar_entero_positivo('abc', 'n')
    assert not v.validar_entero_positivo(None, 'n')


def test_fecha_formato_y_realidad():
    v = _nuevo()
    assert v.validar_fecha('2024-01-15')
    assert not v.validar_fecha('15/01/2024')      # formato incorrecto
    assert not v.validar_fecha('2024-02-30')      # fecha inexistente
    assert not v.validar_fecha(None)


def test_texto_prohibido_y_sanitizacion():
    v = _nuevo()
    assert not v.validar_texto('<script>', 'campo')
    assert v.validar_texto('Texto normal 123', 'campo')
    # elimina < > / y recorta bordes (comportamiento actual)
    assert ValidacionesMixin.sanitizar_texto(" <b>hola</b> ") == 'bholab'


def test_longitud():
    v = _nuevo()
    assert v.validar_longitud('abc', 1, 10, 'campo')
    assert not v.validar_longitud('', 1, 10, 'campo')
    assert not v.validar_longitud('x' * 11, 1, 10, 'campo')


def test_email_formato_opcional():
    v = _nuevo()
    assert v.validar_email('correo@dominio.com')
    assert not v.validar_email('no-es-correo')
    assert v.validar_email(None)   # opcional: vacío pasa
    assert v.validar_email('')


def test_rif_formato():
    v = _nuevo()
    assert v.validar_rif('J-12345678')
    assert v.validar_rif('j12345678')
    assert not v.validar_rif('X-12345678')
    assert not v.validar_rif('J-123')
    assert not v.validar_rif(None)


def test_contrato_rechaza_datos_invalidos_sin_explotar():
    # Regresión C1: antes self._errores lanzaba AttributeError en vez de devolver False
    from app.model.contrato_model import ContratoModel

    m = ContratoModel()
    m.set_id_patrocinador(1)
    m.set_fecha_inicio('2024-01-10')
    m.set_fecha_fin('2024-01-01')          # fin < inicio
    m.set_tipo('1')
    assert m.confirmar_registro() is False
    assert m.tiene_errores()

    m2 = ContratoModel()
    m2.set_id_patrocinador(1)
    m2.set_fecha_inicio('15/01/2024')      # formato inválido
    m2.set_fecha_fin('2024-02-01')
    m2.set_tipo('1')
    assert m2.confirmar_registro() is False

    m3 = ContratoModel()
    m3.set_id_patrocinador(1)
    m3.set_fecha_inicio('2024-01-10')
    m3.set_fecha_fin('2024-02-01')
    m3.set_tipo('1')
    m3.set_monto_total('abc')              # monto no numérico
    assert m3.confirmar_registro() is False


def test_balance_validar_monto():
    from app.model.balance_model import Pago
    p = Pago()
    assert p.validar_monto(10)
    assert p.validar_monto('9.99')
    assert not p.validar_monto(-5)
    assert not p.validar_monto(0)
    assert not p.validar_monto('abc')


def test_reel_registrar_modificar_validan_nombre():
    # Regresión C3: registrar/modificar ignoraban la validación del modelo
    from app.model.reels_model import ReelModel
    r = ReelModel()
    assert r.registrar({'nombre': ''}) is None
    assert r.registrar({'nombre': 'x'}) is None        # < 2 caracteres
    assert r.modificar(1, {'nombre': ''}) is None


def test_inventario_costo_invalido_rechazado():
    # Regresión C5: el costo llegaba crudo al INSERT
    from app.model.inventario_model import InventarioModel

    i = InventarioModel()
    i.set_nombre('Silla')
    i.set_descripcion('Silla de plástico')
    i.set_id_tipo(1)
    i.set_costo('abc')
    assert i.confirmar_registro() is False
    assert any('Costo' in e for e in i.get_errores())

    i2 = InventarioModel()
    i2.set_nombre('Silla')
    i2.set_descripcion('Silla de plástico')
    i2.set_id_tipo(1)
    i2.set_costo('-5')
    assert i2.confirmar_registro() is False

    # costo vacío sigue siendo válido (opcional)
    i3 = InventarioModel()
    i3.set_nombre('Silla')
    i3.set_descripcion('Silla de plástico')
    i3.set_id_tipo(1)
    i3.set_costo(None)
    assert i3._validar_datos_recurso() is True


def test_premio_rechaza_patrocinador_crudo_y_descripcion_larga():
    # M3: id_patrocinador llegaba crudo al INSERT y descripcion sin límite
    from app.model.premio_model import PremioModel

    p = PremioModel()
    p.set_nombre('Bate firmado')
    p.set_id_patrocinador('abc')
    assert p._validar_datos_premio() is False
    assert any('Patrocinador' in e for e in p.get_errores())

    p2 = PremioModel()
    p2.set_nombre('Bate firmado')
    p2.set_id_patrocinador(3)
    p2.set_descripcion('x' * 501)
    assert p2._validar_datos_premio() is False

    p3 = PremioModel()
    p3.set_nombre('Bate firmado')
    p3.set_id_patrocinador('3')
    p3.set_descripcion('Para el fanático del juego')
    assert p3._validar_datos_premio() is True


def test_mantenimiento_fecha_ingreso_valida_formato_real():
    # M4: antes solo exigía "no vacío", cualquier basura llegaba a la BD
    from app.model.mantenimiento_model import MantenimientoModel

    m = MantenimientoModel()
    m.set_recurso_id(1)
    m.set_usuario_id(1)
    m.set_fecha_ingreso('15/01/2024')
    m.set_diagnostico('Pantalla rajada de un costado')
    assert m._validar_datos_mantenimiento() is False

    m2 = MantenimientoModel()
    m2.set_recurso_id(1)
    m2.set_usuario_id(1)
    m2.set_fecha_ingreso('2024-01-15')
    m2.set_diagnostico('Pantalla rajada de un costado')
    assert m2._validar_datos_mantenimiento() is True
