from typing import Any, Dict, Iterable, Optional
from .node import Node
from .container import Container

class Component(Container):
    def __init__(
        self,
        id: str,
        title: str,
        description: str = "",
        type: str = "component",
        metadata: Optional[Dict[str, Any]] = None,
        children: Optional[Dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
        comment: Optional[str] = None
    ) -> None:
        """Initialize a Component with a unique identifier.

        Args:
            id: Unique identifier
            title: Short title or summary of the component
            description: Detailed description of the component
            type: Type of the component (component, system, or database)
            metadata: Additional metadata dictionary
            children: Child nodes dictionary
            tags: Optional iterable of tags associated with the component
        """

        self.__title = title
        self.__description = description

        super().__init__(id=id, type=type, metadata=metadata, children=children, tags=tags, comment=comment)

    def set_title(self, title: str) -> None:
        """Set the title of the Component."""
        self.__title = title

    def set_description(self, description: str) -> None:
        """Set the description of the Component."""
        self.__description = description

    @property
    def title(self) -> str:
        """Get the title of the Component."""
        return self.__title

    @property
    def description(self) -> str:
        """Get the description of the Component."""
        return self.__description


class System(Component):
    def __init__(
        self,
        id: str,
        title: str,
        description: str = "",
        type: str = "system",
        metadata: Optional[Dict[str, Any]] = None,
        children: Optional[Dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> None:
        """Initialize a System component.

        Args:
            id: Unique identifier
            title: Short title or summary of the system
            description: Detailed description of the system
            type: Type (should be "system")
            metadata: Additional metadata dictionary
            children: Child nodes dictionary
            tags: Optional iterable of tags associated with the system
        """
        super().__init__(
            id=id, title=title, description=description, type=type, metadata=metadata, children=children, tags=tags
        )


class Database(Component):
    def __init__(
        self,
        id: str,
        title: str,
        description: str = "",
        type: str = "database",
        metadata: Optional[Dict[str, Any]] = None,
        children: Optional[Dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> None:
        """Initialize a Database component.

        Args:
            id: Unique identifier
            title: Short title or summary of the database
            description: Detailed description of the database
            type: Type (should be "database")
            metadata: Additional metadata dictionary
            children: Child nodes dictionary
            tags: Optional iterable of tags associated with the database
        """
        super().__init__(
            id=id, title=title, description=description, type=type, metadata=metadata, children=children, tags=tags
        )


Node.register_type(Component, "component")
Node.register_type(System, "system")
Node.register_type(Database, "database")
