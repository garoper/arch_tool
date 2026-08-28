"""
Formatter that exports a graph to an html file using the vis.js library.
"""

from typing import Dict, Iterable, Literal, Any, TypedDict, NotRequired, List, Tuple
from .visjs_types import (
    Color,
    EdgeConfig,
    Fixed,
    InteractionConfig,
    LayoutConfig,
    NodeConfig,
    PhysicsConfig,
    Shape,
    Margin,
    Image,
    IconConfig,
    ShapeProperties,
    ShadowConfig,
    WidthConstraintConfig,
    HeightConstraintConfig,
    ImagePaddingConfig,
    ScalingConfig,
    ArrowsConfig,
    EdgeColor,
    FontConfig,
    SelfReferenceConfig,
    SmoothConfig,
    WidthConstraintEdge,
)
import json
import os
import base64
import hashlib
import requests

VIS_NETWORK_SCRIPT_URL = (
    "https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"
)

TEMPLATE = """<!DOCTYPE html>
<html>
    <head>
        <title>{title}</title>
        <!-- embed vis.js library statically-->
        <script type="text/javascript">
        /*<![CDATA[*/
            {vis_network_script}
        /*]]>*/
        </script>
        <style type="text/css">
            #mynetwork {{
                width: 1280px;
                height: 720px;
                border: 1px solid lightgray;
            }}
        </style>
    </head>
    <body>
        <div id="graph"></div>
        <script type="text/javascript">
            function decodeBase64Json(base64String) {{
                try {{
                    // Convert to UTF-8
                    const bytes = Uint8Array.fromBase64(base64String);
                    const jsonString = new TextDecoder('utf-8').decode(bytes);
                    
                    // Parse JSON
                    return JSON.parse(jsonString);
                }} catch (error) {{
                    console.error('Failed to decode base64 data:', error);
                    throw error;
                }}
            }}
            const container = document.getElementById('graph');
            const data = decodeBase64Json('{data_base64}');
            const data_dict = {{}}
            for (let node of data.nodes) {{
                data_dict[node.id] = node
            }}
            const options = decodeBase64Json('{options_base64}');
            network = new vis.Network(container, data, options);

            network.on("hoverNode", function (params) {{
                const nodeId = params.node
                if (!(nodeId in data_dict)) {{
                    return;
                }}
                const node = data_dict[nodeId]
                const metadata = node['metadata'] || {{}}
                const url = metadata['link'] || metadata['url']
                if (url) {{
                    container.style.cursor = 'pointer';
                }} else {{
                    container.style.cursor = 'default';
                }}
            }});

            network.on("blurNode", function (params) {{
                container.style.cursor = 'default';
            }});

            network.on("doubleClick", function (params) {{
                // Check if exactly one node was clicked
                if (params.nodes.length !== 1) {{
                    return;
                }}
                const nodeId = params.nodes[0]
                if (nodeId in data_dict) {{
                    const node = data_dict[nodeId]
                    const metadata = node['metadata'] || {{}}
                    const url = metadata['link'] || metadata['url']
                    if (url) {{
                        // Open the URL in a new tab
                        window.open(url, '_blank') 
                    }}
                }}
            }});
        </script>
    </body>
</html>"""


def safe_get_value(obj: Any, key: str, default: Any = None) -> Any:
    """Safely get a value from a dict-like object, returning a default if not found."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def safe_get(
    obj: Any,
    attr: str | List[str] | Tuple[str],
    default: Any = None,
    override: dict | None = None,
) -> Any:
    """Safely get an attribute from an object, returning a default if not found."""
    if isinstance(attr, (list, tuple)):
        for a in attr:
            ret = safe_get(obj, a, None, override=override)
            if ret is not None:
                return ret
        return default

    if override:
        ret = safe_get_value(override, attr, None)
        if ret is not None:
            return ret

    return safe_get_value(obj, attr, default)


def create_node_template(
    border_width: float = 1.0,
    border_width_selected: float = 2.0,
    color: Color = "#ffffff",
    opacity: float = 1.0,
    fixed: Fixed = False,
    shape: Shape = "ellipse",
    size: float = 25,
    font: FontConfig | None = None,
    label: str | None = None,
    title: str | None = None,
    hidden: bool = False,
    physics: bool = True,
    mass: float = 1.0,
    shadow: ShadowConfig | bool = False,
    margin: Margin | None = None,
    image: Image | None = None,
    image_padding: ImagePaddingConfig | int = 0,
    icon: IconConfig | None = None,
    shape_properties: ShapeProperties | None = None,
    label_highlight_bold: bool = True,
    width_constraint: WidthConstraintConfig | int = None,
    height_constraint: HeightConstraintConfig | int = None,
    x: float | None = None,
    y: float | None = None,
    level: int | None = None,
    group: str | None = None,
    value: float | None = None,
    scaling: ScalingConfig = None,
) -> NodeConfig:
    """
    Create a node template for vis.js network visualization.

    Args:
        border_width: Width of the border of the node
        border_width_selected: Width of the border when selected
        color: Color configuration (string or dict with border/background/highlight/hover)
        opacity: Overall opacity of the node (0-1)
        fixed: Whether node is fixed in position (bool or dict with x/y)
        shape: Shape of the node (ellipse, circle, box, database, text, image, etc.)
        size: Size of the node (for shapes without label inside)
        font: Font configuration dict
        label: Label text for the node
        title: Tooltip text when hovering over the node
        hidden: Whether the node is hidden
        physics: Whether the node participates in physics simulation
        mass: Mass of the node for physics simulation
        shadow: Shadow configuration (bool or dict)
        margin: Margin around the label
        image: Image URLs for image-based shapes
        icon: Icon configuration for icon shape
        shape_properties: Additional shape properties
        label_highlight_bold: Whether label becomes bold when selected
        width_constraint: Width constraints (minimum/maximum)
        height_constraint: Height constraints (minimum/valign)
        x: Initial x position
        y: Initial y position
        level: Level for hierarchical layout
        group: Group membership for styling
        value: Value for scaling nodes
        scaling_config: Scaling configuration for the node

    Returns:
        Dict with node configuration
    """
    node_config = {
        "borderWidth": border_width,
        "borderWidthSelected": border_width_selected,
        "color": color,
        "opacity": opacity,
        "fixed": fixed,
        "font": font,
        "group": group,
        "heightConstraint": height_constraint,
        "hidden": hidden,
        "icon": icon,
        "image": image,
        "imagePadding": image_padding,
        "label": label,
        "labelHighlightBold": label_highlight_bold,
        "level": level,
        "mass": mass,
        "margin": margin,
        "shadow": shadow,
        "physics": physics,
        "scaling": scaling,
        "shape": shape,
        "shapeProperties": shape_properties,
        "size": size,
        "widthConstraint": width_constraint,
        "title": title,
        "value": value,
        "x": x,
        "y": y,
    }
    # Remove keys with None values to keep the config clean
    return {k: v for k, v in node_config.items() if v is not None}


def create_edge_template(
    arrows: ArrowsConfig | str = None,
    color: EdgeColor | str = "#848484",
    dashes: bool | list[int] = False,
    font: FontConfig | None = None,
    from_: float | int | str | None = None,
    hidden: bool = False,
    hover_width: float = 1.0,
    id: float | int | str | None = None,
    label: str | None = None,
    label_highlight_bold: bool = True,
    length: float | None = None,
    physics: bool = True,
    scaling: ScalingConfig = None,
    selection_width: float = 1.0,
    self_reference_size: float | None = None,
    self_reference: SelfReferenceConfig | None = None,
    shadow: ShadowConfig | bool = False,
    smooth: SmoothConfig | bool = True,
    title: str | None = None,
    to: float | int | str | None = None,
    value: float | None = None,
    width: float = 1.0,
    width_constraint: WidthConstraintEdge | bool | int | None = None,
) -> EdgeConfig:
    """
    Create an edge template for vis.js network visualization.

    Args:
        arrows: Arrow configuration (bool, string, or dict)
        color: Color configuration (string or dict with color/highlight/hover)
        dashes: Whether the edge is dashed (bool or list of dash lengths)
        font: Font configuration dict
        from_: Source node ID
        hidden: Whether the edge is hidden
        hover_width: Width of the edge when hovered
        id: Unique identifier for the edge
        label: Label text for the edge
        length: Length of the edge
        physics: Whether the edge participates in physics simulation
        scaling: Scaling configuration for the edge
        selection_width: Width of the edge when selected
        self_reference: Self-reference configuration for the edge
        shadow: Shadow configuration for the edge
        smooth: Smoothness configuration for the edge
        title: Tooltip text when hovering over the edge
        to: Target node ID
        value: Value for the edge
        width: Width of the edge
        width_constraint: Width constraints for the edge

    Returns:
        Dict with edge configuration
    """
    edge_config = {
        "arrows": arrows,
        "color": color,
        "dashes": dashes,
        "font": font,
        "from": from_,
        "hidden": hidden,
        "hoverWidth": hover_width,
        "id": id,
        "label": label,
        "labelHighlightBold": label_highlight_bold,
        "length": length,
        "physics": physics,
        "scaling": scaling,
        "selectionWidth": selection_width,
        "selfReferenceSize": self_reference_size,
        "selfReference": self_reference,
        "shadow": shadow,
        "smooth": smooth,
        "title": title,
        "to": to,
        "value": value,
        "width": width,
        "widthConstraint": width_constraint,
    }
    # Remove keys with None values to keep the config clean
    return {k: v for k, v in edge_config.items() if v is not None}


def create_group_template(
    use_default_group: bool = True,
    groups: Dict[str, NodeConfig] = None,
) -> Dict[str, NodeConfig | bool]:
    """
    Create a group template for vis.js network visualization.

    Args:
        use_default_group: Whether to use the default group configuration
        groups: Dictionary of group configurations (as returned by create_node_template)

    Returns:
        Dict with group configuration
    """

    group_config = {k: v for k, v in groups.items() if v is not None}

    if use_default_group:
        group_config["useDefaultGroups"] = True

    return group_config


DEFAULT_FONT_CONFIG: FontConfig = {
    "multi": "markdown",
    "size": 10,
    "face": "Arial",
    "align": "center",
    "vadjust": 2,
    "bold": {
        "size": 14,
        "mod": "bold",
        "vadjust": -2,
    },
    "mono": {
        "face": "monospace",
        "size": 9,
        "vadjust": 0,
    },
    "boldital": {
        "size": 14,
        "color": "#030054",
        "mod": "bold italic",
        "vadjust": -2,
    },
}

DEFAULT_TYPE_PROPERTIES: Dict[str, NodeConfig] = {
    "node": create_node_template(border_width=1.0, shape="box"),
    "requirement": create_node_template(
        border_width=1.0,
        shape="box",
        title="{title}",
    ),
    "node": create_node_template(border_width=1.0, shape="ellipse"),
    "system": create_node_template(border_width=1.0, shape="box"),
    "component": create_node_template(border_width=1.0, shape="box"),
    "database": create_node_template(border_width=1.0, shape="database"),
    "grouping": create_node_template(border_width=2.0, shape="box"),
    "person": create_node_template(border_width=1.0, shape="ellipse"),
    "role": create_node_template(border_width=1.0, shape="ellipse"),
    "business_function": create_node_template(border_width=1.0, shape="ellipse"),
    "issue": create_node_template(border_width=1.0, shape="box"),
    "feature": create_node_template(border_width=1.0, shape="box"),
}

DEFAULT_EDGE_PROPERTIES: Dict[str, Any] = {
    "impacts": create_edge_template(
        arrows={"to": {"enabled": True, "type": "arrow", "scaleFactor": 1.0}}
    )
}


class VisJSFormatter:
    """
    Formatter that exports a graph to an html file using the vis.js library.
    """

    def __init__(
        self,
        auto_resize: bool = True,
        height: str = "100%",
        width: str = "100%",
        locale: str = "en",
        click_to_use: bool = False,
        layout: LayoutConfig = None,
        interaction: InteractionConfig = None,
        physics: PhysicsConfig = None,
        nodes: NodeConfig = None,
        edges: EdgeConfig = None,
        groups: Dict[str, NodeConfig | bool] = None,
        type_attribute_overrides: Dict[str, NodeConfig] = None,
        edge_attribute_overrides: Dict[str, EdgeConfig] = None,
    ):

        self.__type_attribute_overrides = {
            **DEFAULT_TYPE_PROPERTIES,
            **(type_attribute_overrides or {}),
        }
        self.__edge_attribute_overrides = {
            **DEFAULT_EDGE_PROPERTIES,
            **(edge_attribute_overrides or {}),
        }

        self.__options = {
            "autoResize": auto_resize,
            "height": height,
            "width": width,
            "locale": locale,
            "clickToUse": click_to_use,
            "layout": layout or {},
            "interaction": interaction
            or {
                "hover": True,
                "multiselect": False,
            },
            "groups": groups or {},
            "physics": physics or {},
            "nodes": nodes
            or {
                "font": DEFAULT_FONT_CONFIG,
                "margin": {
                    "bottom": 20,
                    "top": 10,
                    "left": 10,
                    "right": 10,
                },
            },
            "edges": edges or {},
        }

    @property
    def options(self) -> Dict[str, Any]:
        """Get the vis.js network options."""
        return self.__options

    def __format_label(self, node: Any, metadata: Dict[str, Any]) -> str | None:
        header = safe_get(node, ["title", "id"], "", override=metadata)
        if metadata and "url" in metadata or "link" in metadata:
            header = f"_{header}_"
        subtitle = safe_get(node, "technology", "foo", override=metadata)
        subtitle = f"\n`[{subtitle}]`" if subtitle else ""
        text = safe_get(node, ["description", "text"], "textttt", override=metadata)
        text = f"\n{text}" if text else ""

        return f"*{header}*{subtitle}{text}"

    def __format_node(self, node: Any) -> Dict[str, Any]:
        metadata = safe_get(node, "metadata", {})
        type_ = safe_get(node, "type", "node", override=metadata)
        if type_ not in self.__type_attribute_overrides:
            type_ = "node"  # Fallback to default type if unknown

        node_dict: NodeConfig = {**self.__type_attribute_overrides[type_]}
        for k, v in {
            "id": safe_get(node, "id", None, override=metadata),
            "label": self.__format_label(node, metadata),
            "group": safe_get(node, "group", None, override=metadata),
            "title": safe_get(node, ["tooltip", "comment"], None, override=metadata),
            "shape": safe_get(node, "shape", None, override=metadata),
            "metadata": metadata,
        }.items():
            if v is not None:
                node_dict[k] = v

        return node_dict

    def __format_relation(self, relation: Any) -> Dict[str, Any]:
        """Format a relation object into a vis.js edge configuration."""
        metadata = safe_get(relation, "metadata", {})
        type_ = safe_get(relation, "type", "relation", override=metadata)

        # Get edge template based on type if available
        if type_ in self.__edge_attribute_overrides:
            edge_dict: EdgeConfig = {**self.__edge_attribute_overrides[type_]}
        else:
            edge_dict: EdgeConfig = {}

        # Set edge properties
        for k, v in {
            "from": safe_get(relation, "src", None, override=metadata),
            "to": safe_get(relation, "dst", None, override=metadata),
            "label": safe_get(relation, "label", None, override=metadata),
            "title": safe_get(
                relation, ["tooltip", "comment", "description"], None, override=metadata
            ),
            "arrows": edge_dict.get(
                "arrows", "to"
            ),  # Default to arrow pointing to target
        }.items():
            if v is not None:
                edge_dict[k] = v

        return edge_dict

    def __collect_nodes(self, nodes: Iterable[Any] | Any) -> Iterable[Any]:
        if not nodes:
            return []

        if not isinstance(nodes, (list, tuple, set)):
            return self.__format_node(nodes)

        for node in nodes:
            yield self.__format_node(node)
            children = safe_get(node, "children", None)
            if children:
                yield from self.__collect_nodes(children)

    def __collect_edges(self, nodes: Iterable[Any] | Any) -> Iterable[Any]:
        if not nodes:
            return []

        if not isinstance(nodes, (list, tuple, set)):
            for relation in getattr(nodes, "relations", []):
                yield self.__format_relation(relation)

        for node in nodes:
            for relation in getattr(node, "relations", []):
                yield self.__format_relation(relation)

    def format(
        self, nodes: Iterable[Any] | Any, file_name: str | None = None
    ) -> str | None:
        """Format the given graph into an HTML string using vis.js."""
        # Implementation of the formatting logic goes here
        vis_network_script = self.__load_visjs_script()
        options_json = json.dumps(self.__options)
        options_base64 = base64.b64encode(options_json.encode("utf-8")).decode("utf-8")

        all_nodes = list(self.__collect_nodes(nodes))
        all_edges = list(self.__collect_edges(nodes))
        data_json = json.dumps(
            {"nodes": all_nodes, "edges": all_edges}
        )  # Example data structure
        data_base64 = base64.b64encode(data_json.encode("utf-8")).decode("utf-8")
        html_content = TEMPLATE.format(
            title="Graph Visualization",
            vis_network_script=vis_network_script,
            data_base64=data_base64,
            options_base64=options_base64,
        )
        if file_name:
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            with open(file_name, "w", encoding="utf-8") as file:
                file.write(html_content)
            return None
        else:
            return html_content

    def clear_cache(self) -> None:
        """Clear the cached vis.js script."""
        cache_path = self.__get_cache_path()
        if os.path.exists(cache_path):
            os.remove(cache_path)

    def __download_visjs_script(self) -> str:
        """Download the vis.js network script content."""

        response = requests.get(VIS_NETWORK_SCRIPT_URL)
        response.raise_for_status()
        script = response.text
        if script.find("]]>") >= 0:
            raise ValueError(
                "Downloaded vis.js script is invalid. Contains ']]>' sequence which breaks CDATA."
            )
        return script

    def __get_cache_path(self) -> str:
        """Get the path to the cached vis.js script."""
        default_path = os.path.join(os.path.expanduser("~"), ".cache")
        if os.name == "nt":
            cache_dir = os.path.join(
                os.getenv("LOCALAPPDATA", default_path), "arch_tool"
            )
        else:
            cache_dir = os.path.join(
                os.getenv("XDG_CACHE_HOME", default_path), "arch_tool"
            )

        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, "vis-network.min.js")

    def __load_visjs_script(self) -> str:
        """Load the vis.js network script from cache or download it."""
        cache_path = self.__get_cache_path()

        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as file:
                return file.read()
        else:
            script_content = self.__download_visjs_script()
            with open(cache_path, "w", encoding="utf-8") as file:
                file.write(script_content)
            return script_content
