from arch_tool.graph import Graph, Node
from typing import Dict, Iterable, Optional, Any, List, Tuple
from itertools import chain

from arch_tool.relation import Relation
from arch_tool.view.graph_node import GraphNode


def get_attribute(node: Node, attribute_name: str) -> Optional[Any]:
    """Helper method to get an attribute from a Node.

    Args:
        node: The Node to get the attribute from.
        attribute_name: The name of the attribute.

    Returns:
        The value of the attribute if it exists, otherwise None.
    """

    return node.metadata.get(attribute_name, getattr(node, attribute_name, None))


def set_index(index: Dict[Any, List[Node]], node: Node, prop_value: Any) -> None:
    if isinstance(prop_value, (str, int, float, bool)):
        if prop_value is not None:
            if prop_value not in index:
                index[prop_value] = []
            index[prop_value].append(node)
        return

    if isinstance(prop_value, (Node, GraphNode)):
        prop_value = prop_value.id
        if prop_value not in index:
            index[prop_value] = []
        index[prop_value].append(node)
        return

    if isinstance(prop_value, (tuple, list, Iterable)):
        for val in prop_value:
            set_index(index, node, val)
        return

    raise ValueError(
        f"Unsupported property value type {type(prop_value)} for indexing."
    )



class GraphIndex:
    """Class representing a graph index for efficient node lookups."""

    def __init__(self, graph: Graph):
        """Initialize the GraphIndex with a given Graph.

        Args:
            graph: The Graph to index.
        """
        self.__nodes: Dict[str, Tuple[Node]] = {
            path[-1].id: path for path in graph.traverse_nodes()
        }
        self.__relations: Tuple[Relation] = tuple(rel for rel in graph.relations)
        self.__node_indices: Dict[str, Dict[Any, List[Node]]] = {}
        self.__relation_indices: Dict[str, List[Relation]] = {}

    def _parent_child_relations(self) -> Iterable[Relation]:
        """Generate parent-child relations for all nodes in the graph."""
        for path in self.__nodes.values():
            # skip root nodes without parents
            if len(path) < 2:
                continue
            parent = path[-2]
            child = path[-1]
            relation = Relation(
                type="parent of",
                src=parent.id,
                dst=child.id
            )
            yield relation

    def lookup_relations(
        self,
        filter: Iterable[str | Relation | Dict[str, Any]] | str | Relation | Dict[str, Any] = None,
        include_implied: bool = True,
    ) -> Iterable[Relation]:
        """Lookup relations by a specific property value.

        Args:
            filter: The property name to lookup relations by.
            include_implied: Whether to include implied relations (specifically parent-child relations).
        Returns:
            An iterable of matching relations.
        """
        all_relations = chain(
            self.__relations, self._parent_child_relations()) if include_implied else self.__relations

        if filter is None:
            for relation in all_relations:
                yield relation
                
        elif isinstance(filter, str):
            for relation in all_relations:
                if relation.id == filter:
                    yield relation
        elif isinstance(filter, Relation):
            for relation in all_relations:
                if relation.id == filter.id:
                    yield relation
        elif isinstance(filter, dict):
            for relation in all_relations:
                is_match = True
                for key, value in filter.items():
                    if isinstance(value, (str, int, float, bool)):
                        if getattr(relation, key, None) != value:
                            is_match = False
                            break
                    elif isinstance(value, (list, tuple)):
                        if getattr(relation, key, None) not in value:
                            is_match = False
                            break
                    else:
                        raise ValueError(
                            f"Unsupported property value type {type(value)} for indexing."
                        )
                if is_match:
                    yield relation
        elif isinstance(filter, (list, tuple, Iterable)):
            for item in filter:
                yield from self.lookup_relations(item)
        else:
            raise ValueError(
                f"Unsupported filter type {type(filter)} for relation lookup."
            )

    def lookup_nodes(
        self,
        filter: Iterable[str | Node | Dict[str, Any]] | str | Node | Dict[str, Any] = None,
    ) -> Iterable[Node]:
        """Lookup nodes by a specific property value.

        Args:
            filter: The property name to lookup nodes by.


        Returns:
            An iterable of matching nodes.
        """
        if filter is None:
            for path in self.__nodes.values():
                yield path[-1]
        elif isinstance(filter, str):
            match = self.__nodes.get(filter, None)
            if match is not None:
                yield match[-1]
        elif isinstance(filter, Node):
            match = self.__nodes.get(filter.id, None)
            if match is not None:
                yield match[-1]
        elif isinstance(filter, dict):
            matches: Dict[str, int] = {}
            for key, value in filter.items():
                index = self.__node_indices.get(key, self.build_node_index(key) or self.__node_indices[key])

                if isinstance(value, (str, int, float, bool)):
                    for node in index.get(value, []):
                        matches[node.id] = (
                            matches[node.id] + 1 if node.id in matches else 1
                        )

                elif isinstance(value, (list, tuple)):
                    node_match_ids = set()
                    for val in value:
                        for node in index.get(val, []):
                            node_match_ids.add(node.id)
                    for node_id in node_match_ids:
                        matches[node_id] = (
                            matches[node_id] + 1 if node_id in matches else 1
                        )
                else:
                    raise ValueError(
                        f"Unsupported property value type {type(value)} for indexing."
                    )
            required_match_count = len(filter)
            for node_id, match_count in matches.items():
                if match_count == required_match_count:
                    yield self.__nodes[node_id][-1]
        elif isinstance(filter, (list, tuple, Iterable)):
            for item in filter:
                yield from self.lookup_nodes(item)
        else:
            raise ValueError(f"Unsupported filter type {type(filter)} for node lookup.")

    def build_node_index(self, property_name: str) -> None:
        """Build an index for nodes based on a specific property.

        Args:
            property_name: The property name to index nodes by.
        """
        index: Dict[Any, List[Node]] = {}
        for path in self.__nodes.values():
            node = path[-1]
            prop_value = get_attribute(node, property_name)
            set_index(index, node, prop_value)
        self.__node_indices[property_name] = index

    def build_relation_index(self, property_name: str) -> None:
        """Build an index for relations based on a specific property.

        Args:
            property_name: The property name to index relations by.
        """
        index: Dict[Any, List[Relation]] = {}
        for relation in self.__relations:
            prop_value = get_attribute(relation, property_name)
            set_index(index, relation, prop_value)
        self.__relation_indices[property_name] = index

    def has_node(self, id: str) -> bool:
        return id in self.__nodes

    def get_path(self, id: str) -> Optional[Tuple[Node, ...]]:
        """Retrieve the path to a node by its ID.

        Args:
            id: The unique identifier of the node.

        Returns:
            A tuple representing the path to the node if found, otherwise None.
        """
        if self.has_node(id) is False:
            return None

        return self.__nodes[id]

    @property
    def node_paths(self) -> Iterable[Tuple[Node, ...]]:
        """Get all node paths in the graph index."""
        return self.__nodes.values()

    @property
    def relations(self) -> Iterable[Relation]:
        """Get all relations in the graph index."""
        return self.__relations

    @property
    def nodes(self) -> Iterable[Node]:
        """Get all nodes in the graph index."""
        for path in self.__nodes.values():
            yield path[-1]
