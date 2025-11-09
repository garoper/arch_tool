from typing import Any, Dict, Iterable, Optional
from .node import Node
from .container import Container


class Feature(Container):
    def __init__(
        self,
        id: str,
        title: str,
        description: str = "",
        type: str = "feature",
        metadata: Optional[Dict[str, Any]] = None,
        children: Optional[Dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
        comment: Optional[str] = None
    ) -> None:
        """Initialize a Feature with a unique identifier.

        Args:
            id: Unique identifier
            title: Short title or summary of the feature
            description: Detailed description of the feature
            type: Type of the feature (default: "feature")
            metadata: Additional metadata dictionary
            children: Child nodes dictionary
            tags: Optional iterable of tags associated with the feature
        """

        self.__title = title
        self.__description = description

        super().__init__(id=id, type=type, metadata=metadata, children=children, tags=tags, comment=comment)

    def set_title(self, title: str) -> None:
        """Set the title of the Feature."""
        self.__title = title
        
    def set_description(self, description: str) -> None:
        """Set the description of the Feature."""
        self.__description = description

    @property
    def title(self) -> str:
        """Get the title of the Feature."""
        return self.__title

    @property
    def description(self) -> str:
        """Get the description of the Feature."""
        return self.__description


Node.register_type(Feature, "feature")
