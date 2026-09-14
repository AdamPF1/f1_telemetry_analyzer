from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

import fastf1
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection


@dataclass(frozen=True)
class AppConfig:
    cache_folder: str = "cache"
    output_folder: str = "grafikoni"
    minimum_season: int = 2018


class F1DataService:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def enable_cache(self) -> None:
        os.makedirs(self.config.cache_folder, exist_ok=True)
        fastf1.Cache.enable_cache(self.config.cache_folder)

    def get_schedule(self, season: int) -> Any:
        return fastf1.get_event_schedule(season)

    def get_session(self, season: int, round_number: int, session_type: str) -> Any:
        session = fastf1.get_session(season, round_number, session_type)
        session.load()
        return session


class ChartRenderer:
    BACKGROUND = "#111827"
    GRID = "#374151"
    TEXT = "#F9FAFB"
    RED = "#EF4444"
    BLUE = "#38BDF8"
    GREEN = "#22C55E"
    ORANGE = "#F59E0B"

    def __init__(self, config: AppConfig, ui: "ConsoleUI") -> None:
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

    def _display(self, figure: Any, filename: str) -> None:
        figure.tight_layout()
        if self.ui.ask_yes_no("Sačuvati grafikon kao PNG?"):
            os.makedirs(self.config.output_folder, exist_ok=True)
            path = os.path.join(self.config.output_folder, filename)
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
        self._display(figure, f"brzina_{driver}.png")

    def throttle_and_brake(self, telemetry: Any, driver: str) -> None:
        figure, axes = plt.subplots(figsize=(12, 6))
        axes.plot(
            telemetry["Distance"], telemetry["Throttle"],
            label="Gas", color=self.GREEN, linewidth=2
        )
        axes.plot(
            telemetry["Distance"], telemetry["Brake"] * 100,
            label="Kočenje", color=self.RED, linewidth=2
        )
        axes.set_title(f"Gas i kočenje — {driver}", fontweight="bold")
        axes.set_xlabel("Distanca kroz krug (m)")
        axes.set_ylabel("Procenat")
        axes.legend(facecolor=self.BACKGROUND, labelcolor=self.TEXT)
        self._style(figure, axes)
        self._display(figure, f"gas_kocenje_{driver}.png")

    def speed_and_rpm(self, telemetry: Any, driver: str) -> None:
        figure, speed_axis = plt.subplots(figsize=(12, 6))
        rpm_axis = speed_axis.twinx()
        speed_axis.plot(
            telemetry["Distance"], telemetry["Speed"],
            color=self.RED, label="Brzina", linewidth=2
        )
        rpm_axis.plot(
            telemetry["Distance"], telemetry["RPM"],
            color=self.BLUE, label="Obrtaji", linewidth=2
        )
        speed_axis.set_title(f"Brzina i obrtaji — {driver}", fontweight="bold")
        speed_axis.set_xlabel("Distanca kroz krug (m)")
        speed_axis.set_ylabel("Brzina (km/h)", color=self.RED)
        rpm_axis.set_ylabel("RPM / obrtaji motora", color=self.BLUE)
        self._style(figure, speed_axis)
        rpm_axis.tick_params(axis="y", colors=self.BLUE)
        self._display(figure, f"brzina_obrtaji_{driver}.png")

    def track_map(self, telemetry: Any, driver: str) -> None:
        x = np.asarray(telemetry["X"].values)
        y = np.asarray(telemetry["Y"].values)
        speed = np.asarray(telemetry["Speed"].values)
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

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
        self._display(figure, f"mapa_staze_{driver}.png")

    def compare_speed(
        self,
        telemetry_one: Any,
        telemetry_two: Any,
        driver_one: str,
        driver_two: str,
        faster_driver: str,
    ) -> None:
        figure, axes = plt.subplots(figsize=(12, 6))
        axes.plot(
            telemetry_one["Distance"], telemetry_one["Speed"],
            color=self.RED, linewidth=2, label=driver_one
        )
        axes.plot(
            telemetry_two["Distance"], telemetry_two["Speed"],
            color=self.BLUE, linewidth=2, label=driver_two
        )
        axes.set_title(
            f"Poređenje brzine — brži vozač: {faster_driver}",
            fontweight="bold",
        )
        axes.set_xlabel("Distanca kroz krug (m)")
        axes.set_ylabel("Brzina (km/h)")
        axes.legend(facecolor=self.BACKGROUND, labelcolor=self.TEXT)
        self._style(figure, axes)
        self._display(figure, f"poredjenje_{driver_one}_{driver_two}.png")


class ConsoleUI:
    RED = "\033[91m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    def header(self) -> None:
        print(f"\n{self.CYAN}{'═' * 64}{self.RESET}")
        print(f"{self.CYAN}              F1 TELEMETRY ANALYZER{self.RESET}")
        print(f"{self.CYAN}{'═' * 64}{self.RESET}")
        print("Analiza najbržeg kruga na osnovu stvarnih Formula 1 podataka.\n")

    def success(self, message: str) -> None:
        print(f"{self.GREEN}✓ {message}{self.RESET}")

    def error(self, message: str) -> None:
        print(f"{self.RED}✗ {message}{self.RESET}")

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
                value = int(input(f"Sezona (preporučeno {minimum}+): "))
                if value < minimum:
                    print(f"{self.YELLOW}Napomena: starije sezone mogu imati manje podataka.{self.RESET}")
                return value
            except ValueError:
                self.error("Sezona mora biti ceo broj, na primer 2024.")

    def race(self, schedule: Any) -> int:
        print("\n" + self._section("KALENDAR SEZONE"))
        for _, event in schedule.iterrows():
            if event["RoundNumber"] != 0:
                print(f"{int(event['RoundNumber']):>2}. {event['EventName']} — {event['Location']}")
        valid_rounds = set(schedule["RoundNumber"].tolist())
        while True:
            try:
                value = int(input("\nBroj trke: "))
                if value in valid_rounds and value != 0:
                    return value
                self.error("Trka sa tim brojem ne postoji u kalendaru.")
            except ValueError:
                self.error("Broj trke mora biti ceo broj.")

    def session_type(self) -> str:
        sessions = {
            "R": "Trka", "Q": "Kvalifikacije", "FP1": "Prvi trening",
            "FP2": "Drugi trening", "FP3": "Treći trening",
            "S": "Sprint", "SQ": "Sprint kvalifikacije",
        }
        print("\n" + self._section("TIP SESIJE"))
        print("  ".join(f"{key}: {value}" for key, value in sessions.items()))
        while True:
            value = input("\nTip sesije: ").strip().upper()
            if value in sessions:
                return value
            self.error("Nepoznat tip sesije.")

    def drivers(self, session: Any) -> None:
        print("\n" + self._section("DOSTUPNI VOZAČI"))
        if session.results is not None and not session.results.empty:
            for _, driver in session.results.iterrows():
                print(f"{driver['Abbreviation']:<5} {driver['FullName']} — {driver['TeamName']}")
        else:
            print(", ".join(sorted(session.laps["Driver"].dropna().unique())))

    def driver(self, session: Any, prompt: str = "Vozač") -> str:
        available = set(session.laps["Driver"].dropna().unique())
        while True:
            value = input(f"\n{prompt} (npr. VER, HAM, LEC): ").strip().upper()
            if value in available:
                return value
            self.error("Vozač nije pronađen u izabranoj sesiji.")

    def loading_error(self, error: Exception) -> None:
        self.error("Podaci nisu mogli da se učitaju.")
        print("Proverite internet, sezonu i dostupnost izabrane sesije.")
        print(f"Detalji: {error}")

    @staticmethod
    def _section(title: str) -> str:
        return f"── {title} " + "─" * max(0, 54 - len(title))


class TelemetryAnalyzer:
    def __init__(self, ui: ConsoleUI) -> None:
        self.ui = ui

    def fastest_lap(self, session: Any, driver: str) -> Optional[Any]:
        laps = session.laps.pick_drivers(driver)
        if laps.empty:
            self.ui.error("Nema dostupnih krugova za ovog vozača.")
            return None
        lap = laps.pick_fastest()
        if lap is None:
            self.ui.error("Najbrži krug nije dostupan.")
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

    def show_lap_details(self, lap: Any, driver: str) -> None:
        print("\n" + self.ui._section("NAJBRŽI KRUG"))
        print(f"Vozač       : {driver}")
        print(f"Broj kruga  : {int(lap['LapNumber'])}")
        print(f"Vreme       : {lap['LapTime']}")
        print(f"Gume        : {lap['Compound']}")
        position = lap["Position"]
        if position is not None and not (isinstance(position, float) and np.isnan(position)):
            print(f"Pozicija    : {int(position)}")

    def show_statistics(self, telemetry: Any, driver: str) -> None:
        print("\n" + self.ui._section("STATISTIKA TELEMETRIJE"))
        print(f"Vozač                 : {driver}")
        print(f"Maksimalna brzina     : {telemetry['Speed'].max():.2f} km/h")
        print(f"Prosečna brzina       : {telemetry['Speed'].mean():.2f} km/h")
        print(f"Maksimalni gas        : {telemetry['Throttle'].max():.2f}%")
        print(f"Prosečni gas          : {telemetry['Throttle'].mean():.2f}%")
        print(f"Tačke sa kočenjem     : {int((telemetry['Brake'] > 0).sum())}")

    def compare(self, session: Any, first: str, second: str) -> Optional[tuple[Any, Any, Any, Any]]:
        first_lap = self.fastest_lap(session, first)
        second_lap = self.fastest_lap(session, second)
        if first_lap is None or second_lap is None:
            return None
        first_telemetry = self.telemetry(first_lap)
        second_telemetry = self.telemetry(second_lap)
        if first_telemetry is None or second_telemetry is None:
            return None
        first_time = first_lap["LapTime"].total_seconds()
        second_time = second_lap["LapTime"].total_seconds()
        faster = first if first_time <= second_time else second
        return first_telemetry, second_telemetry, faster, first_lap["LapTime"] - second_lap["LapTime"]


class F1TelemetryApplication:
    def __init__(self, config: Optional[AppConfig] = None) -> None:
        self.config = config or AppConfig()
        self.ui = ConsoleUI()
        self.data = F1DataService(self.config)
        self.analyzer = TelemetryAnalyzer(self.ui)
        self.charts = ChartRenderer(self.config, self.ui)

    def run(self) -> None:
        self.data.enable_cache()
        self.ui.header()
        season = self.ui.season(self.config.minimum_season)
        try:
            schedule = self.data.get_schedule(season)
            round_number = self.ui.race(schedule)
            session_type = self.ui.session_type()
            print("\nUčitavanje podataka... Prvi put može potrajati nekoliko minuta.")
            session = self.data.get_session(season, round_number, session_type)
        except Exception as error:
            self.ui.loading_error(error)
            return

        self.ui.success("Podaci su uspešno učitani.")
        self.ui.drivers(session)
        self._analyze_driver(session)

    def _analyze_driver(self, session: Any) -> None:
        while True:
            driver = self.ui.driver(session)
            lap = self.analyzer.fastest_lap(session, driver)
            if lap is None:
                if not self.ui.ask_yes_no("Pokušati sa drugim vozačem?"):
                    return
                continue
            telemetry = self.analyzer.telemetry(lap)
            if telemetry is None:
                if not self.ui.ask_yes_no("Pokušati sa drugim vozačem?"):
                    return
                continue

            self.analyzer.show_lap_details(lap, driver)
            self.analyzer.show_statistics(telemetry, driver)
            self.charts.speed(telemetry, driver)
            self.charts.throttle_and_brake(telemetry, driver)
            self.charts.speed_and_rpm(telemetry, driver)
            self.charts.track_map(telemetry, driver)

            if self.ui.ask_yes_no("Uporediti ovog vozača sa drugim?"):
                other = self.ui.driver(session, f"Drugi vozač za poređenje sa {driver}")
                comparison = self.analyzer.compare(session, driver, other)
                if comparison is not None:
                    first_telemetry, second_telemetry, faster, time_difference = comparison
                    self.ui.success(f"Brži vozač je {faster}. Razlika: {abs(time_difference.total_seconds()):.3f}s")
                    self.charts.compare_speed(
                        first_telemetry, second_telemetry, driver, other, faster
                    )
            return


if __name__ == "__main__":
    F1TelemetryApplication().run()
