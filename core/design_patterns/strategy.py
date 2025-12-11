"""
Strategy Pattern implementation for Short Media Platform.

The Strategy pattern enables selecting an algorithm at runtime.
Used for:
- Feed ranking algorithms (Recency, Engagement, Personalized)
- Post filters (Visibility, BlockedUsers, ContentModeration)
- Matching algorithms (Attribute, Behavioral, ML)
- Notification channels (Push, Email, SMS)
"""

from abc import ABC, abstractmethod
from typing import Any, List


class IStrategy(ABC):
    """Base interface for all strategy implementations."""

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the strategy algorithm.

        Args:
            *args: Positional arguments for the strategy
            **kwargs: Keyword arguments for the strategy

        Returns:
            Any: Result of the strategy execution
        """
        pass


class StrategyContext:
    """
    Context class that uses a Strategy.
    Allows swapping strategies at runtime.
    """

    def __init__(self, strategy: IStrategy = None):
        """
        Initialize the context with an optional strategy.

        Args:
            strategy: Initial strategy to use
        """
        self._strategy = strategy

    def set_strategy(self, strategy: IStrategy) -> None:
        """
        Set or change the strategy at runtime.

        Args:
            strategy: New strategy to use
        """
        self._strategy = strategy

    def execute_strategy(self, *args, **kwargs) -> Any:
        """
        Execute the current strategy.

        Args:
            *args: Positional arguments for the strategy
            **kwargs: Keyword arguments for the strategy

        Returns:
            Any: Result of the strategy execution

        Raises:
            ValueError: If no strategy is set
        """
        if self._strategy is None:
            raise ValueError("No strategy set")
        return self._strategy.execute(*args, **kwargs)
