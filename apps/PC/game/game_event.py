import dataclasses
from typing import Callable

@dataclasses.dataclass
class GameEvent:
    func: Callable
    time_run: float
    duration: float = None
    enable: bool = True
