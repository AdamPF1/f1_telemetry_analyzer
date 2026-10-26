from datetime import timedelta

import numpy as np
import pandas as pd
import pytest

from f1_telemetry_analyzer.analysis import Analyzer


class FakeUI:
    def __init__(self):
        self.errors = []

    def error(self, message):
        self.errors.append(message)

    def loading_error(self, error):
        self.errors.append(str(error))

    def section(self, title):
        return title


class FakeLap(dict):
    empty = False

    def get_telemetry(self):
        return pd.DataFrame({"Speed": [250.0, 310.0], "Throttle": [80.0, 100.0], "Brake": [1, 0]})


class FakeLaps:
    def __init__(self, lap):
        self.lap = lap
        self.empty = lap is None

    def pick_fastest(self):
        return self.lap


class FakeSession:
    def __init__(self, laps):
        self.laps = self
        self.driver_laps = laps

    def pick_drivers(self, driver):
        return FakeLaps(self.driver_laps.get(driver))


def lap(seconds, compound="SOFT", position=1.0):
    return FakeLap(
        LapNumber=10, LapTime=timedelta(seconds=seconds), Compound=compound, Position=position
    )


def sector_lap(first, second, third):
    return FakeLap(
        Sector1Time=timedelta(seconds=first),
        Sector2Time=timedelta(seconds=second),
        Sector3Time=timedelta(seconds=third),
    )


def test_sector_differences_subtracts_second_lap_from_first():
    differences = Analyzer.sector_differences(sector_lap(30, 40, 20), sector_lap(30.5, 39.8, 20))

    assert differences == {"S1": -0.5, "S2": pytest.approx(0.2), "S3": 0}


def test_sector_differences_skips_missing_sector_times():
    first = sector_lap(30, 40, 20)
    first["Sector2Time"] = pd.NaT

    assert set(Analyzer.sector_differences(first, sector_lap(30, 40, 20))) == {"S1", "S3"}


def test_show_sector_differences_prints_faster_driver_per_sector(capsys):
    Analyzer(FakeUI()).show_sector_differences(
        sector_lap(30, 40, 20), sector_lap(30.5, 39.8, 20), "VER", "HAM"
    )

    output = capsys.readouterr().out
    assert "S1  : VER brži za 0.500s" in output
    assert "S2  : HAM brži za 0.200s" in output


def test_show_sector_differences_reports_missing_data():
    ui = FakeUI()
    empty = FakeLap(Sector1Time=pd.NaT, Sector2Time=pd.NaT, Sector3Time=pd.NaT)

    Analyzer(ui).show_sector_differences(empty, empty, "VER", "HAM")

    assert ui.errors == ["Vremena po sektorima nisu dostupna."]


def test_faster_driver_returns_driver_and_positive_difference():
    faster, difference = Analyzer.faster_driver(lap(92), lap(90), "HAM", "VER")

    assert faster == "VER"
    assert difference == 2


def test_lap_data_returns_lap_and_telemetry():
    session = FakeSession({"VER": lap(90)})

    result = Analyzer(FakeUI()).lap_data(session, "VER")

    assert result is not None
    assert result[0]["LapTime"] == timedelta(seconds=90)
    assert result[1]["Speed"].max() == 310


def test_lap_data_reports_missing_driver_laps():
    ui = FakeUI()

    assert Analyzer(ui).lap_data(FakeSession({}), "HAM") is None
    assert ui.errors == ["Nema dostupnih krugova za ovog vozača."]


def test_lap_time_is_formatted_as_minutes_and_seconds():
    assert Analyzer.lap_time(timedelta(seconds=89.708)) == "1:29.708"
    assert Analyzer.lap_time(timedelta(seconds=65.04)) == "1:05.040"


def test_show_lap_skips_missing_compound_and_position(capsys):
    Analyzer(FakeUI()).show_lap(lap(90, compound=np.nan, position=np.nan), "VER")

    output = capsys.readouterr().out
    assert "1:30.000" in output
    assert "Gume" not in output
    assert "Pozicija" not in output
