import logging

from .node import Node
from .container import Container
from .requirement import Requirement
from .feature import Feature
from .issue import Issue
from .grouping import Grouping
from .component import Component, System, Database
from .relation import Relation
from .graph import Graph
from .view import GraphRelation, GraphNode, GraphView
from .formatters import C4Formatter, JSONFormatter, C4DiagramFormatter


"""
arch_tool package initializer.

Keep this file minimal: expose package version and configure a null logger so
consuming applications don't see "No handler found" warnings.
"""

__all__ = [
    "Node",
    "Container",
    "Requirement",
    "Feature",
    "Issue",
    "Grouping",
    "Component",
    "System",
    "Database",
    "Graph",
    "C4Formatter",
    "JSONFormatter",
    "Relation",
    "GraphView",
    "GraphNode",
    "GraphRelation",
    "C4DiagramFormatter",
]

# Protect library users from "No handler found" warnings by adding a NullHandler.
# Consumers should configure logging for this package if they want output.
logging.getLogger(__name__).addHandler(logging.NullHandler())
