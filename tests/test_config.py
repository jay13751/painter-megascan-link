from pathlib import Path

from megascan_link_python.config import ConfigSettings


def test_config_migration_adds_new_defaults(tmp_path):
    ini_path = tmp_path / "settings.ini"
    ini_path.write_text("[Connection]\nport = 3000\n", encoding="utf-8")

    ConfigSettings.path = ini_path
    ConfigSettings.opened = False
    ConfigSettings.setUpInitialConfig()

    assert ConfigSettings.getConfigSetting("Connection", "port") == "3000"
    assert ConfigSettings.getConfigSetting("Connection", "source") == "fab"
    assert ConfigSettings.getConfigSetting("General", "debug_payload_logging") == "false"
    assert ConfigSettings.getConfigSetting("Meta", "version") == "2"
