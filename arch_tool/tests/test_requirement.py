"""Unit tests for Requirement class."""

import unittest
import sys
import os

# Add parent directory to path to import arch_tool
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from arch_tool import Node, Requirement


class TestRequirement(unittest.TestCase):
    """Test cases for the Requirement class."""

    def test_requirement_creation(self):
        """Test basic requirement creation."""
        req = Requirement(id="REQ-001", title="Test Requirement")
        self.assertEqual(req.id, "REQ-001")
        self.assertEqual(req.type, "requirement")
        self.assertEqual(req.metadata, {})

    def test_type_is_added_to_tags(self):
        """Test that the requirement type is added to tags."""
        req = Requirement(id="REQ-001", title="Test Requirement", tags=["important"])
        self.assertIn("important", req.tags)
        self.assertIn("requirement", req.tags)

    def test_priority_is_added_to_tags(self):
        """Test that the priority is added to tags."""
        req = Requirement(
            id="REQ-001",
            title="Test Requirement",
            priority="MUST",
        )
        self.assertIn("must", req.tags)

    def test_requirement_can_set_title(self):
        """Test that requirement can set title."""
        req = Requirement(id="REQ-001", title="Test Requirement")
        req.title = "New Title"
        self.assertEqual(req.title, "New Title")

    def test_requirement_with_metadata(self):
        """Test requirement creation with metadata."""
        metadata = {
            "title": "Test Requirement",
            "priority": "MUST",
            "description": "This is a test requirement",
        }
        req = Requirement(id="REQ-002", title="Test Requirement", metadata=metadata)
        self.assertEqual(req.id, "REQ-002")
        self.assertEqual(req.type, "requirement")
        self.assertEqual(req.metadata, metadata)

    def test_requirement_default_type(self):
        """Test that requirement has default type 'requirement'."""
        req = Requirement(id="REQ-003", title="Another Requirement")
        self.assertEqual(req.type, "requirement")

    def test_requirement_custom_type(self):
        """Test requirement with custom type."""
        req = Requirement(
            id="REQ-004", title="Custom Requirement", type="custom_requirement"
        )
        self.assertEqual(req.type, "custom_requirement")

    def test_requirement_is_node(self):
        """Test that Requirement is a subclass of Node."""
        req = Requirement(id="REQ-005", title="Some Requirement")
        self.assertIsInstance(req, Node)

    def test_requirement_to_dict(self):
        """Test requirement serialization."""
        metadata = {"priority": "SHOULD", "title": "Test"}
        req = Requirement(
            id="C101.1",
            title="Test Requirement",
            description="This is a test requirement",
            metadata=metadata,
        )
        req_dict = req.to_dict()

        self.assertEqual(req_dict["id"], "C101.1")
        self.assertEqual(req_dict["type"], "requirement")
        self.assertEqual(req_dict["metadata"], metadata)

    def test_requirement_from_dict(self):
        """Test requirement deserialization."""
        data = {
            "id": "F101.1",
            "type": "requirement",
            "title": "Cost Calculation",
            "metadata": {"title": "Cost Calculation", "priority": "MUST"},
        }
        req = Node.from_dict(data)
        self.assertIsInstance(req, Requirement)
        self.assertEqual(req.id, "F101.1")
        self.assertEqual(req.metadata["priority"], "MUST")

    def test_requirement_needs_title(self):
        """Test that requirement creation without title raises error."""
        data = {
            "id": "F101.1",
            "type": "requirement",
            "metadata": {"priority": "MUST"},  # No title in metadata either
        }
        with self.assertRaises(TypeError) as context:
            Node.from_dict(data)
        self.assertIn(
            "missing 1 required positional argument: 'title'",
            str(context.exception),
        )

    def test_requirement_needs_id(self):
        """Test that requirement creation without id raises error."""
        data = {
            "type": "requirement",
            "title": "Cost Calculation",
            "metadata": {"title": "Cost Calculation", "priority": "MUST"},
        }
        with self.assertRaises(ValueError) as context:
            Node.from_dict(data)
        self.assertIn("id", str(context.exception))

    def test_requirement_roundtrip(self):
        """Test requirement serialization roundtrip."""
        original = Requirement(
            id="T201.1",
            title="Cost Report Traceability",
            metadata={
                "priority": "SHOULD",
                "description": "Each cost report shall be traceable",
            },
        )

        # Serialize
        data = original.to_dict()

        # Deserialize
        restored = Node.from_dict(data)

        # Verify
        self.assertIsInstance(restored, Requirement)
        self.assertEqual(original.id, restored.id)
        self.assertEqual(original.type, restored.type)
        self.assertEqual(original.metadata, restored.metadata)

    def test_requirement_metadata_modification(self):
        """Test that requirement metadata can be modified."""
        req = Requirement(
            id="REQ-006", title="Test Requirement", metadata={"priority": "COULD"}
        )
        req.metadata["priority"] = "MUST"
        req.metadata["new_field"] = "new_value"

        self.assertEqual(req.metadata["priority"], "MUST")
        self.assertEqual(req.metadata["new_field"], "new_value")


if __name__ == "__main__":
    unittest.main(verbosity=2)
