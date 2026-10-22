from datetime import timedelta

import numpy as np
import pandas as pd

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
