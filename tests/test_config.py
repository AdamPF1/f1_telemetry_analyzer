from pathlib import Path

from f1_telemetry_analyzer.config import Config


def test_config_has_expected_default_paths():
    config = Config()

    assert config.cache_folder == Path("cache")
    assert config.output_folder == Path("grafikoni")
    assert config.minimum_season == 2018
