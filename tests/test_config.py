from pathlib import Path

from f1_telemetry_analyzer.config import Config


def test_config_has_expected_default_paths():
    config = Config()
    project_folder = Path(__file__).resolve().parent.parent

    assert config.project_folder == project_folder
    assert config.cache_folder == project_folder / "cache"
    assert config.output_folder == project_folder / "grafikoni"
    assert config.minimum_season == 2018


def test_config_paths_follow_project_folder():
    config = Config(project_folder=Path("projekat"))

    assert config.cache_folder == Path("projekat") / "cache"
    assert config.output_folder == Path("projekat") / "grafikoni"
