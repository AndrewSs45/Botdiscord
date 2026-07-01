import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime

from utils.logger import setup_logger

log = logging.getLogger("persistence")


class AsyncPersistence:
    """Persistencia asíncrona con guardado automático periódico.

    Acumula cambios en memoria y los escribe a disco cada
    ``save_interval`` segundos o ante una llamada explícita a
    :meth:`save`. Usa escritura atómica (archivo temporal + rename).

    Args:
        file_path: Ruta al archivo JSON de persistencia.
        default_factory: Diccionario por defecto si el archivo no existe.
        save_interval: Segundos entre guardados automáticos.
    """

    def __init__(self, file_path: str, default_factory: dict, save_interval: int = 30):
        self._file = Path(file_path)
        self._default_factory = default_factory
        self._interval = save_interval
        self._data: dict = self._load()
        self._dirty = False
        self._task: asyncio.Task | None = None

    # -- Public API --

    @property
    def data(self) -> dict:
        """Acceso directo al diccionario de datos en memoria."""
        return self._data

    def mark_dirty(self):
        """Marca los datos como modificados para que se guarden."""
        self._dirty = True

    def save(self):
        """Guarda los datos a disco si hay cambios pendientes (síncrono)."""
        if not self._dirty:
            return
        self._flush()

    async def save_async(self):
        """Guarda los datos a disco en un executor (no bloquea el event loop)."""
        if not self._dirty:
            return
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._flush)

    def start_auto_save(self):
        """Inicia el loop de guardado automático en background."""
        loop = asyncio.get_event_loop()
        self._task = loop.create_task(self._auto_save_loop())

    async def stop_auto_save(self):
        """Detiene el loop de guardado automático y fuerza un guardado final."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            await self.save_async()

    # -- Internal --

    def _load(self) -> dict:
        if self._file.exists():
            try:
                with open(self._file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return dict(self._default_factory)

    def _flush(self):
        self._file.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._file.with_suffix(".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            tmp.replace(self._file)
            self._dirty = False
        except OSError as e:
            log.error("Error persistiendo %s: %s", self._file.name, e)

    async def _auto_save_loop(self):
        try:
            while True:
                await asyncio.sleep(self._interval)
                await self.save_async()
        except asyncio.CancelledError:
            await self.save_async()
            raise


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")
