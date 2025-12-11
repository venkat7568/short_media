"""
State Pattern implementation for Short Media Platform.

The State pattern allows an object to alter its behavior when its internal state changes.
The object will appear to change its class.

Used for:
- Video call states (RingingState → ActiveState → EndedState/MissedState)
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any


class IState(ABC):
    """Base interface for all state implementations."""

    @abstractmethod
    def handle(self, context: 'StateContext', *args, **kwargs) -> Any:
        """
        Handle an action in this state.

        Args:
            context: The context object (state machine)
            *args: Positional arguments for the action
            **kwargs: Keyword arguments for the action

        Returns:
            Any: Result of handling the action
        """
        pass

    def on_enter(self, context: 'StateContext') -> None:
        """
        Called when entering this state.

        Args:
            context: The context object (state machine)
        """
        pass

    def on_exit(self, context: 'StateContext') -> None:
        """
        Called when exiting this state.

        Args:
            context: The context object (state machine)
        """
        pass


class StateContext:
    """
    Context class for state machine.
    Maintains current state and delegates actions to it.
    """

    def __init__(self, initial_state: IState = None):
        """
        Initialize the state context.

        Args:
            initial_state: Initial state of the state machine
        """
        self._state = None
        if initial_state:
            self.transition_to(initial_state)

    @property
    def state(self) -> IState:
        """
        Get the current state.

        Returns:
            IState: Current state
        """
        return self._state

    def transition_to(self, state: IState) -> None:
        """
        Transition to a new state.

        Args:
            state: New state to transition to
        """
        if self._state:
            self._state.on_exit(self)

        self._state = state

        if self._state:
            self._state.on_enter(self)

    def handle(self, *args, **kwargs) -> Any:
        """
        Delegate handling to the current state.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Any: Result from state's handle method

        Raises:
            ValueError: If no state is set
        """
        if self._state is None:
            raise ValueError("No state set")
        return self._state.handle(self, *args, **kwargs)

    def get_state_name(self) -> str:
        """
        Get the name of the current state.

        Returns:
            str: Name of the current state class
        """
        if self._state is None:
            return "No State"
        return self._state.__class__.__name__
