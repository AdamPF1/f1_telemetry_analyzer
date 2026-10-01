from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

from .ui import UI


class Charts:
    BACKGROUND = "#111827"
    GRID = "#374151"
    TEXT = "#F9FAFB"
    RED = "#EF4444"
    BLUE = "#38BDF8"
    GREEN = "#22C55E"

    def __init__(self, output_folder: Path, ui: UI) -> None:
        self.output_folder = output_folder
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
            self.output_folder.mkdir(parents=True, exist_ok=True)
            path = self.output_folder / filename
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
        speed_axis.plot(distance, telemetry["Speed"], color=self.RED, linewidth=2)
        rpm_axis.plot(distance, telemetry["RPM"], color=self.BLUE, linewidth=2)
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
            segments, cmap="plasma", norm=plt.Normalize(speed.min(), speed.max()), linewidth=5
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
