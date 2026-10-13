from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    project_folder: Path = Path(__file__).resolve().parent.parent
    cache_folder: Path = project_folder / "cache"
    output_folder: Path = project_folder / "grafikoni"
    minimum_season: int = 2018
