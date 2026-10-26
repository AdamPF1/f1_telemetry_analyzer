from __future__ import annotations

from typing import Any

import fastf1

from .analysis import Analyzer
from .charts import Charts
from .config import Config
from .data import F1Data
from .ui import UI


def choose_driver(session: Any, ui: UI, analyzer: Analyzer) -> tuple[str, Any, Any] | None:
    while True:
        driver = ui.driver(session)
        lap_data = analyzer.lap_data(session, driver)
        if lap_data is not None:
            return driver, *lap_data
        if not ui.ask_yes_no("Pokušati sa drugim vozačem?"):
            return None


def analyze_driver(session: Any, ui: UI, analyzer: Analyzer, charts: Charts) -> None:
    choice = choose_driver(session, ui, analyzer)
    if choice is None:
        return
    driver, lap, telemetry = choice
    analyzer.show_lap(lap, driver)
    analyzer.show_statistics(telemetry, driver)
    while True:
        getattr(charts, ui.chart())(telemetry, driver)
        if not ui.ask_yes_no("Prikazati još jedan grafikon?"):
            break

    if not ui.ask_yes_no("Uporediti ovog vozača sa drugim?"):
        return
    other_driver = ui.driver(session, f"Drugi vozač za poređenje sa {driver}", exclude=driver)
    other_data = analyzer.lap_data(session, other_driver)
    if other_data is None:
        return
    other_lap, other_telemetry = other_data
    faster, difference = analyzer.faster_driver(lap, other_lap, driver, other_driver)
    ui.success(f"Brži vozač je {faster}. Razlika: {difference:.3f}s")
    analyzer.show_sector_differences(lap, other_lap, driver, other_driver)
    charts.compare_speed(telemetry, other_telemetry, driver, other_driver, faster)


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
