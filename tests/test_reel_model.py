import pytest
from unittest.mock import MagicMock, patch

from app.model.reels_model import ReelModel, VideoModel


# Evita que se ejecute la fixture de conftest.py
# que intenta crear las bases de datos reales de prueba.
@pytest.fixture(scope="session", autouse=True)
def bases_de_prueba():
    yield


def test_nombre_vacio_no_es_valido():
    reel = ReelModel()

    resultado = reel._validar_nombre("")

    assert resultado is False


def test_nombre_correcto_es_valido():
    reel = ReelModel()

    resultado = reel._validar_nombre("Mi primer reel")

    assert resultado is True


@patch("app.model.reel_model.Database.get_connection")
def test_consultar_videos_por_reel(mock_conexion):
    videos = [
        {"id": 1, "nombre": "Video de prueba", "reel_id": 5}
    ]

    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = videos
    mock_conexion.return_value = db

    modelo = VideoModel()
    resultado = modelo.consultar_por_reel(5)

    assert resultado == videos
    cursor.execute.assert_called_once()


@patch("app.model.reel_model.Database.get_connection")
def test_registrar_video(mock_conexion):
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.lastrowid = 10
    mock_conexion.return_value = db

    modelo = VideoModel()

    datos = {
        "nombre": "Video nuevo",
        "duracion_segundos": 30,
        "orden": 1,
        "reel_id": 5,
        "id_patrocinador": None
    }

    resultado = modelo.registrar(datos)

    assert resultado["id"] == 10
    assert resultado["nombre"] == "Video nuevo"
    cursor.execute.assert_called_once()


@patch("app.model.reel_model.Database.get_connection")
def test_eliminar_video(mock_conexion):
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    mock_conexion.return_value = db

    modelo = VideoModel()
    modelo.eliminar(10)

    cursor.execute.assert_called_once_with(
        "DELETE FROM videos WHERE id = %s",
        (10,)
    )