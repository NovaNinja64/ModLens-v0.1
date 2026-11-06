from modlens.core.config import load_config


def test_load_config_uses_safe_defaults(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    config = load_config()
    assert config.log_level == "INFO"
    assert config.database_file.name == "modlens.sqlite3"
    assert config.log_file.name == "modlens.log"
