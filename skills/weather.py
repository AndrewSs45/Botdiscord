"""Skill de consulta meteorológica.

Utiliza la API pública Open-Meteo (sin clave API) para obtener
temperatura actual y velocidad del viento de cualquier ciudad.
"""
import aiohttp


class WeatherSkill:
    """Skill para obtener información del clima de una ciudad vía Open-Meteo."""

    def __init__(self):
        self.nombre = "Weather"
        self.descripcion = "Obtiene información del clima"

    async def ejecutar(self, ciudad: str) -> str:
        """Obtiene el clima actual de una ciudad.

        Realiza dos llamadas: una al geocoder para obtener coordenadas
        y otra al pronóstico para los datos meteorológicos actuales.

        Args:
            ciudad: Nombre de la ciudad a consultar.

        Returns:
            Cadena con temperatura y viento, o mensaje de error.
        """
        try:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={ciudad}&count=1&language=es&format=json"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        return "Error consultando el clima."
                    data = await resp.json()

                if not data.get("results"):
                    return "Ciudad no encontrada."

                location = data["results"][0]
                lat, lon = location["latitude"], location["longitude"]

                weather_url = (
                    f"https://api.open-meteo.com/v1/forecast?"
                    f"latitude={lat}&longitude={lon}&"
                    f"current=temperature_2m,weather_code,wind_speed_10m&"
                    f"temperature_unit=celsius&language=es"
                )

                async with session.get(weather_url) as wresp:
                    if wresp.status != 200:
                        return "Error consultando el clima."
                    weather_data = await wresp.json()
                    current = weather_data.get("current", {})

                    return (
                        f"**Clima en {location['name']}, {location.get('country', '')}**\n"
                        f"Temperatura: {current.get('temperature_2m', 'N/A')}°C\n"
                        f"Viento: {current.get('wind_speed_10m', 'N/A')} km/h"
                    )
        except Exception as e:
            return f"No se pudo obtener el clima: {e}"
