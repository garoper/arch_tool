from typing import Any, Dict, Iterable, Optional, List, Tuple

from .relation import Relation
from .node import Node
from .container import Container


class Graph(Container):
    def __init__(
        self,
        id: str = "root",
        type: str = "root",
        metadata: Optional[Dict[str, Any]] = None,
        children: Optional[Iterable[Node]] = None,
        relations: Optional[Iterable[Dict[str, Any] | Relation]] = None,
        tags: Optional[Iterable[str]] = None,
        comment: Optional[str] = None,
    ) -> None:
        """Initialize a Graph containing all requirements, features, issues, and their relationships.

        Args:
            id: Unique identifier (default: "root")
            type: Type of the root (default: "root")
            metadata: Additional metadata dictionary
            children: Child nodes list
            relations: List of relationships between requirements and features/issues
            tags: Optional iterable of tags associated with the graph
        """
        self.__relations: List[Relation] = []
        if relations is not None:
            for rel in relations:
                if isinstance(rel, Relation):
                    self.__relations.append(rel)
                else:
                    # Relation.from_dict may return an iterable of Relation objects
                    self.__relations.extend(Relation.from_dict(rel))

        super().__init__(
            id=id,
            type=type,
            metadata=metadata,
            children=children,
            tags=tags,
            comment=comment,
        )

    @property
    def relations(self) -> Iterable[Relation]:
        """Get the list of relations."""
        yield from self.__relations

    def remove_relation(self, relation: Relation | Dict[str, Any]) -> None:
        """Remove a relationship between entities.

        Args:
            relation: Relation object to remove
        """
        if isinstance(relation, dict):
            self.__relations = [
                rel
                for rel in self.__relations
                if rel.type != relation.get("type")
                or rel.src != relation.get("src")
                or rel.dst != relation.get("dst")
            ]
        else:
            self.__relations.remove(relation)

    def add_relation(self, relation: Relation | Dict[str, Any]) -> None:
        """Add a relationship between entities.

        Args:
            relation: Relation object or dictionary representing the relation
        """
        if isinstance(relation, dict):
            self.__relations.extend(Relation.from_dict(relation))
        else:
            self.__relations.append(relation)

    def create_relation(
        self,
        from_id: str | Iterable[str],
        to_id: str | Iterable[str],
        type: str,
        comment: Optional[str] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> Relation:
        """Add a relationship between entities.

        Args:
            from_id: Source identifier (requirement ID or entity ID) or list of IDs
            to_id: Target identifier (requirement ID or entity ID) or list of IDs
            type: Type of relationship (e.g., "delivered by", "impacts", "depends on")
            comment: Optional comment about the relationship
            tags: Optional tags for categorizing the relationship
        """

        if isinstance(from_id, str):
            from_id = [from_id]
        if isinstance(to_id, str):
            to_id = [to_id]

        for src in from_id:
            for dst in to_id:
                relation = Relation(src=src, dst=dst, type=type)

                if comment:
                    relation.comment = comment

                if tags:
                    relation.tags = tags

                self.__relations.append(relation)

        return relation

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the Root node to a dictionary including relations."""
        result = super().to_dict()
        result["relations"] = self.__relations
        return result

    def append(
        self, data: Node | Dict[str, Any] | Iterable[Node | Dict[str, Any]]
    ) -> None:
        """Extend the graph with additional nodes and/or relations.

        This method can accept:
        - A single Node object
        - A list of Node objects
        - A dictionary with 'children' and/or 'relations' keys
        - A list of dictionaries with 'children' and/or 'relations' keys

        Args:
            data: Node(s), dict(s), or list containing nodes and/or relations to add
                 If dict contains 'children' key, those nodes are added as children
                 If dict contains 'relations' key, those relations are added
        """
        if isinstance(data, dict):
            data = Node.from_dict(data)
            self.append(data)
        elif isinstance(data, Graph):
            for child in data.children:
                self.add_child(child)
            for relation in data.relations:
                self.add_relation(relation)
        elif isinstance(data, Node):
            self.add_child(data)
        elif isinstance(data, Iterable):
            for item in data:
                # Recursively extend with each item
                self.append(item)
        else:
            raise TypeError(
                "Data must be a Node, Graph, dict, or iterable of these types."
            )


Node.register_type(Graph, "root")
