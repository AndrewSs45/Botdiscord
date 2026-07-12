from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from skills.weather import WeatherSkill
from skills.time_skill import TimeSkill
from skills.greeting import detectar_saludo


@pytest.mark.asyncio
async def test_weather_skill_success():
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.__aenter__.return_value = mock_response

    mock_geo_data = {
        "results": [
            {
                "name": "Madrid",
                "country": "España",
                "latitude": 40.4168,
                "longitude": -3.7038,
            }
        ]
    }
    mock_weather_data = {
        "current": {
            "temperature_2m": 22.5,
            "wind_speed_10m": 12.3,
        }
    }

    mock_response.json = AsyncMock(side_effect=[mock_geo_data, mock_weather_data])

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        skill = WeatherSkill()
        result = await skill.ejecutar("Madrid")

    assert "Madrid" in result
    assert "España" in result
    assert "22.5" in result
    assert "12.3" in result


@pytest.mark.asyncio
async def test_weather_skill_not_found():
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.__aenter__.return_value = mock_response
    mock_response.json = AsyncMock(return_value={"results": []})

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        skill = WeatherSkill()
        result = await skill.ejecutar("NonExistentCity")

    assert "Ciudad no encontrada" in result


@pytest.mark.asyncio
async def test_weather_skill_http_error():
    mock_response = AsyncMock()
    mock_response.status = 500
    mock_response.__aenter__.return_value = mock_response

    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        skill = WeatherSkill()
        result = await skill.ejecutar("Madrid")

    assert "Error" in result


@pytest.mark.asyncio
async def test_time_skill_with_timezone():
    skill = TimeSkill()
    result = await skill.ejecutar(timezone="Europe/Madrid")
    assert "Europe/Madrid" in result


@pytest.mark.asyncio
async def test_time_skill_invalid_timezone():
    skill = TimeSkill()
    result = await skill.ejecutar(timezone="Invalid/Zone")
    assert "no válida" in result or "not valid" in result or "invalid" in result.lower()


@pytest.mark.asyncio
async def test_time_skill_default():
    skill = TimeSkill()
    result = await skill.ejecutar()
    assert "Hora" in result or "hora" in result


def test_is_greeting_true():
    assert detectar_saludo("hola") is True
    assert detectar_saludo("Hola") is True
    assert detectar_saludo("buenas") is True
    assert detectar_saludo("hey") is True
    assert detectar_saludo("hello") is True
    assert detectar_saludo("HOLA") is True


def test_is_greeting_false():
    assert detectar_saludo("hola que tal") is False
    assert detectar_saludo("adios") is False
    assert detectar_saludo("como estas") is True
    assert detectar_saludo("") is False
