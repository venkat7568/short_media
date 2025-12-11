"""
Factory Pattern implementation for Short Media Platform.

The Factory pattern provides an interface for creating objects without specifying
their exact classes.

Used for:
- Post creation (TextPost, ImagePost, VideoPost based on content type)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Type


class IFactory(ABC):
    """Base interface for all factory implementations."""

    @abstractmethod
    def create(self, product_type: str, **kwargs) -> Any:
        """
        Create a product based on the product type.

        Args:
            product_type: Type of product to create
            **kwargs: Arguments needed to create the product

        Returns:
            Any: Created product instance

        Raises:
            ValueError: If product_type is not supported
        """
        pass


class BaseFactory(IFactory):
    """
    Base factory implementation with product registry.
    Subclasses can register product types and their classes.
    """

    def __init__(self):
        """Initialize the factory with an empty product registry."""
        self._products: Dict[str, Type] = {}

    def register_product(self, product_type: str, product_class: Type) -> None:
        """
        Register a product type with its corresponding class.

        Args:
            product_type: Identifier for the product type
            product_class: Class to instantiate for this product type
        """
        self._products[product_type] = product_class

    def unregister_product(self, product_type: str) -> None:
        """
        Unregister a product type.

        Args:
            product_type: Identifier for the product type to remove
        """
        if product_type in self._products:
            del self._products[product_type]

    def create(self, product_type: str, **kwargs) -> Any:
        """
        Create a product based on the product type.

        Args:
            product_type: Type of product to create
            **kwargs: Arguments passed to the product constructor

        Returns:
            Any: Created product instance

        Raises:
            ValueError: If product_type is not registered
        """
        product_class = self._products.get(product_type)
        if product_class is None:
            raise ValueError(
                f"Unknown product type: {product_type}. "
                f"Available types: {', '.join(self._products.keys())}"
            )
        return product_class(**kwargs)

    def get_registered_types(self) -> list:
        """
        Get list of all registered product types.

        Returns:
            list: List of product type identifiers
        """
        return list(self._products.keys())
