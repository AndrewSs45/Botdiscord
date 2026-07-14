import pytest
from unittest.mock import MagicMock
from skills.command_tracker import CommandTracker
from utils.persistence import AsyncPersistence


@pytest.fixture
def persistence():
    p = MagicMock(spec=AsyncPersistence)
    p.data = {}
    return p


class TestCommandTracker:
    def test_registrar_comando(self, persistence):
        ct = CommandTracker(persistence)
        ct.registrar_comando("play", 123, "general")
        assert persistence.data["comandos"]["play"]["total"] == 1
        assert persistence.data["comandos"]["play"]["por_usuario"]["123"] == 1
        assert len(persistence.data["historial"]) == 1
        persistence.mark_dirty.assert_called_once()

    def test_registrar_comando_multiple_users(self, persistence):
        ct = CommandTracker(persistence)
        ct.registrar_comando("play", 123)
        ct.registrar_comando("play", 456)
        assert persistence.data["comandos"]["play"]["total"] == 2
        assert persistence.data["comandos"]["play"]["por_usuario"]["123"] == 1
        assert persistence.data["comandos"]["play"]["por_usuario"]["456"] == 1

    def test_obtener_stats_empty(self, persistence):
        ct = CommandTracker(persistence)
        stats = ct.obtener_stats()
        assert stats == ""

    def test_obtener_stats_with_data(self, persistence):
        ct = CommandTracker(persistence)
        ct.registrar_comando("play", 1)
        ct.registrar_comando("skip", 2)
        ct.registrar_comando("play", 3)
        stats = ct.obtener_stats()
        assert "play" in stats
        assert "skip" in stats
        assert "3" in stats
