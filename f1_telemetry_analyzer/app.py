from __future__ import annotations

from typing import Any

import fastf1

from .analysis import Analyzer
from .charts import Charts
from .config import Config
from .data import F1Data
from .ui import UI


def analyze_driver(session: Any, ui: UI, analyzer: Analyzer, charts: Charts) -> None:
    while True:
        driver = ui.driver(session)
        lap = analyzer.fastest_lap(session, driver)
        telemetry = analyzer.telemetry(lap) if lap is not None else None
        if lap is None or telemetry is None:
            if ui.ask_yes_no("Pokušati sa drugim vozačem?"):
                continue
            return

        analyzer.show_lap(lap, driver)
        analyzer.show_statistics(telemetry, driver)
        charts.speed(telemetry, driver)
        charts.throttle_and_brake(telemetry, driver)
        charts.speed_and_rpm(telemetry, driver)
        charts.track_map(telemetry, driver)
        if not ui.ask_yes_no("Uporediti ovog vozača sa drugim?"):
            return

        other_driver = ui.driver(session, f"Drugi vozač za poređenje sa {driver}")
        comparison = analyzer.compare(session, driver, other_driver)
        if comparison is None:
            return
        first_telemetry, second_telemetry, faster, difference = comparison
        ui.success(f"Brži vozač je {faster}. Razlika: {abs(difference.total_seconds()):.3f}s")
        charts.compare_speed(first_telemetry, second_telemetry, driver, other_driver, faster)
        return


def main(config: Config | None = None) -> None:
    config = config or Config()
    ui = UI()
    data = F1Data(config)
    data.enable_cache()
    ui.header()
    season = ui.season(config.minimum_season)
    try:
        schedule = data.schedule(season)
        race = ui.race(schedule)
        session_type = ui.session_type()
        print("\nUčitavanje podataka... Prvi put može potrajati nekoliko minuta.")
        session = data.session(season, race, session_type)
    except (
        OSError,
        ValueError,
        fastf1.exceptions.DataNotLoadedError,
        fastf1.exceptions.FastF1CriticalError,
        fastf1.exceptions.InvalidSessionError,
    ) as error:
        ui.loading_error(error)
        return
    ui.success("Podaci su uspešno učitani.")
    ui.show_drivers(session)
    analyze_driver(session, ui, Analyzer(ui), Charts(config.output_folder, ui))
