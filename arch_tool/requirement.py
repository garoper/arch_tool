from typing import Any, Dict, Optional, Literal, Iterable
from .node import Node
from .container import Container


class Requirement(Container):
    def __init__(
        self,
        id: str,
        title: str,
        description: str = "",
        priority: Literal[
            "MUST", "SHOULD", "COULD", "WONT", "UNSPECIFIED"
        ] = "UNSPECIFIED",
        type: str = "requirement",
        metadata: Optional[Dict[str, Any]] = None,
        children: Optional[Dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
        comment: Optional[str] = None,
    ) -> None:
        """Initialize a Requirement with a unique identifier.

        Args:
            id: Unique identifier
            title: Short summary/title of the requirement
            description: Detailed description of the requirement
            type: Type of the requirement (default: "requirement")
            metadata: Additional metadata dictionary
            children: Child nodes dictionary
        """

        self.__title = title
        self.__description = description
        self.__priority = priority

        super().__init__(
            id=id,
            type=type,
            metadata=metadata,
            children=children,
            tags=tags,
            comment=comment,
        )

    @property
    def priority(self) -> Literal["MUST", "SHOULD", "COULD", "WONT", "UNSPECIFIED"]:
        """Get the priority of the Requirement."""
        return self.__priority

    @property
    def title(self) -> str:
        """Get the title of the Requirement."""
        return self.__title

    @property
    def description(self) -> str:
        """Get the description of the Requirement."""
        return self.__description

    @property
    def tags(self) -> Iterable[str]:
        """Get immutable list of tags associated with the Requirement."""
        yield from super().tags
        if self.__priority != "UNSPECIFIED":
            priority_tag = self.__priority.lower()
            if not self.has_tag(priority_tag):
                yield priority_tag

    @title.setter
    def title(self, title: str) -> None:
        """Set the title of the Requirement."""
        self.__title = title

    @description.setter
    def description(self, description: str) -> None:
        """Set the description of the Requirement."""
        self.__description = description

    @priority.setter
    def priority(
        self, priority: Literal["MUST", "SHOULD", "COULD", "WONT", "UNSPECIFIED"]
    ) -> None:
        """Set the priority of the Requirement."""
        self.__priority = priority


Node.register_type(Requirement, "requirement")
