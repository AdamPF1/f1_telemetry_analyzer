from __future__ import annotations

from typing import Any

import fastf1
import numpy as np

from .ui import UI


class Analyzer:
    def __init__(self, ui: UI) -> None:
        self.ui = ui

    def fastest_lap(self, session: Any, driver: str) -> Any | None:
        laps = session.laps.pick_drivers(driver)
        if laps.empty:
            self.ui.error("Nema dostupnih krugova za ovog vozača.")
            return None
        lap = laps.pick_fastest()
        if lap is None or lap.empty:
            self.ui.error("Najbrži krug nije dostupan.")
            return None
        return lap

    def telemetry(self, lap: Any) -> Any | None:
        try:
            telemetry = lap.get_telemetry()
        except (
            OSError,
            ValueError,
            fastf1.exceptions.DataNotLoadedError,
            fastf1.exceptions.NoLapDataError,
        ) as error:
            self.ui.loading_error(error)
            return None
        if telemetry.empty:
            self.ui.error("Telemetrija nije dostupna za ovaj krug.")
            return None
        return telemetry

    def show_lap(self, lap: Any, driver: str) -> None:
        print(f"\n{self.ui.section('NAJBRŽI KRUG')}")
        print(f"Vozač       : {driver}")
        print(f"Broj kruga  : {int(lap['LapNumber'])}")
        print(f"Vreme       : {lap['LapTime']}")
        print(f"Gume        : {lap['Compound']}")
        position = lap["Position"]
        if position is not None and not (isinstance(position, float) and np.isnan(position)):
            print(f"Pozicija    : {int(position)}")

    def show_statistics(self, telemetry: Any, driver: str) -> None:
        print(f"\n{self.ui.section('STATISTIKA TELEMETRIJE')}")
        print(f"Vozač                 : {driver}")
        print(f"Maksimalna brzina     : {telemetry['Speed'].max():.2f} km/h")
        print(f"Prosečna brzina       : {telemetry['Speed'].mean():.2f} km/h")
        print(f"Maksimalni gas        : {telemetry['Throttle'].max():.2f}%")
        print(f"Prosečni gas          : {telemetry['Throttle'].mean():.2f}%")
        print(f"Tačke sa kočenjem     : {(telemetry['Brake'] > 0).sum()}")

    def compare(
        self, session: Any, first_driver: str, second_driver: str
    ) -> tuple[Any, Any, str, Any] | None:
        first_lap = self.fastest_lap(session, first_driver)
        second_lap = self.fastest_lap(session, second_driver)
        if first_lap is None or second_lap is None:
            return None
        first_telemetry = self.telemetry(first_lap)
        second_telemetry = self.telemetry(second_lap)
        if first_telemetry is None or second_telemetry is None:
            return None
        first_time = first_lap["LapTime"].total_seconds()
        second_time = second_lap["LapTime"].total_seconds()
        faster = first_driver if first_time <= second_time else second_driver
        difference = first_lap["LapTime"] - second_lap["LapTime"]
        return first_telemetry, second_telemetry, faster, difference
