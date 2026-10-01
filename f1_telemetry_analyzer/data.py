from typing import Any

import fastf1

from .config import Config


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
