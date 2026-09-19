import io

import pytest
from PIL import Image

from app.config import Config


@pytest.fixture
def config():
    return {key: getattr(Config, key) for key in dir(Config) if key.isupper()}


@pytest.fixture
def make_jpeg():
    def _make(width=64, height=48, color=(200, 120, 80)):
        buffer = io.BytesIO()
        Image.new("RGB", (width, height), color).save(buffer, format="JPEG")
        return buffer.getvalue()

    return _make
