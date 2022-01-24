import multiprocessing
from typing import Any, Dict, Optional

from gunicorn.app.base import Application


def number_of_workers() -> int:
    return (multiprocessing.cpu_count() * 2) + 1


class StandaloneApplication(Application):
    def __init__(self, app: Any, options: Optional[Dict[Any, Any]] = None):
        self._options = options
        self._application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self) -> None:
        config = {}
        if self._options:
            config = {
                key: value
                for key, value in self._options.items()
                if key in self.cfg.settings and value is not None
            }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self) -> Any:
        return self._application
