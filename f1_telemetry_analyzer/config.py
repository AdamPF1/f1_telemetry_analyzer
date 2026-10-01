from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    cache_folder: Path = Path("cache")
    output_folder: Path = Path("grafikoni")
    minimum_season: int = 2018
