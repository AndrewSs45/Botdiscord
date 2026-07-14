import pytest
from unittest.mock import AsyncMock, patch
from skills.internet_search import InternetSearchSkill


@pytest.mark.asyncio
async def test_internet_search_success():
    mock_result = "**Resultados de búsqueda:**\n1. [Test Page](https://example.com) - A test page"
    with patch("skills.internet_search.buscar_en_internet", return_value=mock_result):
        skill = InternetSearchSkill()
        result = await skill.ejecutar("test query")
        assert "Test Page" in result
        assert "example.com" in result


@pytest.mark.asyncio
async def test_internet_search_no_results():
    with patch("skills.internet_search.buscar_en_internet", return_value="No se encontraron resultados."):
        skill = InternetSearchSkill()
        result = await skill.ejecutar("nonexistent")
        assert "No se encontraron resultados" in result


@pytest.mark.asyncio
async def test_internet_search_error():
    with patch("skills.internet_search.buscar_en_internet", return_value="Error al realizar la búsqueda."):
        skill = InternetSearchSkill()
        result = await skill.ejecutar("error")
        assert "Error" in result
