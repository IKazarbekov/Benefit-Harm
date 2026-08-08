from dataclasses import dataclass, field
from datetime import datetime

from py_model.mood import Mood

@dataclass
class GameSnapshotV1:
    emotion: Mood
    frequency_key_down: int
    game_different: int
    health: int
    time: datetime = field(default_factory=datetime.now)
