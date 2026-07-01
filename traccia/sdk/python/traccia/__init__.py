from .session import TracciaSession

__version__ = '0.1.0'

def start(objective: str):
    return TracciaSession(objective=objective)
