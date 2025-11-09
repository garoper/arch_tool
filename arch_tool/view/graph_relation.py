from arch_tool import Relation
from typing import Iterable, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .graph_node import GraphNode


class GraphRelation:
    """
    A GraphRelation represents a relationship between two GraphNodes within a graph structure.
    """

    def __init__(self, relation: Relation, src: "GraphNode", dst: "GraphNode"):
        """Initialize a GraphRelation with a Relation and its associated GraphNodes.

        Args:
            relation: The Relation instance this GraphRelation represents
            src: The source GraphNode of the relation
            dst: The target GraphNode of the relation
        """
        self.__relation: Relation = relation
        self.__src: "GraphNode" = src
        self.__dst: "GraphNode" = dst

    @property
    def relation(self) -> Relation:
        """Get the underlying Relation of this GraphRelation."""
        return self.__relation

    @property
    def src(self) -> str:
        """Get the source GraphNode of this relation."""
        return self.__src.id

    @property
    def dst(self) -> str:
        """Get the target GraphNode of this relation."""
        return self.__dst.id

    def get_source_node(self) -> "GraphNode":
        """Get the source GraphNode of this relation."""
        return self.__src

    def get_target_node(self) -> "GraphNode":
        """Get the target GraphNode of this relation."""
        return self.__dst

    def __getattr__(self, name: str, default: Any = None) -> Any:
        """Delegate attribute access to the underlying Relation."""
        # Avoid recursion by only delegating to __node
        if name.startswith("_GraphRelation__"):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

        try:
            if hasattr(self.__relation, name):
                return getattr(self.__relation, name, default)

        except AttributeError:
            return default
