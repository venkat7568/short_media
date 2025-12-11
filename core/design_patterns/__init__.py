"""
Design patterns package for Short Media Platform.
Contains base classes and implementations for:
- Strategy Pattern
- Factory Pattern
- Builder Pattern
- State Pattern
"""

from .strategy import IStrategy
from .factory import IFactory
from .builder import IBuilder
from .state import IState

__all__ = [
    'IStrategy',
    'IFactory',
    'IBuilder',
    'IState',
]
