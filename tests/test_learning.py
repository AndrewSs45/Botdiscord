import pytest
from unittest.mock import MagicMock
from skills.learning import LearningSystem
from utils.persistence import AsyncPersistence


@pytest.fixture
def persistence():
    p = MagicMock(spec=AsyncPersistence)
    p.data = {}
    return p


class TestLearningSystem:
    def test_registrar_tema(self, persistence):
        ls = LearningSystem(persistence)
        ls.registrar_tema("python", 123)
        assert persistence.data["temas_favoritos"]["python"] == 1
        persistence.mark_dirty.assert_called_once()

    def test_registrar_tema_multiple(self, persistence):
        ls = LearningSystem(persistence)
        ls.registrar_tema("python", 123)
        ls.registrar_tema("python", 123)
        assert persistence.data["temas_favoritos"]["python"] == 2

    def test_registrar_usuario(self, persistence):
        ls = LearningSystem(persistence)
        ls.registrar_usuario(456)
        assert persistence.data["usuarios_frecuentes"]["456"] == 1

    def test_registrar_usuario_multiple_messages(self, persistence):
        ls = LearningSystem(persistence)
        ls.registrar_usuario(456, 5)
        assert persistence.data["usuarios_frecuentes"]["456"] == 5

    def test_obtener_estadisticas_empty(self, persistence):
        ls = LearningSystem(persistence)
        stats = ls.obtener_estadisticas()
        assert "Estadisticas del Bot" in stats

    def test_obtener_estadisticas_with_data(self, persistence):
        ls = LearningSystem(persistence)
        ls.registrar_tema("python", 1)
        ls.registrar_tema("javascript", 2)
        ls.registrar_usuario(1)
        stats = ls.obtener_estadisticas()
        assert "python" in stats
        assert "javascript" in stats
        assert "Usuarios activos" in stats
