"""Unit tests for C4Formatter class."""

import unittest
import sys
import os

from arch_tool.grouping import Grouping

# Add parent directory to path to import arch_tool
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from arch_tool import Node, Requirement, C4Formatter, Relation, Graph
from arch_tool.formatters.c4_formatter import decode_string, encode_string


class EncodeDecodeStringTests(unittest.TestCase):

    def test_encode_string_with_quotes(self):
        """Test encoding a string with quotes to PlantUML format."""
        text = 'This is a "test" string.'
        encoded = encode_string(text)
        self.assertEqual(encoded, "This is a <U+0022>test<U+0022> string.")

    def test_encode_string_with_newlines(self):
        """Test encoding a string with newlines to PlantUML format."""
        text = "This is a test string.\nWith a newline."
        encoded = encode_string(text)
        self.assertEqual(encoded, "This is a test string.\\nWith a newline.")

    def test_encode_plain_string(self):
        """Test encoding a string to PlantUML format."""
        text = "This is a test string."
        encoded = encode_string(text)
        self.assertEqual(encoded, "This is a test string.")

    def test_decode_string(self):
        """Test decoding a PlantUML string back to normal format."""
        encoded = "<U+0022>This is a test string.<U+0022>"
        decoded = decode_string(encoded)
        self.assertEqual(decoded, '"This is a test string."')


class TestC4PlantUMLGeneration(unittest.TestCase):
    def setUp(self):
        self.formatter = C4Formatter(
            header="@startuml\n'''\nThis is a custom header for PlantUML diagrams.\n'''",
            type_map={
                "requirement": "Container",
                "node": "Component",
                "container": "Component",
                "grouping": "Boundary",
            },
            node_factory=Node.from_dict,
        )
        return super().setUp()

    def test_grouping_is_encoded_to_boundary_with_valid_boundary_parameters(self):
        """Test that a grouping node is encoded to a Boundary in PlantUML."""
        grouping = Grouping(
            id="G1",
            type="grouping",
            title="My Grouping",
            tags=["grouping"],
        )

        plantuml = self.formatter.format(
            grouping, include_header=False, include_footer=False
        )

        expected = 'Boundary("G1", "My Grouping", $tags="grouping")'
        self.assertIn(plantuml, expected)

    def test_writing_to_a_file_with_wb_encoding_preserves_newlines(self):
        """Test that writing to a binary file preserves newlines correctly."""
        import io

        graph = Graph(
            id="root",
            type="root",
            metadata={},
            children=[
                Requirement(
                    id="R1",
                    title="Requirement 1",
                    description="This is line 1.\nThis is line 2.",
                )
            ],
        )

        # Use BytesIO to simulate a binary file
        with io.BytesIO() as binary_file:
            self.formatter.dump(graph, binary_file)
            binary_file.seek(0)
            content = binary_file.read().decode('utf-8')

            # Check that newlines are represented as \n in the output
            self.assertIn("This is line 1.\\nThis is line 2.", content)

    def test_writing_to_a_file_with_text_encoding_encodes_newlines_correctly(self):
        """Test that writing to a text file encodes newlines correctly."""
        import io

        graph = Graph(
            id="root",
            type="root",
            metadata={},
            children=[
                Requirement(
                    id="R1",
                    title="Requirement 1",
                    description="This is line 1.\nThis is line 2.",
                )
            ],
        )

        # Use StringIO to simulate a text file
        with io.StringIO() as text_file:
            self.formatter.dump(graph, text_file)
            text_file.seek(0)
            content = text_file.read()

            # Check that newlines are represented as \n in the output
            self.assertIn("This is line 1.\\nThis is line 2.", content)

    def test_format_relation(self):
        """Test formatting a relation to PlantUML C4 syntax."""
        relation = Relation(
            src="C101.1",
            dst="C101.5",
            type="depends on",
            comment="C101.1 depends on C101.5",
            tags=["dependency"],
        )
        plantuml_relation = self.formatter._format_relation(relation)
        expected = [
            'Rel("C101.1", "C101.5", "depends on", $tags="dependency")',
            'Rel(C101.1, C101.5, "depends on", $tags="dependency")',
        ]
        self.assertIn(plantuml_relation, expected)

    def test_graph_root_formatting_to_title(self):
        """Test that Graph root node is formatted with title."""
        graph = Graph(
            id="root",
            type="root",
            metadata={"title": "System Architecture"},
        )

        plantuml = self.formatter.format(
            graph, include_header=True, include_footer=True
        )

        self.assertIn("@startuml", plantuml)
        self.assertIn("title System Architecture", plantuml)
        self.assertIn("@enduml", plantuml)

    def test_single_string_header_is_written_as_single_line_by_dump(self):
        """Test that single string header is written as a single line by dump()."""
        graph = Graph(id="root", type="root")

        from io import StringIO

        stream = StringIO()
        self.formatter.dump(graph, stream)

        header = "This is a custom header for PlantUML diagrams."

        stream.seek(0)
        output = stream.read()
        self.assertIn(header + "\n", output)


class TestPlantUMLParsing(unittest.TestCase):
    """Test cases for PlantUML parsing with C4Formatter."""

    def setUp(self):
        """Set up C4Formatter for each test."""
        self.formatter = C4Formatter(
            type_map={
                "requirement": "Container",
                "node": "Component",
                "container": "Component",
            },
            node_factory=Node.from_dict,
        )

    def test_from_plantuml_basic_container(self):
        """Test parsing basic Container with MUST priority."""
        plantuml = 'Container("C101.1", "Modular Product Definition", "C101.1", "The CPQ system must offer...", $tags="must+requirement")'
        node = self.formatter.parse(plantuml)

        self.assertIsInstance(node, Requirement)
        self.assertEqual(node.id, "C101.1")
        self.assertEqual(node.title, "Modular Product Definition")
        self.assertEqual(node.description, "The CPQ system must offer...")
        self.assertSetEqual(set(node.tags), {"must", "requirement"})

    def test_from_plantuml_should_priority(self):
        """Test parsing Container with SHOULD priority."""
        plantuml = 'Container("C101.2", "Multi-Level BOM", "C101.2", "The system should support...", $tags="should+requirement")'
        node = self.formatter.parse(plantuml)

        self.assertIsInstance(node, Requirement)
        self.assertEqual(node.id, "C101.2")
        self.assertSetEqual(set(node.tags), {"should", "requirement"})

    def test_from_plantuml_could_priority(self):
        """Test parsing Container with COULD priority."""
        plantuml = 'Container("C101.3", "Feature X", "C101.3", "The system could include...", $tags="could+requirement")'
        node = self.formatter.parse(plantuml)

        self.assertEqual(node.id, "C101.3")
        self.assertSetEqual(set(node.tags), {"could", "requirement"})

    def test_from_plantuml_with_escaped_quotes(self):
        """Test parsing PlantUML with escaped quotes in description."""
        plantuml = r'Container("C102.1", "Title", "C102.1", "Description with \"quotes\"", $tags="must+requirement")'
        node = self.formatter.parse(plantuml)

        self.assertEqual(node.id, "C102.1")
        self.assertIn("quotes", node.description)

    def test_from_plantuml_minimal(self):
        """Test parsing minimal Container (ID only)."""
        plantuml = 'Component("C101.1", "", "C101.1", "")'
        node = self.formatter.parse(plantuml)

        self.assertEqual(node.id, "C101.1")
        self.assertEqual(node.metadata.get("title", ""), "")
        self.assertEqual(node.metadata.get("description", ""), "")

    def test_from_plantuml_with_sprite(self):
        """Test parsing Container with sprite parameter."""
        plantuml = 'Container("C101.1", "Title", "C101.1", "Description", $tags="must+requirement", $sprite="database")'
        node = self.formatter.parse(plantuml)

        self.assertEqual(node.id, "C101.1")
        self.assertEqual(node.metadata["sprite"], "database")
        self.assertSetEqual(set(node.tags), {"must", "requirement"})

    def test_from_plantuml_with_link(self):
        """Test parsing Container with link parameter."""
        plantuml = 'Container("C101.1", "Title", "C101.1", "Description", $tags="must+requirement", $link="https://example.com")'
        node = self.formatter.parse(plantuml)

        self.assertEqual(node.id, "C101.1")
        self.assertEqual(node.metadata["link"], "https://example.com")

    def test_from_plantuml_invalid_syntax(self):
        """Test that invalid PlantUML raises ValueError."""
        invalid_plantuml = "Not a valid PlantUML string"
        with self.assertRaises(ValueError) as context:
            self.formatter.parse(invalid_plantuml)
        self.assertIn("Invalid PlantUML syntax", str(context.exception))

    def test_from_plantuml_missing_arguments(self):
        """Test that PlantUML with missing arguments raises ValueError."""
        invalid_plantuml = "Container()"
        with self.assertRaises(ValueError) as context:
            self.formatter.parse(invalid_plantuml)
        # The error message from pyparsing will mention the parsing error
        self.assertTrue(
            "Invalid PlantUML syntax" in str(context.exception)
            or "Data must contain 'id' and 'type' keys." in str(context.exception)
        )

    def test_from_plantuml_invalid_id(self):
        """Test that PlantUML with invalid ID raises ValueError."""
        invalid_plantuml = (
            'Container("invalid id!", "Title", "invalid id!", "Description")'
        )
        with self.assertRaises(ValueError) as context:
            self.formatter.parse(invalid_plantuml)
        # The error should mention the ID validation issue
        self.assertTrue(
            "Invalid ID" in str(context.exception)
            or "ID must match" in str(context.exception)
        )

    def test_from_plantuml_roundtrip(self):
        """Test that node can be converted to PlantUML and back."""
        # Create a requirement
        original = Requirement(
            id="C101.5",
            title="Target Cost Definition",
            description="The system must define target costs",
            tags=["must", "requirement"],
        )

        # Convert to PlantUML
        plantuml = self.formatter.format(
            original, include_footer=False, include_header=False
        )

        # Parse back
        restored = self.formatter.parse(plantuml)

        # Verify
        self.assertIsInstance(restored, Requirement)
        self.assertEqual(original.id, restored.id)
        self.assertEqual(original.title, restored.title)
        self.assertEqual(original.description, restored.description)
        self.assertSetEqual(set(original.tags), set(restored.tags))

    def test_from_plantuml_real_example_c101_1(self):
        """Test parsing real example from requirements.puml (C101.1)."""
        plantuml = 'Container("C101.1", "Modular Product Definition", "C101.1", "The CPQ system must offer a modular product definition capability that allows hierarchical structuring of product configurations.", $tags="must+requirement")'
        node = self.formatter.parse(plantuml)

        self.assertIsInstance(node, Requirement)
        self.assertEqual(node.id, "C101.1")
        self.assertEqual(node.title, "Modular Product Definition")
        self.assertIn("hierarchical structuring", node.description)
        self.assertSetEqual(set(node.tags), {"must", "requirement"})

    def test_from_plantuml_real_example_c101_5(self):
        """Test parsing real example from requirements.puml (C101.5)."""
        plantuml = 'Container("C101.5", "Target Cost Definition", "C101.5", "The system must allow defining target costs for products and components.", $tags="must+requirement")'
        node = self.formatter.parse(plantuml)

        self.assertIsInstance(node, Requirement)
        self.assertEqual(node.id, "C101.5")
        self.assertEqual(node.title, "Target Cost Definition")
        self.assertIn("target costs", node.description)
        self.assertSetEqual(set(node.tags), {"must", "requirement"})

    def test_format_relation(self):
        """Test formatting a relation to PlantUML C4 syntax."""
        from arch_tool.relation import Relation

        relation = Relation(
            src="C101.1",
            dst="C101.5",
            type="depends on",
            comment="C101.1 depends on C101.5",
            tags=["dependency"],
        )

        plantuml_relation = self.formatter._format_relation(relation)

        expected = [
            'Rel("C101.1", "C101.5", "depends on", $tags="dependency")',
            'Rel(C101.1, C101.5, "depends on", $tags="dependency")',
        ]
        self.assertIn(plantuml_relation, expected)

    def test_from_plantuml_multiple_tags(self):
        """Test parsing Container with multiple tags."""
        plantuml = 'Container("F101.1", "Title", "F101.1", "Description", $tags="must+requirement+feature+costing")'
        node = self.formatter.parse(plantuml)

        self.assertEqual(node.id, "F101.1")
        self.assertSetEqual(set(node.tags), {"must", "requirement", "feature", "costing"})

    def test_from_plantuml_with_children(self):
        """Test parsing Container with children (not directly supported, but check metadata)."""
        plantuml = """Container("F101.1", "Title", "F101.1", "Description", $tags="must+requirement+feature+costing")  {
    Component("F101.1.1", "Child Component 1", "F101.1.1", "First child component")
}"""
        node = self.formatter.parse(plantuml)

        self.assertEqual(node.id, "F101.1")
        self.assertLessEqual(len(node.children), 1)

    def test_roundtrip_with_children(self):
        """Test roundtrip serialization with children."""
        parent = Requirement(
            id="F200.1",
            title="Parent Requirement",
            description="This is the parent requirement.",
            metadata={"tags": ["must", "requirement"]},
            children=[
                Requirement(
                    id="F200.1.1",
                    title="Child Requirement 1",
                    description="First child requirement.",
                ),
                Requirement(
                    id="F200.1.2",
                    title="Child Requirement 2",
                    description="Second child requirement.",
                ),
            ],
        )

        # Convert to PlantUML
        plantuml = self.formatter.format(parent)

        # Parse back
        restored = self.formatter.parse(plantuml)

        # Verify
        self.assertEqual(parent.id, restored.id)
        self.assertEqual(parent.title, restored.title)
        self.assertEqual(parent.description, restored.description)
        self.assertEqual(len(parent.children), len(restored.children))


if __name__ == "__main__":
    unittest.main(verbosity=2)
