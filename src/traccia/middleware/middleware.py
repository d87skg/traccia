from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple, Any, Dict

class Action(Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    WARN = "WARN"

class Middleware(ABC):
    @abstractmethod
    def process(self, event: Dict[str, Any]) -> Tuple[Dict[str, Any], Action]:
        '''Process an event. Return (modified_event, action).'''
        ...
