from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import fastf1
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection


@dataclass(frozen=True)
class Config:
    cache_folder: Path = Path("cache")
    output_folder: Path = Path("grafikoni")
    minimum_season: int = 2018


class UI:
    COLORS = {
        "red": "\033[91m",
        "green": "\033[92m",
        "cyan": "\033[96m",
        "yellow": "\033[93m",
        "reset": "\033[0m",
    }

    SESSION_NAMES = {
        "R": "Trka",
        "Q": "Kvalifikacije",
        "FP1": "Prvi trening",
        "FP2": "Drugi trening",
        "FP3": "Treći trening",
        "S": "Sprint",
        "SQ": "Sprint kvalifikacije",
    }

    def header(self) -> None:
        cyan = self.COLORS["cyan"]
        reset = self.COLORS["reset"]
        print(f"\n{cyan}{'═' * 64}{reset}")
        print(f"{cyan}              F1 TELEMETRY ANALYZER{reset}")
        print(f"{cyan}{'═' * 64}{reset}")
        print("Analiza najbržeg kruga na osnovu stvarnih Formula 1 podataka.\n")

    def success(self, message: str) -> None:
        print(f"{self.COLORS['green']}✓ {message}{self.COLORS['reset']}")

    def error(self, message: str) -> None:
        print(f"{self.COLORS['red']}✗ {message}{self.COLORS['reset']}")

    def section(self, title: str) -> str:
        return f"── {title} " + "─" * max(0, 54 - len(title))

    def ask_yes_no(self, message: str) -> bool:
        while True:
            answer = input(f"{message} [da/ne]: ").strip().lower()
            if answer in {"da", "d"}:
                return True
            if answer in {"ne", "n"}:
                return False
            self.error("Unesite 'da' ili 'ne'.")

    def season(self, minimum: int) -> int:
        while True:
            try:
                season = int(input(f"Sezona (preporučeno {minimum}+): "))
            except ValueError:
                self.error("Sezona mora biti ceo broj, na primer 2024.")
                continue

            if season < minimum:
                print(
                    f"{self.COLORS['yellow']}Napomena: starije sezone "
                    f"mogu imati manje podataka.{self.COLORS['reset']}"
                )
            return season

    def race(self, schedule: Any) -> int:
        print(f"\n{self.section('KALENDAR SEZONE')}")
        valid_rounds = set()

        for _, event in schedule.iterrows():
            round_number = int(event["RoundNumber"])
            if round_number == 0:
                continue
            valid_rounds.add(round_number)
            print(f"{round_number:>2}. {event['EventName']} — {event['Location']}")

        while True:
            try:
                race_number = int(input("\nBroj trke: "))
            except ValueError:
                self.error("Broj trke mora biti ceo broj.")
                continue

            if race_number in valid_rounds:
                return race_number
            self.error("Trka sa tim brojem ne postoji u kalendaru.")

    def session_type(self) -> str:
        print(f"\n{self.section('TIP SESIJE')}")
        print("  ".join(f"{key}: {name}" for key, name in self.SESSION_NAMES.items()))

        while True:
            session_type = input("\nTip sesije: ").strip().upper()
            if session_type in self.SESSION_NAMES:
                return session_type
            self.error("Nepoznat tip sesije.")

    def show_drivers(self, session: Any) -> None:
        print(f"\n{self.section('DOSTUPNI VOZAČI')}")
        results = session.results

        if results is not None and not results.empty:
            for _, driver in results.iterrows():
                print(
                    f"{driver['Abbreviation']:<5} "
                    f"{driver['FullName']} — {driver['TeamName']}"
                )
            return

        drivers = sorted(session.laps["Driver"].dropna().unique())
        print(", ".join(drivers))

    def driver(self, session: Any, prompt: str = "Vozač") -> str:
        available = set(session.laps["Driver"].dropna().unique())

        while True:
            driver = input(f"\n{prompt} (npr. VER, HAM, LEC): ").strip().upper()
            if driver in available:
                return driver
            self.error("Vozač nije pronađen u izabranoj sesiji.")

    def loading_error(self, error: Exception) -> None:
        self.error("Podaci nisu mogli da se učitaju.")
        print("Proverite internet, sezonu i dostupnost izabrane sesije.")
        print(f"Detalji: {error}")


class F1Data:
    def __init__(self, config: Config) -> None:
        self.config = config

    def enable_cache(self) -> None:
        self.config.cache_folder.mkdir(parents=True, exist_ok=True)
        fastf1.Cache.enable_cache(str(self.config.cache_folder))

    def schedule(self, season: int) -> Any:
        return fastf1.get_event_schedule(season)

    def session(self, season: int, race: int, session_type: str) -> Any:
        session = fastf1.get_session(season, race, session_type)
        session.load()
        return session


class Analyzer:
    def __init__(self, ui: UI) -> None:
        self.ui = ui

    def fastest_lap(self, session: Any, driver: str) -> Optional[Any]:
        laps = session.laps.pick_drivers(driver)
        if laps.empty:
            self.ui.error("Nema dostupnih krugova za ovog vozača.")
            return None

        lap = laps.pick_fastest()
        if lap is None or lap.empty:
            self.ui.error("Najbrži krug nije dostupan.")
            return None
        return lap

    def telemetry(self, lap: Any) -> Optional[Any]:
        try:
            telemetry = lap.get_telemetry()
        except Exception as error:
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
    ) -> Optional[tuple[Any, Any, str, Any]]:
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


class Charts:
    BACKGROUND = "#111827"
    GRID = "#374151"
    TEXT = "#F9FAFB"
    RED = "#EF4444"
    BLUE = "#38BDF8"
    GREEN = "#22C55E"

    def __init__(self, config: Config, ui: UI) -> None:
        self.config = config
        self.ui = ui

    def _style(self, figure: Any, axes: Any) -> None:
        figure.patch.set_facecolor(self.BACKGROUND)
        axes.set_facecolor(self.BACKGROUND)
        axes.tick_params(colors=self.TEXT)
        axes.xaxis.label.set_color(self.TEXT)
        axes.yaxis.label.set_color(self.TEXT)
        axes.title.set_color(self.TEXT)

        for spine in axes.spines.values():
            spine.set_color(self.GRID)
        axes.grid(True, color=self.GRID, alpha=0.6)

    def _finish(self, figure: Any, filename: str) -> None:
        figure.tight_layout()
        if self.ui.ask_yes_no("Sačuvati grafikon kao PNG?"):
            self.config.output_folder.mkdir(parents=True, exist_ok=True)
            path = self.config.output_folder / filename
            figure.savefig(path, dpi=150, bbox_inches="tight", facecolor=figure.get_facecolor())
            self.ui.success(f"Grafikon je sačuvan: {path}")
        plt.show()
        plt.close(figure)

    def speed(self, telemetry: Any, driver: str) -> None:
        figure, axes = plt.subplots(figsize=(12, 6))
        axes.plot(telemetry["Distance"], telemetry["Speed"], color=self.RED, linewidth=2)
        axes.set_title(f"Brzina kroz najbrži krug — {driver}", fontweight="bold")
        axes.set_xlabel("Distanca kroz krug (m)")
        axes.set_ylabel("Brzina (km/h)")
        self._style(figure, axes)
        self._finish(figure, f"brzina_{driver}.png")

    def throttle_and_brake(self, telemetry: Any, driver: str) -> None:
        figure, axes = plt.subplots(figsize=(12, 6))
        distance = telemetry["Distance"]
        axes.plot(distance, telemetry["Throttle"], label="Gas", color=self.GREEN, linewidth=2)
        axes.plot(distance, telemetry["Brake"] * 100, label="Kočenje", color=self.RED, linewidth=2)
        axes.set_title(f"Gas i kočenje — {driver}", fontweight="bold")
        axes.set_xlabel("Distanca kroz krug (m)")
        axes.set_ylabel("Procenat")
        axes.legend(facecolor=self.BACKGROUND, labelcolor=self.TEXT)
        self._style(figure, axes)
        self._finish(figure, f"gas_kocenje_{driver}.png")

    def speed_and_rpm(self, telemetry: Any, driver: str) -> None:
        figure, speed_axis = plt.subplots(figsize=(12, 6))
        rpm_axis = speed_axis.twinx()
        distance = telemetry["Distance"]

        speed_axis.plot(distance, telemetry["Speed"], color=self.RED, label="Brzina", linewidth=2)
        rpm_axis.plot(distance, telemetry["RPM"], color=self.BLUE, label="Obrtaji", linewidth=2)
        speed_axis.set_title(f"Brzina i obrtaji — {driver}", fontweight="bold")
        speed_axis.set_xlabel("Distanca kroz krug (m)")
        speed_axis.set_ylabel("Brzina (km/h)", color=self.RED)
        rpm_axis.set_ylabel("RPM / obrtaji motora", color=self.BLUE)
        self._style(figure, speed_axis)
        rpm_axis.tick_params(axis="y", colors=self.BLUE)
        self._finish(figure, f"brzina_obrtaji_{driver}.png")

    def track_map(self, telemetry: Any, driver: str) -> None:
        x = np.asarray(telemetry["X"])
        y = np.asarray(telemetry["Y"])
        speed = np.asarray(telemetry["Speed"])
        points = np.column_stack((x, y)).reshape(-1, 1, 2)
        segments = np.concatenate((points[:-1], points[1:]), axis=1)

        figure, axes = plt.subplots(figsize=(10, 8))
        lines = LineCollection(
            segments,
            cmap="plasma",
            norm=plt.Normalize(speed.min(), speed.max()),
            linewidth=5,
        )
        lines.set_array(speed)
        axes.add_collection(lines)
        axes.set_xlim(x.min() - 500, x.max() + 500)
        axes.set_ylim(y.min() - 500, y.max() + 500)
        axes.set_title(f"Mapa staze po brzini — {driver}", fontweight="bold")
        axes.axis("off")
        self._style(figure, axes)

        colorbar = figure.colorbar(lines, ax=axes)
        colorbar.set_label("Brzina (km/h)", color=self.TEXT)
        colorbar.ax.tick_params(colors=self.TEXT)
        self._finish(figure, f"mapa_staze_{driver}.png")

    def compare_speed(
        self,
        first_telemetry: Any,
        second_telemetry: Any,
        first_driver: str,
        second_driver: str,
        faster_driver: str,
    ) -> None:
        figure, axes = plt.subplots(figsize=(12, 6))
        axes.plot(
            first_telemetry["Distance"],
            first_telemetry["Speed"],
            color=self.RED,
            linewidth=2,
            label=first_driver,
        )
        axes.plot(
            second_telemetry["Distance"],
            second_telemetry["Speed"],
            color=self.BLUE,
            linewidth=2,
            label=second_driver,
        )
        axes.set_title(f"Poređenje brzine — brži vozač: {faster_driver}", fontweight="bold")
        axes.set_xlabel("Distanca kroz krug (m)")
        axes.set_ylabel("Brzina (km/h)")
        axes.legend(facecolor=self.BACKGROUND, labelcolor=self.TEXT)
        self._style(figure, axes)
        self._finish(figure, f"poredjenje_{first_driver}_{second_driver}.png")


def analyze_driver(
    session: Any,
    ui: UI,
    analyzer: Analyzer,
    charts: Charts,
) -> None:
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
        charts.compare_speed(
            first_telemetry,
            second_telemetry,
            driver,
            other_driver,
            faster,
        )
        return


def main(config: Optional[Config] = None) -> None:
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
    except Exception as error:
        ui.loading_error(error)
        return

    ui.success("Podaci su uspešno učitani.")
    ui.show_drivers(session)
    analyze_driver(session, ui, Analyzer(ui), Charts(config, ui))


if __name__ == "__main__":
    main()
