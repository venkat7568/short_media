"""
Builder Pattern implementation for Short Media Platform.

The Builder pattern separates the construction of a complex object from its
representation, allowing the same construction process to create different representations.

Used for:
- SearchQueryBuilder (constructs complex match search criteria incrementally)
"""

from abc import ABC, abstractmethod
from typing import Any


class IBuilder(ABC):
    """Base interface for all builder implementations."""

    @abstractmethod
    def reset(self) -> None:
        """Reset the builder to initial state."""
        pass

    @abstractmethod
    def build(self) -> Any:
        """
        Build and return the final product.

        Returns:
            Any: The constructed product
        """
        pass


class BaseBuilder(IBuilder):
    """
    Base builder implementation.
    Provides common builder functionality.
    """

    def __init__(self):
        """Initialize the builder."""
        self.reset()

    def reset(self) -> None:
        """Reset the builder to initial state."""
        self._product = {}

    def build(self) -> Any:
        """
        Build and return the final product.
        Override in subclasses for custom build logic.

        Returns:
            Any: The constructed product
        """
        product = self._product
        self.reset()
        return product


class FluentBuilder(BaseBuilder):
    """
    Fluent builder implementation that supports method chaining.
    Methods return self to enable fluent interface.

    Example:
        builder = FluentBuilder()
        result = builder.with_x(value).with_y(value).build()
    """

    def _add_property(self, key: str, value: Any) -> 'FluentBuilder':
        """
        Add a property to the product being built.

        Args:
            key: Property name
            value: Property value

        Returns:
            FluentBuilder: Self for method chaining
        """
        self._product[key] = value
        return self

    def __getattr__(self, name: str):
        """
        Handle dynamic with_* methods for fluent interface.

        Args:
            name: Method name (should start with 'with_')

        Returns:
            function: Method that adds property and returns self

        Example:
            builder.with_name('John').with_age(30).build()
        """
        if name.startswith('with_'):
            property_name = name[5:]  # Remove 'with_' prefix
            return lambda value: self._add_property(property_name, value)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
