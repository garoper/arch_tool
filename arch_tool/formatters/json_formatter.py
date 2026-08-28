"""
JSON formatter for architecture tool.
"""

import json
from typing import Any, Callable, Dict, Iterable, Optional, TextIO

from arch_tool import Node


class JSONFormatter:
    def __init__(
        self, node_factory: Optional[Callable[[Dict[str, Any]], Any]] = Node.from_dict
    ):
        self._node_factory = node_factory

    def format(self, data: Dict[str, Any] | Iterable[Dict[str, Any]]) -> str:
        return json.dumps(data, indent=4)

    def parse(self, data_str: str) -> Any:
        """Parse a JSON string into node object(s).

        Args:
            data_str: JSON string to parse

        Returns:
            Node object(s) if node_factory is configured, otherwise raw data
        """
        data = json.loads(data_str)
        if self._node_factory:
            if isinstance(data, list):
                return [self._node_factory(item) for item in data]
            else:
                return self._node_factory(data)
        return data

    def dump(
        self, data: Dict[str, Any] | Iterable[Dict[str, Any]], file: TextIO
    ) -> None:
        """Dump JSON data to a file object.

        Args:
            data: Data to serialize (dict or list of dicts)
            file: File object opened for writing (text mode)
        """
        json.dump(data, file, indent=4)

    def load(self, file: TextIO) -> Any:
        """Load and parse JSON data from a file object.

        Args:
            file: File object opened for reading (text mode)

        Returns:
            Node object(s) if node_factory is configured, otherwise raw data
        """
        data = json.load(file)
        if self._node_factory:
            if isinstance(data, list):
                return [self._node_factory(item) for item in data]
            else:
                return self._node_factory(data)
        return data
