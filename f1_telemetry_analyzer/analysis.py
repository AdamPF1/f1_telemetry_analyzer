from __future__ import annotations

from typing import Any, ClassVar

import fastf1
import pandas as pd

from .ui import UI


class Analyzer:
    SECTORS: ClassVar[dict[str, str]] = {
        "S1": "Sector1Time",
        "S2": "Sector2Time",
        "S3": "Sector3Time",
    }

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

    def lap_data(self, session: Any, driver: str) -> tuple[Any, Any] | None:
        lap = self.fastest_lap(session, driver)
        if lap is None:
            return None
        telemetry = self.telemetry(lap)
        if telemetry is None:
            return None
        return lap, telemetry

    @staticmethod
    def lap_time(time: Any) -> str:
        minutes, seconds = divmod(time.total_seconds(), 60)
        return f"{int(minutes)}:{seconds:06.3f}"

    def show_lap(self, lap: Any, driver: str) -> None:
        print(f"\n{self.ui.section('NAJBRŽI KRUG')}")
        print(f"Vozač       : {driver}")
        print(f"Broj kruga  : {int(lap['LapNumber'])}")
        print(f"Vreme       : {self.lap_time(lap['LapTime'])}")
        if pd.notna(lap["Compound"]):
            print(f"Gume        : {lap['Compound']}")
        if pd.notna(lap["Position"]):
            print(f"Pozicija    : {int(lap['Position'])}")

    def show_statistics(self, telemetry: Any, driver: str) -> None:
        print(f"\n{self.ui.section('STATISTIKA TELEMETRIJE')}")
        print(f"Vozač                 : {driver}")
        print(f"Maksimalna brzina     : {telemetry['Speed'].max():.2f} km/h")
        print(f"Prosečna brzina       : {telemetry['Speed'].mean():.2f} km/h")
        print(f"Maksimalni gas        : {telemetry['Throttle'].max():.2f}%")
        print(f"Prosečni gas          : {telemetry['Throttle'].mean():.2f}%")
        print(f"Tačke sa kočenjem     : {(telemetry['Brake'] > 0).sum()}")

    @staticmethod
    def faster_driver(
        first_lap: Any, second_lap: Any, first_driver: str, second_driver: str
    ) -> tuple[str, float]:
        difference = (first_lap["LapTime"] - second_lap["LapTime"]).total_seconds()
        faster = first_driver if difference <= 0 else second_driver
        return faster, abs(difference)

    @classmethod
    def sector_differences(cls, first_lap: Any, second_lap: Any) -> dict[str, float]:
        differences = {}
        for sector, column in cls.SECTORS.items():
            if pd.isna(first_lap[column]) or pd.isna(second_lap[column]):
                continue
            differences[sector] = (first_lap[column] - second_lap[column]).total_seconds()
        return differences

    def show_sector_differences(
        self, first_lap: Any, second_lap: Any, first_driver: str, second_driver: str
    ) -> None:
        print(f"\n{self.ui.section('RAZLIKE PO SEKTORIMA')}")
        differences = self.sector_differences(first_lap, second_lap)
        if not differences:
            self.ui.error("Vremena po sektorima nisu dostupna.")
            return
        for sector, difference in differences.items():
            faster = first_driver if difference <= 0 else second_driver
            print(f"{sector}  : {faster} brži za {abs(difference):.3f}s")
