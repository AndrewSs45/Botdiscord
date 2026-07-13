import pytest
from skills.time_skill import get_time_for_timezone


class TestTimeSkill:
    def test_valid_timezone(self):
        result = get_time_for_timezone("America/Bogota")
        assert "America/Bogota" in result or "UTC" in result or "Bogota" in result

    def test_invalid_timezone_returns_helpful_message(self):
        result = get_time_for_timezone("Invalid/Zone")
        assert "error" in result.lower() or "invalid" in result.lower() or "not found" in result.lower()
