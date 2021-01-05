#
# Bentobox
# SDK - ECS
# Base classes
#

from typing import List, Any
from abc import ABC, abstractmethod


class Component(ABC):
    """Component represents a ECS Component in the Engine. """

    @abstractmethod
    def get_attr(self, name: str) -> Any:
        """Retrieve the attribute value with the given name from this ECS component

        Args:
            name: Name of the attribute to retrieve.
        Raises:
            ValueError: If the component has no such attribute.
        Returns:
            The value of the attribute.
        """
        pass

    def __getattr__(self, name: str) -> Any:
        """ Alias for get_attr() """
        return self.get_attr(name)

    @abstractmethod
    def set_attr(self, name: str, value: Any):
        """Sets the attribute with the given name with the given value.

        Args:
            name: Name of the attribute to set.
            value: Value to set the attribute to.
        Raises:
            ValueError: If the component has no such attribute.
        """
        pass

    def __setattr__(self, name: str, value: Any) -> Any:
        """ Alias for set_attr() """
        return self.set_attr(name, value)


class Entity(ABC):
    """Entity represents a ECS entity in the Engine. """

    @abstractmethod
    def get_component(self, name: str) -> Component:
        """Retrieve the ECS component with the given name that is attached to this entity.

        Args:
            name:
                The name of the ECS component to retrieve.
        Returns:
            Component that represents the ECS component.
        """
        pass

    def __getitem__(self, name: str) -> Component:
        """Alias for get_component()"""
        return self.get_component(name)
