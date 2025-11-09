"""Unit tests for Node class."""

import unittest
import sys
import os

# Add parent directory to path to import arch_tool
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from arch_tool import Node


class TestNode(unittest.TestCase):
    """Test cases for the Node class."""

    def test_node_creation(self):
        """Test basic node creation."""
        node = Node(id="node123", type="node")
        self.assertEqual(node.id, "node123")
        self.assertEqual(node.type, "node")
        self.assertEqual(node.metadata, {})

    def test_node_with_metadata(self):
        """Test node creation with metadata."""
        metadata = {"key1": "value1", "key2": 42}
        node = Node(id="node456", type="custom", metadata=metadata)
        self.assertEqual(node.id, "node456")
        self.assertEqual(node.type, "custom")
        self.assertEqual(node.metadata, metadata)

    def test_node_metadata_default_empty_dict(self):
        """Test that metadata defaults to empty dict."""
        node = Node(id="test")
        self.assertIsInstance(node.metadata, dict)
        self.assertEqual(len(node.metadata), 0)

    def test_node_id_immutable(self):
        """Test that node id cannot be changed."""
        node = Node(id="immutable_id")
        with self.assertRaises(AttributeError):
            node.id = "new_id"

    def test_node_type_immutable(self):
        """Test that node type cannot be changed."""
        node = Node(id="test", type="original")
        with self.assertRaises(AttributeError):
            node.type = "modified"

    def test_node_metadata_mutable(self):
        """Test that metadata can be modified."""
        node = Node(id="test")
        node.metadata["new_key"] = "new_value"
        self.assertEqual(node.metadata["new_key"], "new_value")

    def test_to_dict_converts_generators_to_list(self):
        """Test that to_dict converts generator properties to lists."""
        class TestNodeWithGenerator(Node):
            @property
            def tags(self):
                yield "tag1"
                yield "tag2"

        node = TestNodeWithGenerator(id="gen_test", type="node")
        node_dict = node.to_dict()
        self.assertIn("tags", node_dict)
        self.assertIsInstance(node_dict["tags"], list)
        self.assertEqual(node_dict["tags"], ["tag1", "tag2"])
        
    def test_node_to_dict(self):
        """Test node serialization to dictionary."""
        metadata = {"priority": "MUST", "title": "Test"}
        node = Node(id="test123", type="node", metadata=metadata)
        node_dict = node.to_dict()

        self.assertIn("id", node_dict)
        self.assertIn("type", node_dict)
        self.assertIn("metadata", node_dict)
        self.assertEqual(node_dict["id"], "test123")
        self.assertEqual(node_dict["type"], "node")
        self.assertEqual(node_dict["metadata"], metadata)

    def test_node_from_dict(self):
        """Test node deserialization from dictionary."""
        data = {"id": "node789", "type": "node", "metadata": {"key": "value"}}
        node = Node.from_dict(data)
        self.assertEqual(node.id, "node789")
        self.assertEqual(node.type, "node")
        self.assertEqual(node.metadata, {"key": "value"})

    def test_node_from_dict_missing_id(self):
        """Test that from_dict raises error when id is missing."""
        data = {"type": "node"}
        with self.assertRaises(ValueError) as context:
            Node.from_dict(data)
        self.assertIn("id", str(context.exception))

    def test_node_from_dict_missing_type(self):
        """Test that from_dict raises error when type is missing."""
        data = {"id": "test"}
        with self.assertRaises(ValueError) as context:
            Node.from_dict(data)
        self.assertIn("type", str(context.exception))

    def test_node_from_dict_unknown_type(self):
        """Test that from_dict raises error for unknown node type."""
        data = {"id": "test", "type": "unknown_type_xyz"}
        with self.assertRaises(ValueError) as context:
            Node.from_dict(data)
        self.assertIn("Unknown node type", str(context.exception))

    def test_node_from_dict_without_metadata(self):
        """Test that from_dict works without metadata field."""
        data = {"id": "test", "type": "node"}
        node = Node.from_dict(data)
        self.assertEqual(node.metadata, {})

    def test_node_repr(self):
        """Test node string representation."""
        node = Node(id="repr_test", type="custom_type")
        repr_str = repr(node)
        self.assertIn("repr_test", repr_str)
        self.assertIn("custom_type", repr_str)

    def test_node_register_type(self):
        """Test registering a new node type."""

        class CustomNode(Node):
            pass

        Node.register_type(CustomNode, "custom")
        data = {"id": "custom1", "type": "custom"}
        node = Node.from_dict(data)
        self.assertIsInstance(node, CustomNode)

    def test_node_roundtrip_serialization(self):
        """Test that node can be serialized and deserialized."""
        original = Node(
            id="roundtrip_test", type="node", metadata={"key1": "value1", "key2": 123}
        )

        # Serialize
        data = original.to_dict()

        # Deserialize
        restored = Node.from_dict(data)

        # Compare
        self.assertEqual(original.id, restored.id)
        self.assertEqual(original.type, restored.type)
        self.assertEqual(original.metadata, restored.metadata)


class TestNodeTypeRegistry(unittest.TestCase):
    """Test cases for node type registration."""

    def test_node_type_registered(self):
        """Test that 'node' type is registered."""
        data = {"id": "test", "type": "node"}
        node = Node.from_dict(data)
        self.assertIsInstance(node, Node)

    def test_requirement_type_registered(self):
        """Test that 'requirement' type is registered."""
        from arch_tool import Requirement

        data = {
            "id": "test",
            "type": "requirement",
            "title": "foo",
            "description": "bar",
        }
        node = Node.from_dict(data)
        self.assertIsInstance(node, Requirement)

    def test_multiple_type_registrations(self):
        """Test registering multiple custom types."""

        class TypeA(Node):
            pass

        class TypeB(Node):
            pass

        Node.register_type(TypeA, "type_a")
        Node.register_type(TypeB, "type_b")

        node_a = Node.from_dict({"id": "a1", "type": "type_a"})
        node_b = Node.from_dict({"id": "b1", "type": "type_b"})

        self.assertIsInstance(node_a, TypeA)
        self.assertIsInstance(node_b, TypeB)


if __name__ == "__main__":
    unittest.main(verbosity=2)
