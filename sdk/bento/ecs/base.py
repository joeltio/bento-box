#
# Bentobox
# SDK - ECS
# Base classes
#

from typing import FrozenSet, List, Any, Set, Union
from abc import ABC, abstractmethod, abstractproperty

from bento.spec.ecs import ComponentDef


class Component(ABC):
    """Component represents a ECS Component in the Engine. """

    @abstractproperty
    def component_name(self):
        """Get the name of the this Component"""
        pass

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

    def __str__(self):
        return f"{type(self).__name__}<{self._entity_id}, {self._name}>"


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

    @abstractproperty
    def id(self) -> int:
        """Get the id of this Entity"""
        return 0  # placeholder to statisfy type checking

    @abstractproperty
    def components(self) -> FrozenSet[Component]:
        """Get the components attached to this Entity"""
        return FrozenSet()  # placeholder to statisfy type checking

    def __getitem__(self, name: Union[str, ComponentDef]) -> Component:
        """Alias for get_component()"""
        return self.get_component(str(name))

    def __str__(self):
        return f"{type(self).__name__}<{self.id}>"
