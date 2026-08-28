from typing import Any, Literal, Optional
import warnings
from diagrams import Diagram, c4

try:
    from diagrams import c4  # type: ignore

    _HAS_DIAGRAMS_C4 = True
except (ImportError, ModuleNotFoundError):
    warnings.warn(
        "Optional dependency 'diagrams.c4' not available. C4DiagramFormatter will be limited or unavailable.",
        UserWarning,
    )
    # Fallback: set c4 to None if diagrams.c4 cannot be imported
    c4 = None  # type: ignore
    _HAS_DIAGRAMS_C4 = False

from .c4_formatter import get_attribute

DEFAULT_TYPE_MAP = {
    "requirement": c4.Container,
    "node": c4.Container,
    "system": c4.System,
    "component": c4.System,
    "database": c4.Database,
    "grouping": c4.SystemBoundary,
    "person": c4.Person,
    "role": c4.Person,
    "business_function": c4.Person,
    "issue": c4.Container,
    "feature": c4.Container,
}


class C4DiagramFormatter:
    def __init__(
        self,
        output_format: Literal["png", "svg", "pdf", "dot"] = "svg",
        file_name: Optional[str] = None,
        title: Optional[str] = None,
        type_map: dict[str, Any] = DEFAULT_TYPE_MAP,
        type_attribute_overrides: Optional[dict[str, dict[str, str]]] = None,
    ):
        self.__output_format = output_format
        self.__file_name = file_name
        self.__title = title
        self.__type_map = {**type_map}
        self.__type_attribute_overrides = (
            type_attribute_overrides if type_attribute_overrides else {}
        )

    def _format_node(
        self, node: Any, node_cache: dict[str, Any], node_attr: dict[str, Any] = {}
    ) -> None:
        node_type = get_attribute(node, "type", None)
        if node_type in self.__type_map:
            node_class = self.__type_map[node_type]
        else:
            node_class = c4.Container  # Default to Container if type not found

        node_id = get_attribute(node, "id", None)
        if node_id is None:
            raise ValueError("Node must have an 'id' attribute.")

        attribute_overrides = self.__type_attribute_overrides.get(node_type, {})

        args = {
            "name": get_attribute(node, "title", node_id),
            "description": get_attribute(node, "description", ""),
            "technology": get_attribute(node, "technology", ""),
            "external": get_attribute(node, "external", False),
            "width": get_attribute(node, "width", None),
            "height": get_attribute(node, "height", None),
            "type": node_type,
            "labelloc": get_attribute(node, "labelloc", None),
            "shape": get_attribute(node, "shape", None),
            "fontcolor": get_attribute(node, "fontcolor", None),
            "fillcolor": get_attribute(node, "fillcolor", None),
            "fixedsize": get_attribute(node, "fixedsize", None),
            "shape": get_attribute(node, "shape", None),
            "style": get_attribute(node, "style", None),
            "fillcolor": get_attribute(node, "fillcolor", None),
            "fontname": get_attribute(node, "fontname", None),
            "fontsize": get_attribute(node, "fontsize", None),
            "fixedsize": get_attribute(node, "fixedsize", None),
            "tooltip": get_attribute(
                node, "tooltip", get_attribute(node, "comment", None)
            ),
            "URL": get_attribute(node, "URL", get_attribute(node, "link", None)),
        }

        for k, v in attribute_overrides.items():
            if k not in args or args[k] is None:
                args[k] = v

        for k, v in node_attr.items():
            if k not in args or args[k] is None:
                args[k] = v

        diagram_node = node_class(
            **{k: str(v) for k, v in args.items() if v is not None}
        )
        node_cache[node_id] = diagram_node

        if hasattr(node, "children"):
            if isinstance(diagram_node, c4.Cluster):
                with diagram_node:
                    for child in node.children:
                        self._format_node(child, node_cache, node_attr)

            else:
                for child in node.children:
                    self._format_node(child, node_cache, node_attr)
                    if hasattr(child, "id"):
                        self._format_relation(
                            {"src": node_id, "dst": child.id, "type": "parent of"},
                            node_cache,
                        )

    def _format_relation(
        self, relation: Any, node_cache: dict[str, Any], edge_attr: dict[str, Any] = {}
    ) -> None:
        source_id = get_attribute(relation, "src", None)
        target_id = get_attribute(relation, "dst", None)

        if source_id not in node_cache or target_id not in node_cache:
            raise ValueError(
                f"Relation references unknown nodes: {source_id} -> {target_id}"
            )

        source_node = node_cache[source_id]
        target_node = node_cache[target_id]

        node_type = get_attribute(relation, "type", None)

        attribute_overrides = self.__type_attribute_overrides.get(node_type, {})

        args = {
            "label": node_type,
            "style": get_attribute(relation, "style", None),
            "color": get_attribute(relation, "color", None),
            "fontcolor": get_attribute(relation, "fontcolor", None),
            "fontsize": get_attribute(relation, "fontsize", None),
            "fontname": get_attribute(relation, "fontname", None),
            "tooltip": get_attribute(
                relation, "tooltip", get_attribute(relation, "comment", None)
            ),
            "URL": get_attribute(
                relation, "URL", get_attribute(relation, "link", None)
            ),
        }

        for k, v in attribute_overrides.items():
            if k not in args or args[k] is None:
                args[k] = v

        for k, v in edge_attr.items():
            if k not in args or args[k] is None:
                args[k] = v

        (
            source_node
            >> c4.Relationship(**{k: str(v) for k, v in args.items() if v is not None})
            >> target_node
        )

    def format(
        self,
        graph: Any,
        graph_attr: Optional[
            dict[
                Literal[
                    "bgcolor",
                    "center",
                    "concentrate",
                    "dpi",
                    "fontcolor",
                    "fontname",
                    "fontsize",
                    "label",
                    "inputscale",
                    "labelloc",
                    "labeljust",
                    "landscape",
                    "size",
                    "tooltip",
                    "URL",
                ],
                Any,
            ]
        ] = {},
        node_attr: Optional[
            dict[
                Literal[
                    "shape",
                    "style",
                    "fillcolor",
                    "fontcolor",
                    "fontname",
                    "fontsize",
                    "fixedsize",
                    "width",
                    "height",
                    "tooltip",
                    "URL",
                    "labelloc",
                ],
                Any,
            ]
        ] = {},
        edge_attr: Optional[
            dict[
                Literal[
                    "style",
                    "color",
                    "fontcolor",
                    "fontname",
                    "fontsize",
                    "tooltip",
                    "URL",
                ],
                Any,
            ]
        ] = {},
    ) -> Diagram:
        title = (
            self.__title
            if self.__title
            else get_attribute(graph, "title", "Architecture Diagram")
        )
        children = getattr(graph, "children", [])
        relations = getattr(graph, "relations", [])
        node_cache: dict[str, Any] = {}
        with Diagram(
            title,
            show=False,
            outformat=self.__output_format,
            filename=self.__file_name,
            graph_attr=graph_attr,
            edge_attr=edge_attr,
            node_attr=node_attr,
        ) as diag:
            for c in children:
                self._format_node(c, node_cache, node_attr)

            for r in relations:
                self._format_relation(r, node_cache, edge_attr)

        return diag
