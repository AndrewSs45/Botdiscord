import pytest
from skills.greeting import obtener_respuesta_saludo, is_greeting


class TestGreetingExtended:
    def test_obtener_respuesta_saludo_contains_name(self):
        result = obtener_respuesta_saludo("TestUser", "<@123>")
        assert "TestUser" in result

    def test_obtener_respuesta_saludo_not_empty(self):
        result = obtener_respuesta_saludo("User", "<@456>")
        assert len(result) > 0

    def test_is_greeting_edge_cases(self):
        assert is_greeting(" hola ") is True
        assert is_greeting("hola!") is True
        assert is_greeting("hola.") is True
        assert is_greeting("") is False
        assert is_greeting("   ") is False
        assert is_greeting("que tal") is True
        assert is_greeting("como estas") is True

    def test_is_greeting_case_insensitive(self):
        assert is_greeting("HOLA") is True
        assert is_greeting("Buenas") is True
        assert is_greeting("HELLO") is True

    def test_is_greeting_variants(self):
        assert is_greeting("qué tal") is True
        assert is_greeting("buen día") is True
        assert is_greeting("buenos días") is True
        assert is_greeting("saludos") is True
