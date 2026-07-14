import pytest
from unittest.mock import MagicMock
from skills.user_preferences import UserPreferences
from utils.persistence import AsyncPersistence


@pytest.fixture
def persistence():
    p = MagicMock(spec=AsyncPersistence)
    p.data = {}
    return p


class TestUserPreferences:
    def test_set_timezone_valid(self, persistence):
        up = UserPreferences(persistence)
        result = up.set_timezone(1, "UTC")
        assert "guardada" in result
        assert "UTC" in result
        persistence.mark_dirty.assert_called_once()

    def test_set_timezone_invalid(self, persistence):
        up = UserPreferences(persistence)
        result = up.set_timezone(1, "Invalid/Zone")
        assert "no válida" in result

    def test_get_timezone_not_set(self, persistence):
        up = UserPreferences(persistence)
        assert up.get_timezone(1) is None

    def test_get_timezone_after_set(self, persistence):
        up = UserPreferences(persistence)
        persistence.data["timezones"] = {"1": "America/New_York"}
        assert up.get_timezone(1) == "America/New_York"

    def test_get_current_time_for_no_timezone(self, persistence):
        up = UserPreferences(persistence)
        assert up.get_current_time_for(1) is None
