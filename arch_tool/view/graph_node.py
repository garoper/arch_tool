from arch_tool import Node
from typing import Iterable, Callable, Literal, Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .graph_view import GraphView
    from .graph_relation import GraphRelation


class GraphNode:
    """
    A GraphNode represents a node within a graph structure, allowing easy traversal and manipulation of its relationships.
    """

    def __init__(self, path: tuple[Node], graph: "GraphView", filtered: bool = True):
        """Initialize a GraphNode with a Node and its parent Graph.

        Args:
            path: The path taken to reach this node
            graph: The parent Graph containing the Node
        """
        self.__node: Node = path[-1]
        self.__path: tuple[Node] = path
        self.__graph: "GraphView" = graph
        self.__filtered: bool = filtered

    @property
    def parent(self) -> Optional["GraphNode"]:
        """Get the parent GraphNode of this node, if any."""
        if not self.__path or len(self.__path) <= 1:
            return None

        if not self.__filtered:
            return GraphNode(self.__path[:-1], self.__graph, filtered=False)

        for i in range(len(self.__path) - 2, -1, -1):
            if self.__graph.is_node_included(self.__path[i].id):
                return self.__graph.get_node(self.__path[i].id)

        return None

    @property
    def node(self) -> Node:
        """Get the underlying Node of this GraphNode."""
        return self.__node

    def _seek_closest_visible_descendants(self, node: Node) -> Iterable["GraphNode"]:
        """Recursively seek the closest visible descendants of a given GraphNode.

        Args:
            node: The starting GraphNode to search from.

        Yields:
            Visible descendant GraphNodes.
        """
        if not hasattr(node, "children"):
            return

        for child in node.children:
            if self.__graph.is_node_included(child.id):
                yield self.__graph.get_node(child.id, all=not self.__filtered)
            else:
                yield from self._seek_closest_visible_descendants(child)

    @property
    def children(self) -> Iterable["GraphNode"]:
        """Get the child GraphNodes of this node."""
        if not hasattr(self.__node, "children"):
            return []

        if not self.__filtered:
            for child in self.__node.children:
                yield self.__graph.get_node(child.id, all=True)
            return

        yield from self._seek_closest_visible_descendants(self.__node)

    def get_relations(
        self, direction: Literal["incoming", "outgoing", "both"] = "both"
    ) -> Iterable["GraphRelation"]:
        """Get the relations associated with this node."""
        filter = (
            (lambda r: r.src == self.id or r.dst == self.id)
            if direction == "both"
            else ({"dst": self.id} if direction == "incoming" else {"src": self.id})
        )
        
        yield from self.__graph.get_relations(filter=filter, all=not self.__filtered)

    def _iterate_related_nodes_recursive(
        self,
        direction: str,
        type: Optional[str | Iterable[str] | Callable[["GraphRelation"], bool]],
        processed: set[str] = set(),
        max_depth: int = 50,
    ) -> Iterable["GraphNode"]:
        """Recursively iterate related GraphNodes based on direction and type.

        Args:
            type: Optional type of relation to filter by
            direction: 'outgoing' for successors, 'incoming' for predecessors
        """
        processed.add(self.id)

        for relation in self.get_relations():
            if type is not None:
                if isinstance(type, str):
                    if relation.relation.type != type:
                        continue
                elif callable(type):
                    if not type(relation):
                        continue
                elif isinstance(type, Iterable):
                    if relation.relation.type not in type:
                        continue
            if direction == "outgoing":
                if relation.dst in processed:
                    continue
                dst_node = relation.get_target_node()
                yield dst_node
                if max_depth > 0:
                    yield from dst_node._iterate_related_nodes_recursive(
                        direction, type, processed, max_depth - 1
                    )
            elif direction == "incoming":
                if relation.src in processed:
                    continue
                src_node = relation.get_source_node()
                yield src_node
                if max_depth > 0:
                    yield from src_node._iterate_related_nodes_recursive(
                        direction, type, processed, max_depth - 1
                    )

    def successors(
        self,
        type: Optional[str | Iterable[str] | Callable[["GraphRelation"], bool]] = None,
        max_depth: int = 50,
    ) -> Iterable["GraphNode"]:
        """Get the successor GraphNodes connected by outgoing relations.

        Args:
            type: Optional type of relation to filter by
            max_depth: Maximum depth for recursive traversal

        Returns:
            An iterable of successor GraphNodes.
        """
        for relation in self._iterate_related_nodes_recursive(
            "outgoing", type, set(), max_depth
        ):
            yield relation

    def predecessors(
        self,
        type: Optional[str | Iterable[str] | Callable[["GraphRelation"], bool]] = None,
        max_depth: int = 50,
    ) -> Iterable["GraphNode"]:
        """Get the predecessor GraphNodes connected by incoming relations.

        Args:
            type: Optional type of relation to filter by
            max_depth: Maximum depth for recursive traversal

        Returns:
            An iterable of predecessor GraphNodes.
        """
        for relation in self._iterate_related_nodes_recursive(
            "incoming", type, set(), max_depth
        ):
            yield relation

    @property
    def descendants(self) -> Iterable["GraphNode"]:
        """Get all descendant GraphNodes of this node."""
        for child in self.children:
            yield child
            yield from child.descendants

    @property
    def ancestors(self) -> Iterable["GraphNode"]:
        """Get all ancestor GraphNodes of this node."""
        parent = self.parent
        while parent is not None:
            yield parent
            parent = parent.parent

    def has_descendant(
        self, filter: Dict[str, Any] | Callable[["GraphNode"], bool]
    ) -> bool:
        """Check if any descendant GraphNode satisfies the given filter function.

        Args:
            filter: A function that takes a GraphNode and returns True if it matches the criteria.
        Returns:
            True if any descendant GraphNode matches the filter, False otherwise.
        """
        if isinstance(filter, dict):
            return any(
                all(getattr(descendant, k) == v for k, v in filter.items())
                for descendant in self.descendants
            )
        elif callable(filter):
            return any(filter(descendant) for descendant in self.descendants)
        return False

    def has_relation(
        self, filter: Dict[str, Any] | Callable[["GraphRelation"], bool]
    ) -> bool:
        """Check if any GraphRelation satisfies the given filter function.

        Args:
            filter: A function that takes a GraphRelation and returns True if it matches the criteria.
        Returns:
            True if any GraphRelation matches the filter, False otherwise.
        """
        for relation in self.get_relations():
            if isinstance(filter, dict):
                if all(
                    getattr(relation, k) == v or relation.relation.metadata.get(k) == v
                    for k, v in filter.items()
                ):
                    return True
            elif callable(filter):
                if filter(relation):
                    return True
        return False

    def has_child(self, filter: Dict[str, Any] | Callable[["GraphNode"], bool]) -> bool:
        """Check if any child GraphNode satisfies the given filter function.

        Args:
            filter: A function that takes a GraphNode and returns True if it matches the criteria.

        Returns:
            True if any child GraphNode matches the filter, False otherwise.
        """
        for child in self.children:
            if isinstance(filter, dict):
                if all(
                    getattr(child, k) == v or child.node.metadata.get(k) == v
                    for k, v in filter.items()
                ):
                    return True
            elif callable(filter):
                if filter(child):
                    return True
        return False

    def __getattr__(self, name: str, default: Any = None) -> Any:
        """Delegate attribute access to the underlying node.

        This allows GraphNode to transparently proxy attributes like 'title',
        'description', etc. from the underlying Node object.
        """
        # Avoid recursion by only delegating to __node
        if name.startswith("_GraphNode__"):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

        try:
            if hasattr(self.__node, name):
                return getattr(self.__node, name, default)

        except AttributeError:
            return default
