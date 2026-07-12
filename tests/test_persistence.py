import json
import asyncio
from pathlib import Path

import pytest

from utils.persistence import AsyncPersistence


@pytest.fixture
def tmp_file(tmp_path):
    return str(tmp_path / "test_data.json")


@pytest.mark.asyncio
async def test_persistence_load_default(tmp_file):
    p = AsyncPersistence(tmp_file, {"key": "value"})
    assert p.data == {"key": "value"}


@pytest.mark.asyncio
async def test_persistence_mark_dirty(tmp_file):
    p = AsyncPersistence(tmp_file, {})
    assert p._dirty is False
    p.mark_dirty()
    assert p._dirty is True


@pytest.mark.asyncio
async def test_persistence_save_and_load(tmp_file):
    p = AsyncPersistence(tmp_file, {})
    p.data["foo"] = "bar"
    p.mark_dirty()
    p.save()

    p2 = AsyncPersistence(tmp_file, {})
    assert p2.data["foo"] == "bar"


@pytest.mark.asyncio
async def test_persistence_save_async(tmp_file):
    p = AsyncPersistence(tmp_file, {})
    p.data["num"] = 42
    p.mark_dirty()
    await p.save_async()

    with open(tmp_file) as f:
        data = json.load(f)
    assert data["num"] == 42


@pytest.mark.asyncio
async def test_persistence_auto_save(tmp_file):
    p = AsyncPersistence(tmp_file, {}, save_interval=1)
    p.data["auto"] = "saved"
    p.mark_dirty()
    p.start_auto_save()

    await asyncio.sleep(1.5)
    await p.stop_auto_save()

    with open(tmp_file) as f:
        data = json.load(f)
    assert data["auto"] == "saved"


@pytest.mark.asyncio
async def test_now_iso():
    from utils.persistence import now_iso

    result = now_iso()
    assert "T" in result
