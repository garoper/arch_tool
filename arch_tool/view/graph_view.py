from arch_tool import Node, Graph, Relation
from typing import Dict, Iterable, Callable, Literal, Optional, Any, Set, TypeAlias
import collections.abc
import builtins

from arch_tool.view.graph_relation import GraphRelation

from .graph_index import GraphIndex
from .graph_node import GraphNode

NodeFilter: TypeAlias = Callable[[GraphNode | Node], bool]
RelationFilter: TypeAlias = Callable[[GraphRelation | Relation], bool]
AttributeFilter: TypeAlias = Dict[
    str, bool | str | int | float | Iterable[str | int | float]
]
IdFilter: TypeAlias = str | Node | GraphNode | Iterable[str | Node | GraphNode]


def build_node_filter(
    filter: IdFilter | AttributeFilter | NodeFilter | None,
) -> NodeFilter:
    """
    Build a node filter function based on the provided filter criteria.
    """
    if filter is None:
        return lambda _: True
    if isinstance(filter, str):
        return lambda node: node.id == filter
    if hasattr(filter, "id"):
        return lambda node: node.id == filter.id
    if isinstance(filter, dict):
        check_filter_dict(filter)
        return lambda node: all(
            (
                getattr(node, key, None) == value
                if isinstance(value, (str, int, float, bool))
                else getattr(node, key, None) in value
            )
            for key, value in filter.items()
        )
    if isinstance(filter, collections.abc.Iterable):
        id_set: Set[str] = set()
        for item in filter:
            if isinstance(item, str):
                id_set.add(item)
            elif hasattr(item, "id"):
                id_set.add(item.id)
            else:
                raise ValueError(
                    "The supplied filter argument if iterable, should either be an id string or an object with an 'id'-attribute."
                )
        return lambda node: node.id in id_set
    if callable(filter):
        return filter
    raise ValueError("Invalid filter type")


def build_relation_filter(
    filter: RelationFilter | AttributeFilter | IdFilter | None,
) -> RelationFilter:
    """
    Build a relation filter function based on the provided filter criteria.
    """
    if filter is None:
        return lambda _: True
    if isinstance(filter, str):
        return lambda rel: rel.id == filter
    if hasattr(filter, "id"):
        return lambda rel: rel.id == filter.id
    if isinstance(filter, dict):
        check_filter_dict(filter)
        return lambda rel: all(
            (
                getattr(rel, key, None) == value
                if isinstance(value, (str, int, float, bool))
                else getattr(rel, key, None) in value
            )
            for key, value in filter.items()
        )
    if isinstance(filter, collections.abc.Iterable):
        id_set: Set[str] = set()
        for item in filter:
            if isinstance(item, str):
                id_set.add(item)
            elif hasattr(item, "id"):
                id_set.add(item.id)
            else:
                raise ValueError(
                    "The supplied filter argument if iterable, should either be an id string or an object with an 'id'-attribute."
                )
        return lambda rel: rel.id in id_set
    if callable(filter):
        return filter
    raise ValueError("Invalid filter type")


def check_filter_dict(filter):
    for _, v in filter.items():
        if isinstance(v, (str, int, float, bool)):
            continue
        if isinstance(v, collections.abc.Iterable):
            continue
        else:
            raise ValueError(f"Unsupported property value type {type(v)} for indexing.")


"""
A GraphView provides a filtered view of a Graph, allowing inclusion and exclusion
of specific nodes and relations based on various criteria.
"""


class GraphView:
    """
    Provides a filtered and extendable view of a Graph, allowing inclusion and exclusion
    of nodes and relations based on various criteria. Useful for creating subgraphs,
    exploring relationships, and managing graph subsets for visualization or analysis.
    """

    def __init__(
        self, graph: Graph, include_all: bool = False, title: Optional[str] = None
    ):
        """Initialize a GraphView."""
        self.__index = GraphIndex(graph)
        if title is not None:
            self.title = title

        self.__included_nodes: Dict[str, bool] = (
            {node.id: True for node in self.__index.nodes} if include_all else {}
        )

        self.__included_edges: Dict[str, bool] = (
            {rel.id: True for rel in self.__index.relations} if include_all else {}
        )

        self.__graph = graph

    @property
    def children(self) -> Iterable["GraphNode"]:
        """Get the children nodes as GraphNodes. If the actual child nodes to the root node are hidden, the first visible child will automatically be included.

        Yields:
            GraphNode: The child GraphNodes of this graph view.
        """
        for path in self.__index.node_paths:
            if (
                len(path) >= 2
                and self.__included_nodes.get(path[-1].id, False)
                and sum(1 for p in path[1:] if self.__included_nodes.get(p.id, False))
                == 1
            ):
                yield GraphNode(path, self)

    @property
    def relations(self) -> Iterable[GraphRelation]:
        """Get the relations from the underlying graph."""
        for relation in self.__index.relations:
            src = self.get_node(relation.src)
            if src is None:
                continue
            dst = self.get_node(relation.dst)
            if dst is None:
                continue
            yield GraphRelation(relation, src, dst)

    def get_node(self, node_id: str, all: bool = False) -> Optional["GraphNode"]:
        """Get a GraphNode by its ID.

        Args:
            node_id: The ID of the node to retrieve.

        Returns:
            The corresponding GraphNode, or None if not found.
        """
        if not all and not self.__included_nodes.get(node_id, False):
            return None

        path = self.__index.get_path(node_id)
        if path is None:
            return None

        return GraphNode(path, self)

    def include_nodes(
        self,
        filter: IdFilter | AttributeFilter | NodeFilter,
    ) -> None:
        """Include specific nodes in the GraphView.

        Args:
            nodes: Nodes to include, specified by ID, GraphNode, or a filter function.
        """
        for n in self.get_nodes(filter, all=True):
            self.__included_nodes[n.id] = True

    def exclude_nodes(
        self,
        filter: IdFilter | AttributeFilter | NodeFilter,
    ) -> None:
        """Exclude specific nodes from the GraphView."""
        for n in self.get_nodes(filter, all=False):
            self.__included_nodes.pop(n.id, None)

    def update(self) -> None:
        """Update the GraphView to reflect changes in the underlying Graph.

        Note that new nodes will not be included unless explicitly added.
        """
        self.__index = GraphIndex(self.__graph)
        self.__included_nodes = {
            node.id: True
            for node in self.__index.nodes
            if node.id in self.__included_nodes
        }

    def extend(
        self,
        relation_filter: RelationFilter | AttributeFilter | IdFilter,
        node_filter: IdFilter | AttributeFilter | NodeFilter = None,
        depth: int = 0,
        direction : Literal["incoming", "outgoing", "both"] = "both"
    ) -> None:
        """Extend the GraphView by including related nodes and relations. This includes parents and children (which can be filtered by type = 'parent of').

        Args:
            relation_filter: A filter to select relations.
            node_filter: A filter to select nodes.
            depth: The depth to extend the view.
        """
        if depth < 0:
            return
        relation_filter_fn = build_relation_filter(relation_filter)
        node_filter = build_node_filter(node_filter)

        to_process = [
            self.get_node(k) for k, v in self.__included_nodes.items() if v is True
        ]
        for _ in range(depth):
            next_to_process = []
            for node in to_process:
                for r in self.__index.lookup_relations(
                    [{"src": node.id}, {"dst": node.id}]
                ):
                    graph_relation = GraphRelation(
                        r, self.get_node(r.src, True), self.get_node(r.dst, True)
                    )
                    if not relation_filter_fn(graph_relation):
                        continue
                    includes_src = self.__included_nodes.get(graph_relation.src, False)
                    includes_dst = self.__included_nodes.get(graph_relation.dst, False)
                    if includes_src and includes_dst:
                        self.__included_edges[graph_relation.id] = True
                    elif depth <= 0:
                        # do not extend further
                        continue
                    elif not includes_dst and direction != "incoming" and node_filter(
                        graph_relation.get_target_node()
                    ):
                        self.__included_edges[graph_relation.id] = True
                        self.__included_nodes[graph_relation.dst] = True
                        next_to_process.append(graph_relation.get_target_node())
                    elif not includes_src and direction != "outgoing" and node_filter(
                        graph_relation.get_source_node()
                    ):
                        self.__included_edges[graph_relation.id] = True
                        self.__included_nodes[graph_relation.src] = True
                        next_to_process.append(graph_relation.get_source_node())
            if not next_to_process:
                break
            to_process = next_to_process

    def get_nodes(
        self,
        filter: IdFilter | AttributeFilter | NodeFilter | None = None,
        all: bool = False,
    ) -> Iterable["GraphNode"]:
        """Get nodes from the GraphView based on a filter.

        Args:
            filter: A filter to select nodes. Can be a string (node ID), an iterable of strings (node IDs),
                    a dictionary of properties to match, or a callable that takes a GraphNode and returns a bool.

        Returns:
            An iterable of matching GraphNodes.
        """
        if filter is None:
            for path in self.__index.node_paths:
                if all or self.__included_nodes.get(path[-1].id, False):
                    yield self.get_node(path[-1].id, all)
            return

        if isinstance(filter, dict):
            for node in self.__index.lookup_nodes(filter):
                if all or self.__included_nodes.get(node.id, False):
                    yield self.get_node(node.id, all)
            return

        if isinstance(filter, str) or hasattr(filter, "id"):
            node_id = filter if isinstance(filter, str) else filter.id
            node = self.get_node(node_id, all)
            if node is not None:
                yield node
            return

        if isinstance(filter, collections.abc.Iterable) and not isinstance(
            filter, (str, dict)
        ):
            returned: Set[str] = set()
            for item in filter:
                for node in self.get_nodes(item, all):
                    if node.id in returned:
                        continue
                    returned.add(node.id)
                    yield node
            return

        if callable(filter):
            for path in self.__index.node_paths:
                node = GraphNode(path, self)
                if filter(node):
                    if all or self.__included_nodes.get(node.id, False):
                        yield node
            return

    def get_relations(
        self,
        filter: RelationFilter | AttributeFilter | IdFilter | None = None,
        all: bool = False,
    ) -> Iterable["GraphRelation"]:
        """Get relations from the GraphView based on a filter.

        Args:
            filter: A filter to select relations. Can be a dictionary of properties to match
                (matches both direct attributes and metadata keys), or a callable that takes
                a GraphRelation and returns a bool.
        Returns:
            An iterable of matching GraphRelations.
        """
        filter_function: Callable[["GraphRelation"], bool] = lambda r: True
        if isinstance(filter, str):
            filter_function = lambda r: r.id == filter
        elif hasattr(filter, "id"):
            filter_function = lambda r: r.id == filter.id
        elif isinstance(filter, dict):
            check_filter_dict(filter)
            filter_function = lambda r: builtins.all(
                (
                    (getattr(r, k, None) == v or r.relation.metadata.get(k) == v)
                    if isinstance(v, (str, int, float, bool))
                    else (getattr(r, k, None) in v or r.relation.metadata.get(k) in v)
                )
                for k, v in filter.items()
            )
        elif isinstance(filter, collections.abc.Iterable):
            id_set: Set[str] = set()
            for item in filter:
                if isinstance(item, str):
                    id_set.add(item)
                elif hasattr(item, "id"):
                    id_set.add(item.id)
                else:
                    raise ValueError(
                        "The supplied filter argument if iterable, should either be an id string or an object with an 'id'-attribute."
                    )

            filter_function = lambda r: r.id in id_set
        elif callable(filter):
            filter_function = filter
        elif filter is None:
            pass
        else:
            raise ValueError(
                f"Unsupported filter type {type(filter)} for relation lookup."
            )

        relations = (
            self.relations
            if not all
            else [
                GraphRelation(r, self.get_node(r.src, True), self.get_node(r.dst, True))
                for r in self.__index.relations
            ]
        )
        for relation in relations:
            if all or (
                self.__included_edges.get(relation.id, False)
                and self.__included_nodes.get(relation.src, False)
                and self.__included_nodes.get(relation.dst, False)
            ):
                if filter_function(relation):
                    yield relation

    def is_node_included(self, node_id: str) -> bool:
        """Check if a node is included in the GraphView.

        Args:
            node_id: The ID of the node to check.
        Returns:
            True if the node is included, False otherwise.
        """
        return self.__included_nodes.get(node_id, False)

    def __getattr__(self, name: str, default: Any = None) -> Any:
        """Delegate attribute access to the underlying Graph object.

        This allows GraphView to transparently proxy attributes like 'title',
        'description', etc. from the underlying Graph object.
        """
        # Avoid recursion by only delegating to __graph
        if name.startswith("_GraphView__"):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

        try:
            if hasattr(self.__graph, name):
                return getattr(self.__graph, name, default)
        except AttributeError:
            return default
            return default
