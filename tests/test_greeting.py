import pytest
from skills.greeting import is_greeting


class TestGreeting:
    @pytest.mark.parametrize("message,expected", [
        ("hola", True),
        ("HOLA", True),
        ("hello", True),
        ("buenos días", True),
        ("que tal", True),
        ("adiós", False),
        ("!ping", False),
    ])
    def test_is_greeting(self, message: str, expected: bool):
        assert is_greeting(message) == expected
