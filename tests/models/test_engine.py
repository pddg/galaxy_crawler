import pytest

from unittest.mock import call, patch

from galaxy_crawler.models import engine


class TestEngineType(object):

    @pytest.mark.parametrize(
        "engine_type, url", [
            (engine.EngineType.IN_MEMORY, "sqlite://"),
            (engine.EngineType.POSTGRES, "postgresql://user:pass@localhost:5432/db"),
            (engine.EngineType.POSTGRES, "postgresql://user@localhost:5432/db"),
            (engine.EngineType.POSTGRES, "postgresql://192.168.1.2:5432/db"),
            (engine.EngineType.POSTGRES, "postgresql://db.example.com:5432/db"),
            (engine.EngineType.SQLITE, "sqlite:///sqlite3.db"),
            (engine.EngineType.SQLITE, "sqlite:////path/to/sqlite3.db"),
        ]
    )
    def test_valid_url(self, engine_type, url):
        expected = "mocked_engine"
        with patch("galaxy_crawler.models.engine.create_engine", return_value=expected) as patched:
            e = engine_type.get_engine(url)
            assert e == expected
            assert patched.mock_calls[0], call(url)

    @pytest.mark.parametrize(
        "engine_type, url", [
            (engine.EngineType.IN_MEMORY, "sqlite:///sqlite3.db"),
            (engine.EngineType.IN_MEMORY, "sqlite:///"),
            (engine.EngineType.POSTGRES, "postgresql:///localhost:5432/db"),
            (engine.EngineType.POSTGRES, "postgresql://localhost/db"),
            (engine.EngineType.POSTGRES, "postgresql://localhost"),
            (engine.EngineType.SQLITE, "sqlite://sqlite3.db"),
            (engine.EngineType.SQLITE, "sqlite://"),
        ]
    )
    def test_invalid_url(self, engine_type, url):
        with pytest.raises(engine.InvalidUrlError):
            engine_type.get_engine(url)


