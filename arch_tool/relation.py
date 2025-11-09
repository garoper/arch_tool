from typing import Any, Dict, Iterable, List, Optional


class Relation:
    """Class representing a relationship between two nodes."""

    def __init__(
        self,
        src: str,
        dst: str,
        type: str,
        description: Optional[str] = None,
        comment: Optional[str] = None,
        metadata: Optional[dict] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> None:
        """Initialize a Relation between two nodes.

        Args:
            src: Source node identifier
            dst: Target node identifier
            type: Type of relationship (e.g., "delivered by", "impacts", "depends on")
            description: Optional description of the relationship
            comment: Optional comment about the relationship
            metadata: Additional metadata dictionary
            tags: Optional tags for categorizing the relationship
        """
        self.__src: str = src
        self.__dst: str = dst
        self.__type: str = type
        self.description: Optional[str] = description
        self.comment: Optional[str] = comment
        self.__metadata: dict = {**metadata} if metadata is not None else {}
        self.__tags: List[str] = [tag for tag in tags] if tags is not None else []

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Iterable["Relation"]:
        """Create a Relation instance from a dictionary.

        Args:
            data: Dictionary containing relation properties

        Returns:
            Iterable[Relation] relations
        """

        sources = data["src"] if "src" in data else []
        if not sources:
            raise ValueError("Relation data must contain 'src' key.")

        destinations = data["dst"] if "dst" in data else []
        if not destinations:
            raise ValueError("Relation data must contain 'dst' key.")

        type = data["type"] if "type" in data else None
        if not type:
            raise ValueError("Relation data must contain 'type' key.")

        for src in sources if isinstance(sources, list) else [sources]:
            for dst in (
                destinations if isinstance(destinations, list) else [destinations]
            ):
                yield Relation(
                    src=src,
                    dst=dst,
                    type=type,
                    description=data.get("description", None),
                    comment=data.get("comment", None),
                    metadata=data.get("metadata", None),
                    tags=data.get("tags", None),
                )

    def set_tags(self, tags: Iterable[str]) -> None:
        """Set the tags for the relation."""
        self.__tags = [tag for tag in tags]

    @property
    def id(self) -> str:
        """Get a unique identifier for the relation."""
        return f"{self.__src}--[{self.__type}]-->{self.__dst}"
    
    @property
    def src(self) -> str:
        """Get the source node identifier."""
        return self.__src

    @property
    def dst(self) -> str:
        """Get the target node identifier."""
        return self.__dst

    @property
    def type(self) -> str:
        """Get the type of relationship."""
        return self.__type

    @property
    def metadata(self) -> dict:
        """Get the metadata dictionary."""
        return self.__metadata

    @property
    def tags(self) -> List[str]:
        """Get the list of tags."""
        return self.__tags

    def __repr__(self):
        return self.id