from datetime import timedelta

from f1_telemetry_analyzer.analysis import Analyzer


class FakeUI:
    def error(self, message):
        pass

    def loading_error(self, error):
        pass


class FakeLap:
    empty = False

    def __init__(self, seconds):
        self.values = {"LapTime": timedelta(seconds=seconds)}

    def __getitem__(self, key):
        return self.values[key]

    def get_telemetry(self):
        return FakeTelemetry()


class FakeTelemetry:
    empty = False


class FakeLaps:
    empty = False

    def __init__(self, lap):
        self.lap = lap

    def pick_fastest(self):
        return self.lap


class FakeSession:
    def __init__(self):
        self.laps = self

    def pick_drivers(self, driver):
        return FakeLaps(FakeLap(90 if driver == "VER" else 92))


def test_compare_selects_faster_driver():
    result = Analyzer(FakeUI()).compare(FakeSession(), "VER", "HAM")

    assert result is not None
    assert result[2] == "VER"
    assert result[3] == timedelta(seconds=-2)
