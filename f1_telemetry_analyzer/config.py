from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    project_folder: Path = Path(__file__).resolve().parent.parent
    minimum_season: int = 2018

    @property
    def cache_folder(self) -> Path:
        return self.project_folder / "cache"

    @property
    def output_folder(self) -> Path:
        return self.project_folder / "grafikoni"
