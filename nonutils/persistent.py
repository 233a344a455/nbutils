import json
from pathlib import Path
from typing import Dict, Any

from pydantic import BaseSettings

pref_dir: Path = Path("preferences")

def json_config_settings_source(pref: 'Preference') -> Dict[str, Any]:
    if pref._perf_path.exists():
        return json.loads(pref._perf_path.read_text(encoding='utf-8'))
    else:
        return {}

class Preference(BaseSettings):
    _initialized = False
    _perf_path: Path

    def __dump(self):
        self._perf_path.write_text(self.json(), encoding='utf-8')

    def __init__(self, pref_name: str, *args, **kwargs):
        self._perf_path = pref_dir / f"{pref_name}.json"
        pref_dir.mkdir(parents=True, exist_ok=True)

        super().__init__(*args, **kwargs)

        self._initialized = True

    def __setattr__(self, name, value):
        # Dump preference when a attr is changed
        super().__setattr__(name, value)
        if getattr(self, '_initialized', False):
            self.__dump()

    class Config:
        underscore_attrs_are_private = True

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                json_config_settings_source,
                env_settings,
                file_secret_settings,
            )

