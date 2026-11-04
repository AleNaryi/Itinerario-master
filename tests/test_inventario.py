import pytest
from unittest.mock import MagicMock

from app.model.inventario_model import InventarioModel, TipoRecursoModel

def preparar_recurso_valido():
    """Crea un recurso con los campos obligatorios para las pruebas."""
    inventario = InventarioModel()
    inventario.set_nombre("Laptop")
    inventario.set_id_tipo(1)
    inventario.set_descripcion("Equipo portátil para oficina")
    inventario.set_costo(850)
    return inventario

def preparar_db_simulada(monkeypatch, modelo, rowcount=1):
    """
    Simula la conexión y el cursor de MySQL.
    Las pruebas no se conectan a la base de datos real.
    """
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.rowcount = rowcount

    monkeypatch.setattr(modelo, "_get_db", lambda: db)
    return db, cursor


# ---------- PRUEBAS DE InventarioModel ----------

def test_validar_recurso_con_datos_correctos():
    inventario = preparar_recurso_valido()

    assert inventario._validar_datos_recurso() is True

def test_rechazar_recurso_sin_nombre():
    inventario = InventarioModel()
    inventario.set_id_tipo(1)

    assert inventario._validar_datos_recurso() is False

def test_rechazar_tipo_de_recurso_no_positivo():
    inventario = InventarioModel()
    inventario.set_nombre("Laptop")
    inventario.set_id_tipo(0)

    assert inventario._validar_datos_recurso() is False

def test_rechazar_costo_no_numerico():
    inventario = preparar_recurso_valido()
    inventario.set_costo("no es un numero")

    assert inventario._validar_datos_recurso() is False

def test_registrar_recurso_correctamente(monkeypatch):
    inventario = preparar_recurso_valido()
    db, cursor = preparar_db_simulada(monkeypatch, inventario, rowcount=1)

    resultado = inventario.confirmar_registro()

    assert resultado is True
    cursor.execute.assert_called_once()
    db.cursor.assert_called_once()


def test_no_confirmar_registro_si_falla_la_validacion(monkeypatch):
    inventario = InventarioModel()
    db, cursor = preparar_db_simulada(monkeypatch, inventario)

    resultado = inventario.confirmar_registro()

    assert resultado is False
    cursor.execute.assert_not_called()
    db.cursor.assert_not_called()


def test_consultar_recursos_devuelve_resultados(monkeypatch):
    inventario = InventarioModel()
    db, cursor = preparar_db_simulada(monkeypatch, inventario)
    recursos = [{"id": 1, "nombre": "Laptop"}]
    cursor.fetchall.return_value = recursos

    resultado = inventario.consultar()

    assert resultado == recursos
    cursor.execute.assert_called_once()


def test_consultar_filtrando_por_tipo_y_estado(monkeypatch):
    inventario = InventarioModel()
    _, cursor = preparar_db_simulada(monkeypatch, inventario)
    cursor.fetchall.return_value = []

    inventario.consultar(tipo_id=2, estado_id=1)

    consulta_sql, parametros = cursor.execute.call_args.args
    assert "r.tipo_id = %s" in consulta_sql
    assert "r.estado_id = %s" in consulta_sql
    assert parametros == [2, 1]


def test_buscar_recurso_por_id(monkeypatch):
    inventario = InventarioModel()
    _, cursor = preparar_db_simulada(monkeypatch, inventario)
    recurso = {"id": 7, "nombre": "Proyector"}
    cursor.fetchone.return_value = recurso

    resultado = inventario.obtener_por_id(7)

    assert resultado == recurso
    cursor.execute.assert_called_once()
    assert cursor.execute.call_args.args[1] == (7,)


def test_eliminar_recurso_logicamente(monkeypatch):
    inventario = InventarioModel()
    _, cursor = preparar_db_simulada(monkeypatch, inventario, rowcount=1)

    resultado = inventario.confirmar_eliminacion(7)

    assert resultado is True
    consulta_sql, parametros = cursor.execute.call_args.args
    assert "eliminado = 1" in consulta_sql
    assert parametros == (7,)


def test_cambiar_estado_del_recurso(monkeypatch):
    inventario = InventarioModel()
    _, cursor = preparar_db_simulada(monkeypatch, inventario, rowcount=1)

    resultado = inventario.cambiar_estado(7, 2)

    assert resultado is True
    assert cursor.execute.call_args.args[1] == (2, 7)


# ---------- PRUEBAS DE TipoRecursoModel ----------

def test_validar_tipo_de_recurso_correcto():
    tipo = TipoRecursoModel()
    tipo.set_nombre_tipo("Mobiliario")

    assert tipo._validar_datos_recurso() is True


def test_rechazar_tipo_de_recurso_sin_nombre():
    tipo = TipoRecursoModel()

    assert tipo._validar_datos_recurso() is False


def test_registrar_tipo_de_recurso(monkeypatch):
    tipo = TipoRecursoModel()
    tipo.set_nombre_tipo("Mobiliario")
    tipo.set_descripcion_tipo("Muebles y equipos")

    _, cursor = preparar_db_simulada(monkeypatch, tipo, rowcount=1)

    resultado = tipo.confirmar_registro()

    assert resultado is True
    cursor.execute.assert_called_once()
