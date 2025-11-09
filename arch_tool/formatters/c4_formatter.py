"""
C4 formatter for serializing and parsing C4 PlantUML diagram elements.

This module provides a formatter class that manages the conversion between
Node objects and PlantUML C4 diagram syntax.

Usage:
    Create a C4Formatter instance with a mapping of node types to C4 element types,
    then use it to format nodes to PlantUML or parse PlantUML back to nodes:

    >>> from arch_tool import Node, Requirement, C4Formatter
    >>>
    >>> # Create formatter with type mappings
    >>> formatter = C4Formatter(type_map={
    ...     "requirement": "Container",
    ...     "system": "System",
    ...     "component": "Component"
    ... })
    >>>
    >>> # Format nodes to PlantUML
    >>> nodes = [Requirement(id="REQ-001", title="Test")]
    >>> plantuml = formatter.format(nodes)
    >>>
    >>> # Parse PlantUML back to nodes
    >>> parsed_nodes = formatter.parse('Container("REQ-001", "Test", ...)')

The C4 formatter is independent of the Node class and works with any objects
that have the required attributes (id, type, metadata).
"""

import io
import re
from typing import Dict, Any, Optional, List, Callable, Iterable, TextIO, BinaryIO
import pyparsing as pp

PARAMETER_ORDERS = {
    "Person": ["id", "title", "description", "sprite", "tags", "link", "type"],
    "Person_Ext": ["id", "title", "description", "sprite", "tags", "link", "type"],
    "System": [
        "id",
        "title",
        "description",
        "sprite",
        "tags",
        "link",
        "type",
        "baseShape",
    ],
    "SystemDb": ["id", "title", "description", "sprite", "tags", "link", "type"],
    "SystemQueue": ["id", "title", "description", "sprite", "tags", "link", "type"],
    "System_Ext": [
        "id",
        "title",
        "description",
        "sprite",
        "tags",
        "link",
        "type",
        "baseShape",
    ],
    "SystemDb_Ext": ["id", "title", "description", "sprite", "tags", "link", "type"],
    "SystemQueue_Ext": ["id", "title", "description", "sprite", "tags", "link", "type"],
    "Boundary": ["id", "title", "type", "tags", "link", "description"],
    "Enterprise_Boundary": ["id", "title", "tags", "link", "description"],
    "System_Boundary": ["id", "title", "tags", "link", "description"],
    "Container": [
        "id",
        "title",
        "technology",
        "description",
        "sprite",
        "tags",
        "link",
        "baseShape",
    ],
    "ContainerDb": [
        "id",
        "title",
        "technology",
        "description",
        "sprite",
        "tags",
        "link",
    ],
    "ContainerQueue": [
        "id",
        "title",
        "technology",
        "description",
        "sprite",
        "tags",
        "link",
    ],
    "Container_Ext": [
        "id",
        "title",
        "technology",
        "description",
        "sprite",
        "tags",
        "link",
        "baseShape",
    ],
    "ContainerDb_Ext": [
        "id",
        "title",
        "technology",
        "description",
        "sprite",
        "tags",
        "link",
    ],
    "ContainerQueue_Ext": [
        "id",
        "title",
        "technology",
        "description",
        "sprite",
        "tags",
        "link",
    ],
    "Container_Boundary": ["id", "title", "tags", "link", "description"],
    "Component": [
        "id",
        "title",
        "technology",
        "description",
        "sprite",
        "tags",
        "link",
        "baseShape",
    ],
    "ComponentDb": [
        "id",
        "title",
        "technology",
        "description",
        "sprite",
        "tags",
        "link",
    ],
    "ComponentQueue": [
        "id",
        "title",
        "technology",
        "description",
        "sprite",
        "tags",
        "link",
    ],
    "Component_Ext": [
        "id",
        "title",
        "technology",
        "description",
        "sprite",
        "tags",
        "link",
        "baseShape",
    ],
    "ComponentDb_Ext": [
        "id",
        "title",
        "technology",
        "description",
        "sprite",
        "tags",
        "link",
    ],
    "ComponentQueue_Ext": [
        "id",
        "title",
        "technology",
        "description",
        "sprite",
        "tags",
        "link",
    ],
    "Deployment_Node": ["id", "title", "type", "description", "sprite", "tags", "link"],
    "Node": ["id", "title", "type", "description", "sprite", "tags", "link"],
    "Node_L": ["id", "title", "type", "description", "sprite", "tags", "link"],
    "Node_R": ["id", "title", "type", "description", "sprite", "tags", "link"],
}

"""
@startuml
title Nucera CS Basic Requirements

!include <tupadr3/common.puml>
!include <tupadr3/font-awesome-6/clipboard_check.puml>
!include <tupadr3/font-awesome-6/gear.puml>
!include <tupadr3/font-awesome/bug.puml>

AddElementTag("issue", $sprite="bug")
AddElementTag("requirement", $sprite="clipboard_check")
AddElementTag("feature", $sprite="gear")
AddElementTag("must", $bgColor="#741717", $borderColor="#ffffff", $borderThickness=2)
AddElementTag("could", $bgColor="#b8b8b8", $borderColor="#ffffff", $borderThickness=2)
AddElementTag("should", $bgColor="#f2c94c", $fontColor="#000000", $borderColor="#000000", $borderThickness=2)
AddElementTag("standard", $bgColor="#176174", $borderColor="#ffffff", $borderThickness=2)
 """
DEFAULT_HEADER = (
    "@startuml",
    "!pragma svginteractive true",
    "!include <C4/C4_Container.puml>",
    "!include <C4/C4_Component.puml>",
)

DEFAULT_FOOTER = ("@enduml",)

DEFAULT_TYPE_MAP: Dict[str, str] = {
    "requirement": "Container",
    "node": "Component",
    "system": "System",
    "component": "Component",
    "database": "ContainerDb",
    "grouping": "Boundary",
    "person": "Person",
    "issue": "Component",
    "feature": "Component",
}


def write_lines_binary(lines: Iterable[str], file: BinaryIO) -> None:
    """Write lines to a binary file, adding newlines.

    Args:
        lines: An iterable of strings to write
        file: The binary file object to write to
    """
    if isinstance(lines, str):
        file.write((lines + "\n").encode("utf-8"))
        return

    for line in lines:
        file.write((line + "\n").encode("utf-8"))


def is_binary_stream(file: TextIO | BinaryIO) -> bool:
    """Check if a file object is opened in binary mode.

    Args:
        file: The file object to check
    Returns:
        True if the file is opened in binary mode, False otherwise
    """
    # Check instance type first (most reliable for in-memory streams)
    if isinstance(file, (io.RawIOBase, io.BufferedIOBase, io.BytesIO)):
        return True
    if isinstance(file, (io.TextIOBase, io.TextIOWrapper, io.StringIO)):
        return False

    # Fallback to mode attribute for real file objects
    mode = getattr(file, "mode", "")
    return "b" in mode


def write_lines(lines: Iterable[str], file: TextIO | BinaryIO) -> None:
    """Write lines to a text file, adding newlines.

    Args:
        lines: An iterable of strings to write
        file: The file object to write to
    """

    # check if stream is binary
    if is_binary_stream(file):
        write_lines_binary(lines, file)
        return

    if isinstance(lines, str):
        file.write(lines)
        file.write("\n")
        return

    for line in lines:
        file.write(line)
        file.write("\n")


def encode_string(value: str) -> str:
    """Encode a string for PlantUML by escaping quotes and backslashes.

    Args:
        value: The input string to encode
    Returns:
        The encoded string with quotes and backslashes escaped
    """
    value = re.sub(r"[\n\r]+", r"\\n", value)
    value = re.sub(r'"', "<U+0022>", value)
    return value


def decode_string(value: str) -> str:
    """Decode a PlantUML-encoded string by unescaping quotes and backslashes.

    Args:
        value: The encoded string to decode

    Returns:
        The decoded string with quotes and backslashes unescaped
    """
    value = re.sub(r"\\n", "\n", value)
    value = re.sub(r"<U\+0022>", '"', value)
    return value


def get_attribute(obj, attr: str, default: Optional[Any] = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(attr, default)

    # First try to get from object attribute (property or field)
    if hasattr(obj, attr):
        try:
            value = getattr(obj, attr)
            # Don't use empty strings, prefer metadata or default
            if value is not None:
                return value
        except AttributeError:
            pass

    # Then check metadata
    metadata = get_attribute(obj, "metadata", None)
    if metadata and attr in metadata:
        return metadata[attr]

    return default


def validate_tags(tags: List[str]) -> None:
    """Validate that tags only contain alphanumeric characters, underscores, or hyphens.

    Args:
        tags: List of tag strings to validate

    Raises:
        ValueError: If any tag is invalid
    """
    for tag in tags:
        if not re.match(r"^[\w\-]+$", tag):
            raise ValueError(
                "Tags can only contain alphanumeric characters, underscores, or hyphens."
            )


def create_c4_parser():
    """Create a PlantUML C4 parser for Node representations.

    Parses PlantUML C4 syntax:
    Container("id", "label", "technology", "description", $tags="tag1+tag2", $sprite="icon")

    Also supports nested elements:
    Container("id", "label", ...) {
        Component("child_id", ...)
    }

    The positional parameters are:
    1. id - unique identifier
    2. label - display label/title
    3. technology - technology/type (optional, often same as label or type name)
    4. description - detailed description (optional)

    Additional parameters like $tags, $sprite, $link are optional.
    """

    # Define basic elements
    quoted_string = pp.QuotedString('"', escChar="\\", multiline=False)

    # C4 element types
    c4_type = pp.one_of(list(PARAMETER_ORDERS.keys()))("c4_type")

    # Parameter arguments like $tags="value"
    param_name = pp.Combine(pp.Literal("$") + pp.Word(pp.alphas))
    param_value = quoted_string
    parameter = pp.Group(param_name("name") + pp.Suppress("=") + param_value("value"))

    # Forward declaration for recursive grammar
    plantuml_element = pp.Forward()

    # PlantUML C4 format: Type("id", "label", "technology", "description", $param="value", ...)
    # All positional parameters after id and label are optional
    plantuml_expr = (
        c4_type
        + pp.Suppress("(")
        + pp.ZeroOrMore(pp.Suppress(pp.Optional(",")) + quoted_string("value"))(
            "unnamed_params"
        )
        + pp.ZeroOrMore(pp.Suppress(",") + parameter)("parameters")
        + pp.Suppress(")")
    )

    # Optional children block: { ... }
    # Each child element is already a Group, so we collect them
    children_block = (
        pp.Suppress("{")
        + pp.Group(pp.ZeroOrMore(pp.Group(plantuml_element)))("children")
        + pp.Suppress("}")
    )

    # Complete element with optional children
    plantuml_element <<= plantuml_expr + pp.Optional(children_block)

    return plantuml_element


class C4Formatter:
    """Formatter for converting between Node objects and PlantUML C4 syntax."""

    def __init__(
        self,
        type_map: Optional[Dict[str, str]] = DEFAULT_TYPE_MAP,
        node_factory: Optional[Callable[[Dict[str, Any]], Any]] = None,
        header: Iterable[str] | str = DEFAULT_HEADER,
        footer: Iterable[str] | str = DEFAULT_FOOTER,
    ):
        """Initialize the C4 formatter.

        Args:
            type_map: Dictionary mapping node type strings to C4 element types
                     e.g., {"requirement": "Container", "system": "System"}
            node_factory: Optional factory function to create nodes from dicts.
                         Should accept a dict with 'id', 'type', 'metadata' and return a Node.
                         If not provided, nodes won't be created during parsing.
        """
        self.__type_map: Dict[str, str] = type_map or {}
        self.__node_factory: Optional[Callable[[Dict[str, Any]], Any]] = node_factory
        self.__parser: pp.ParserElement = create_c4_parser()
        self.__header: List[str] = (
            list(header)
            if isinstance(header, Iterable) and not isinstance(header, (str, bytes))
            else [header]
        )
        self.__footer: List[str] = (
            list(footer)
            if isinstance(footer, Iterable) and not isinstance(footer, (str, bytes))
            else [footer]
        )

    @property
    def header(self) -> List[str]:
        """Get the header lines for PlantUML C4 diagrams."""
        return self.__header

    @property
    def footer(self) -> List[str]:
        """Get the footer lines for PlantUML C4 diagrams."""
        return self.__footer

    def _get_c4_type(self, node_type: str) -> str:
        """Get the C4 element type for a node type.

        Args:
            node_type: The node type string

        Returns:
            The C4 element type, or "Component" as default
        """
        return self.__type_map.get(node_type, "Component")

    def _format_relation(self, relation: Any) -> str:
        """Format a relation object to PlantUML C4 syntax.

        Rel(from, to, label, ?techn, ?descr, ?sprite, ?tags, ?link)
        Based on the metadata of the relation object, format as one of:
        - BiRel
        - Rel_Up
        - Rel_Down
        - Rel_Left
        - Rel_Right

        Args:
            relation: Relation object with 'source', 'destination', 'description', 'technology', 'tags'

        Returns:
            PlantUML C4 relation string
        """
        source_id = get_attribute(relation, "src")
        dest_id = get_attribute(relation, "dst")
        label = get_attribute(relation, "type", "")
        technology = get_attribute(relation, "technology", "")
        tags = get_attribute(relation, "tags", [])
        description = get_attribute(relation, "description", "")
        direction = get_attribute(relation, "direction", "")
        sprite = get_attribute(relation, "sprite", "")
        link = get_attribute(relation, "link", "")
        tooltip = get_attribute(relation, "tooltip", get_attribute(relation, "comment", None))
        if tooltip:
            link = f"{link}{{{tooltip}}}"

        c4_relation_type = "Rel"
        match direction:
            case "up":
                c4_relation_type = "Rel_Up"
            case "down":
                c4_relation_type = "Rel_Down"
            case "left":
                c4_relation_type = "Rel_Left"
            case "right":
                c4_relation_type = "Rel_Right"
            case _:
                c4_relation_type = "Rel"

        args = [source_id, dest_id, f'"{encode_string(label)}"']

        if technology:
            args.append(f"$techn={encode_string(technology)}")
        if description:
            args.append(f"$descr={encode_string(description)}")
        if tags:
            validate_tags(tags)
            args.append(f'$tags="{"+".join(tags)}"')
        if sprite:
            args.append(f'$sprite="{encode_string(sprite)}"')
        if link:
            args.append(f'$link="{encode_string(link)}"')

        return f"{c4_relation_type}({', '.join(args)})"

    def _format_node(
        self,
        node_obj: Any,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        sprite: Optional[str] = None,
        technology: Optional[str] = None,
        link: Optional[str] = None,
        type: Optional[str] = None,
        tooltip: Optional[str] = None,
    ) -> str:
        """Convert a single Node object to PlantUML C4 representation.

        Args:
            node_obj: The node object to convert
            title: Optional title override
            description: Optional description override
            tags: Optional tags override
            sprite: Optional sprite override
            technology: Optional technology override
            link: Optional link override
            type: Optional type override

        Returns:
            PlantUML C4 syntax string
        """
        c4_representation = self._get_c4_type(node_obj.type)

        if title is None:
            # Try title first, then fallback to id
            title = get_attribute(node_obj, "title", node_obj.id)

        if description is None:
            # Try description, default to empty string
            description = get_attribute(node_obj, "description", "")

        if tags is None:
            tags = get_attribute(node_obj, "tags", [])

        if sprite is None:
            sprite = get_attribute(node_obj, "sprite", "")

        if link is None:
            link = get_attribute(node_obj, "link", "")

        if technology is None:
            technology = get_attribute(node_obj, "technology", node_obj.type)

            if tooltip is None:
                tooltip = get_attribute(
                    node_obj, "tooltip", get_attribute(node_obj, "comment", None)
                )
                if tooltip:
                    link = f"{link}{{{tooltip}}}"

        # Make a copy of tags to avoid modifying the original
        tags = list(tags) if tags else []
        if node_obj.type not in tags:
            tags.append(node_obj.type)

        # Build args list matching PlantUML C4 format
        args = [f'"{node_obj.id}"', f'"{encode_string(title)}"']

        # Add optional parameters
        if tags and "tags" in PARAMETER_ORDERS[c4_representation]:
            validate_tags(tags)
            args.append(f"$tags=\"{'+'.join(encode_string(tag) for tag in tags)}\"")
        if sprite and "sprite" in PARAMETER_ORDERS[c4_representation]:
            args.append(f'$sprite="{encode_string(sprite)}"')
        if link and "link" in PARAMETER_ORDERS[c4_representation]:
            args.append(f'$link="{encode_string(link)}"')
        if type and "type" in PARAMETER_ORDERS[c4_representation]:
            args.append(f'$type="{encode_string(type)}"')
        if technology and "technology" in PARAMETER_ORDERS[c4_representation]:
            args.append(f'$techn="{encode_string(technology)}"')
        if description and "description" in PARAMETER_ORDERS[c4_representation]:
            args.append(f'$descr="{encode_string(description)}"')

        return f"{c4_representation}({', '.join(args)})"

    def format(
        self,
        nodes: Iterable[Any] | Any,
        include_header: bool = True,
        include_footer: bool = True,
    ) -> str:
        """Format a list of nodes to PlantUML C4 syntax.

        Supports nested nodes with children.

        Args:
            nodes: List of node objects to format
            include_header: Whether to include the PlantUML header lines
            include_footer: Whether to include the PlantUML footer lines

        Returns:
            Complete PlantUML C4 syntax string with all nodes and their children
        """
        if isinstance(nodes, (dict, str, bytes)) or not isinstance(nodes, Iterable):
            nodes = [nodes]

        lines = []

        if include_header:
            lines.extend(self.__header)

        lines.extend(self._format_nodes(nodes))

        if include_footer:
            lines.extend(self.__footer)

        return "\n".join(lines)

    def _format_relations(self, relations: Optional[Iterable[Any]]) -> Iterable[str]:
        """Format a list of relations to PlantUML C4 syntax.

        Args:
            relations: Iterable of relation objects to format

        Yields:
            Formatted PlantUML C4 lines for each relation
        """
        if relations is None:
            return

        for relation in relations:
            yield self._format_relation(relation)

    def _format_nodes(
        self, nodes: Iterable[Any], indent: int = 0, skip_root: bool = False
    ) -> Iterable[str]:
        """Recursively format nodes and their children to PlantUML C4 syntax.
        Args:
            nodes: Iterable of node objects to format
            indent: Current indentation level for nested nodes
            skip_root: Whether to skip formatting the root node
        Yields:
            Formatted PlantUML C4 lines for each node and its children
        """
        nodes = list(nodes) if isinstance(nodes, Iterable) else [nodes]

        # handle root graph which is not a C4 element and just translated to a title
        if not skip_root and indent == 0 and len(nodes) == 1:
            nodes = list(nodes)
            root_node = nodes[0]
            type = get_attribute(root_node, "type", "root")
            if type == "root":
                title = get_attribute(root_node, "title", "Architecture Diagram")
                yield f"title {title}"
                nodes = getattr(root_node, "children", [])
                yield from self._format_nodes(nodes, indent, skip_root=True)
                relations = getattr(root_node, "relations", None)
                yield from self._format_relations(relations)
                return

        indent_str = "  " * indent
        for node in nodes:
            # Format the current node
            line = self._format_node(node)

            # Check if node has children
            children = getattr(node, "children", None)
            children = list(children) if children else []

            if children:
                # Node has children - format as boundary with nested elements
                yield (f"{indent_str}{line} {{")
                # Recursively format children
                yield from self._format_nodes(children, indent + 1)
                yield (f"{indent_str}}}")
            else:
                yield (f"{indent_str}{line}")

    def parse(self, plantuml_str: str) -> Any:
        """Parse a PlantUML C4 string into a Node object.

        Args:
            plantuml_str: PlantUML C4 element string

        Returns:
            Node object created via the node_factory, or dict if no factory provided

        Raises:
            ValueError: If the PlantUML string is invalid
        """
        result_dict = self._parse_to_dict(plantuml_str)

        if self.__node_factory is None:
            return result_dict

        return self.__node_factory(result_dict)

    def parse_parameter(self, param_name, param_value) -> Any:
        """Parse a single parameter value based on its name.

        Args:
            param_name: The name of the parameter (e.g., "tags", "sprite")
            param_value: The string value of the parameter

        Returns:
            Parsed value, which may be a list or a single string
        """
        if param_name == "tags":
            return param_value.split("+")
        return param_value

    def _parse_result_to_dict(self, result) -> Dict[str, Any]:
        """Parse a pyparsing result object into a dictionary.

        This is a helper method for parsing both parent and child elements.

        Args:
            result: pyparsing ParseResults object

        Returns:
            Dictionary with node data
        """
        result_dict: Dict[str, Any] = {}

        if hasattr(result, "unnamed_params"):
            unnamed_params = result.unnamed_params.as_list()
            param_order = PARAMETER_ORDERS.get(result.c4_type, [])
            for i, param_name in enumerate(param_order[0 : len(unnamed_params)]):
                value = decode_string(unnamed_params[i])
                result_dict[param_name] = self.parse_parameter(param_name, value)

        # Build metadata
        if hasattr(result, "parameters"):
            for param in result.parameters:
                param_name = param.name[1:]  # Remove the $ prefix
                match param_name:
                    case "descr":
                        param_name = "description"
                    case "techn":
                        param_name = "technology"
                param_value = decode_string(param.value)

                result_dict[param_name] = self.parse_parameter(param_name, param_value)

        # Determine node type from C4 type or tags
        node_type = "node"  # default

        # First check if C4 type maps to a known node type
        c4_type = result.c4_type
        for ntype, ctype in self.__type_map.items():
            if ctype == c4_type:
                node_type = ntype
                break

        # Then check if any tag matches a node type in the type map
        for tag in result_dict.get("tags", []):
            if tag in self.__type_map:
                node_type = tag
                break

        result_dict["type"] = node_type

        # Parse children if present
        if hasattr(result, "children") and result.children:
            children_list = []
            for child_result in result.children:
                # Recursively parse each child
                child_dict = self._parse_result_to_dict(child_result)
                children_list.append(child_dict)
            result_dict["children"] = children_list

        return result_dict

    def _parse_to_dict(self, plantuml_str: str) -> Dict[str, Any]:
        """Parse a PlantUML C4 string into a dictionary.

        Args:
            plantuml_str: PlantUML C4 element string (can include header/footer lines which will be ignored)

        Returns:
            Dictionary with 'id', 'type', and 'metadata' keys

        Raises:
            ValueError: If the PlantUML string is invalid
        """
        # Filter out header/footer lines that are not C4 elements
        cleaned_str = self._clean_plantuml(plantuml_str)

        try:
            result = self.__parser.parseString(cleaned_str.strip(), parseAll=True)
        except pp.ParseException as e:
            raise ValueError(f"Invalid PlantUML syntax: {cleaned_str}. Error: {str(e)}")

        return self._parse_result_to_dict(result)

    def _clean_plantuml(self, plantuml_str: str) -> str:
        """Remove header and footer lines from PlantUML string.

        Removes lines starting with:
        - @startuml, @enduml
        - !include, !pragma, !define, !theme
        - title, caption, legend, header, footer
        - AddElementTag, AddRelTag, LAYOUT_*, SHOW_*, HIDE_*
        - skinparam, scale
        - Comments (')

        Args:
            plantuml_str: Raw PlantUML string

        Returns:
            Cleaned PlantUML string with only C4 element definitions
        """
        lines = plantuml_str.split("\n")
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                continue

            # Skip header/footer directives
            if any(
                stripped.startswith(prefix)
                for prefix in [
                    "@startuml",
                    "@enduml",
                    "!include",
                    "!pragma",
                    "!define",
                    "!theme",
                    "title ",
                    "caption ",
                    "legend",
                    "header ",
                    "footer ",
                    "AddElementTag",
                    "AddRelTag",
                    "UpdateElementStyle",
                    "UpdateRelStyle",
                    "LAYOUT_",
                    "SHOW_",
                    "HIDE_",
                    "skinparam",
                    "scale",
                    "'",  # Comments
                ]
            ):
                continue

            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def load(self, file: TextIO | BinaryIO) -> Any:
        """Load and parse PlantUML C4 data from a file object.

        Args:
            file: File object opened for reading (text mode or binary mode)

        Returns:
            Node object(s) if node_factory is configured, otherwise raw data
        """
        if is_binary_stream(file):
            content = file.read().decode("utf-8")
        else:
            content = file.read()
        return self.parse(content)

    def dump(self, nodes: Any | Iterable[Any], file: TextIO | BinaryIO) -> None:
        """Dump PlantUML C4 data to a file object.

        Args:
            data: Data to serialize (dict or list of dicts)
            file: File object opened for writing (text mode or binary mode)
        """
        if isinstance(nodes, (str, bytes, dict)) or not isinstance(nodes, Iterable):
            nodes = [nodes]

        write_lines(self.__header, file)
        write_lines(self._format_nodes(nodes), file)
        write_lines(self.__footer, file)
