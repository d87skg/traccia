from .session import TracciaSession

__version__ = '0.3.0'

def start(objective: str):
    return TracciaSession(objective=objective)
