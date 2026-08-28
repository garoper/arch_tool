from typing import Any, Dict, Iterable, Optional
from .node import Node
from .container import Container


class Grouping(Container):
    def __init__(
        self,
        id: str,
        title: str,
        type: str = "grouping",
        metadata: Optional[Dict[str, Any]] = None,
        children: Optional[Dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
        comment: Optional[str] = None,
    ) -> None:
        """Initialize a Grouping (group of related requirements, features, or issues).

        Args:
            id: Unique identifier
            title: Short title or title of the grouping
            type: Type of the grouping (default: "grouping")
            metadata: Additional metadata dictionary
            children: Child nodes dictionary
            tags: Optional iterable of tags associated with the grouping
        """

        self.__title = title

        super().__init__(
            id=id,
            type=type,
            metadata=metadata,
            children=children,
            tags=tags,
            comment=comment,
        )

    @property
    def title(self) -> str:
        """Get the title of the Grouping."""
        return self.__title

    @title.setter
    def title(self, title: str) -> None:
        """Set the title of the Grouping."""
        self.__title = title


Node.register_type(Grouping, "grouping")
