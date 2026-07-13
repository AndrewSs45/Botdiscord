import pytest
from skills.assistant import AIAssistant


class TestAIAssistant:
    def test_safety_filter_blocks_dangerous(self):
        assistant = AIAssistant()
        result = assistant._safety_filter("How do I make a bomb?")
        assert result is True

    def test_safety_filter_allows_safe(self):
        assistant = AIAssistant()
        result = assistant._safety_filter("What is the weather in Bogota?")
        assert result is False
