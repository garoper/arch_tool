from .node import Node
from typing import Any, Dict, Iterable, Tuple, Optional


class Container(Node):
    def __init__(
        self,
        id: str,
        type: str = "container",
        metadata: Optional[Dict[str, Any]] = None,
        children: Iterable[Node | Dict[str, Any]] = [],
        tags: Optional[Iterable[str]] = None,
        comment: Optional[str] = None,
    ) -> None:
        """Initialize a Container with a unique identifier."""
        child_list = (
            [Node.from_dict(c) if isinstance(c, dict) else c for c in children]
            if children
            else []
        )

        self.__children: Dict[str, Node] = {child.id: child for child in child_list}

        super().__init__(
            id=id, type=type, metadata=metadata, tags=tags, comment=comment
        )

    def add_child(self, child: Node | Dict[str, Any]) -> None:
        """Add a child Node to the Container."""
        if isinstance(child, dict):
            child = Node.from_dict(child)
        self.__children[child.id] = child

    def remove_child(self, child: Node | str) -> None:
        """Remove a child Node from the Container."""
        child_id = child.id if isinstance(child, Node) else child
        self.__children.pop(child_id, None)

    def get_child(self, child_id: str) -> Optional[Node]:
        """Get a child Node by its ID."""
        return self.__children.get(child_id, None)

    def has_child(self, child_id: str) -> bool:
        """Check if a child Node with the given ID exists in the Container."""
        return child_id in self.__children

    @property
    def children(self) -> Iterable[Node]:
        """Get the list of child Nodes."""
        return self.__children.values()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize all properties of the Container to a dictionary.

        Overrides Node.to_dict() to properly handle the children property
        by converting dict_values to a list for JSON serialization.
        """
        result = super().to_dict()
        # Convert children from dict_values to list of dictionaries
        if "children" in result:
            result["children"] = [child.to_dict() for child in self.children]
        return result

    def traverse_nodes(
        node: Node, path: Optional[Tuple[Node, ...]] = None
    ) -> Iterable[Tuple[Node, ...]]:
        """Helper method to traverse the graph and yield paths to each node.

        Args:
            node: The current Node to traverse.
            path: The current path taken to reach this node.

        Yields:
            Tuples representing the path to each node in the graph.
        """
        if path is None:
            path = (node,)

        yield path

        if not hasattr(node, "children"):
            return

        for child in node.children:
            if isinstance(child, Container):
                yield from Container.traverse_nodes(child, path + (child,))
            else:
                yield path + (child,)


Node.register_type(Container, "container")
