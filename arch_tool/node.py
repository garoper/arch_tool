"""
A node is a representation of a single object within the architecture graph. It holds information about the object, such as type, title, description, children, tags and other custom meta data.

The node can be instantiated as different types, depending on the type of object it represents. Examples of node types include 'requirement', 'system', 'component', 'issue', 'feature', 'database', 'person', 'grouping'.

Nodes can be serialized to and from dictionaries for easy storage and retrieval.

Nodes can also be visualized in C4 diagrams. Use the C4Formatter class to convert nodes to PlantUML syntax.
"""

import re
from typing import Iterable, List, Dict, Any, Optional, Set
import json

def convert_generators_to_lists(data: Any) -> Any:
    """convert any generator to a list."""
    if isinstance(data, Iterable) and not isinstance(data, (dict, list, set, tuple, str, bytes)):
        return [convert_generators_to_lists(item) for item in data]
    else:
        return data

def validate_id(id: str) -> None:
    """Validate that the given id is a non-empty string matching the pattern ^[a-zA-Z0-9_.-]+$."""
    if not isinstance(id, str) or not id:
        raise ValueError("ID must be a non-empty string.")
    if not re.match(r"^[a-zA-Z0-9_.\-]+$", id):
        raise ValueError("ID must match the pattern ^[a-zA-Z0-9_.-]+$.")


class Node:
    __types = {}

    def __init__(
        self, id: str, type: str = "node", metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None, comment: Optional[str] = None
    ) -> None:
        """Initialize a Node with a unique identifier."""
        validate_id(id)
        self.__id: str = id
        self.__type: str = type
        self.__metadata: Dict[str, Any] = metadata if metadata is not None else {}
        self.__tags: Set[str] = set(tags) if tags is not None else set()
        self.comment: Optional[str] = comment

    def add_tag(self, tag: str) -> None:
        """Add a tag to the Node."""
        self.__tags.add(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the Node."""
        self.__tags.discard(tag)

    def has_tag(self, tag: str) -> bool:
        """Check if the Node has a specific tag."""
        return tag in self.__tags

    @property
    def tags(self) -> Iterable[str]:
        """Get immutable list of tags associated with the Node."""
        yield from iter(self.__tags)
        if not self.__type.lower() in self.__tags:
            yield self.__type.lower()

    @property
    def id(self) -> str:
        """The unique identifier of the node."""
        return self.__id

    @property
    def type(self) -> str:
        """The type of the node."""
        return self.__type

    @property
    def metadata(self) -> Dict[str, Any]:
        """The metadata dictionary of the node. Can be used by a user to store custom information about the node."""
        return self.__metadata

    def to_dict(self) -> Dict[str, Any]:
        """Serialize all properties of the Node to a dictionary."""
        ret = {}
        for key in dir(self):
            if key.startswith("_"):
                continue
            attr = getattr(self, key)
            if not callable(attr):
                ret[key] = convert_generators_to_lists(attr)

        return ret

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Node":
        """Deserialize a Node from a dictionary."""
        if not all(key in data for key in ("id", "type")):
            raise ValueError("Data must contain 'id' and 'type' keys.")
        if not data["type"] in Node.__types:
            raise ValueError(f"Unknown node type: {data['type']}")
        type = data["type"]
        cls = Node.__types[type]

        metadata = data.get("metadata", {})

        # Build constructor arguments
        constructor_args = {
            "id": data["id"],   
            "type": data["type"],
            "metadata": metadata,
        }
                
        # Inspect the constructor to find required parameters
        # and populate them from data 
        import inspect
        sig = inspect.signature(cls.__init__)
        for param_name, _ in sig.parameters.items():
            if param_name == "self" or param_name in constructor_args:
                continue
            
            # If this parameter is not already set and exists in data, use it
            if param_name in data:
                constructor_args[param_name] = data[param_name]
        
        for k, v in data.items():
            if k not in constructor_args:
                metadata[k] = v
                
        return cls(**constructor_args)

    def __repr__(self) -> str:
        return f"Node(id={self.__id}, type={self.__type})"

    def dumps(self) -> str:
        """Return a string representation of the Node."""
        return json.dumps(self.to_dict(), indent=4)

    @staticmethod
    def register_type(type_cls: type, type_name: str) -> None:
        """Register a new node type.
        
        Args:
            type_cls: The class to register
            type_name: The type name string
        """
        if type_name in Node.__types:
            if Node.__types[type_name] != type_cls:
                raise ValueError(f"Node type '{type_name}' is already registered.")
            return

        Node.__types[type_name] = type_cls


Node.register_type(Node, "node")
