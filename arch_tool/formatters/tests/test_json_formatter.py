"""Unit tests for JSONFormatter class."""

import unittest
import sys
import os
import json
import tempfile

# Add parent directory to path to import arch_tool
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from arch_tool import Node, Requirement, JSONFormatter


class TestJSONFormatter(unittest.TestCase):
    """Test cases for the JSONFormatter class."""

    def setUp(self):
        """Set up JSONFormatter for each test."""
        self.formatter = JSONFormatter(node_factory=Node.from_dict)

    def test_format_dict(self):
        """Test formatting a single dictionary."""
        data = {"id": "test1", "type": "node", "metadata": {"key": "value"}}
        result = self.formatter.format(data)
        
        self.assertIsInstance(result, str)
        parsed = json.loads(result)
        self.assertEqual(parsed["id"], "test1")
        self.assertEqual(parsed["type"], "node")

    def test_format_list(self):
        """Test formatting a list of dictionaries."""
        data = [
            {"id": "test1", "type": "node"},
            {"id": "test2", "type": "node"}
        ]
        result = self.formatter.format(data)
        
        self.assertIsInstance(result, str)
        parsed = json.loads(result)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["id"], "test1")

    def test_parse_dict(self):
        """Test parsing a JSON string to a single node."""
        json_str = '{"id": "test1", "type": "node", "metadata": {"key": "value"}}'
        node = self.formatter.parse(json_str)
        
        self.assertIsInstance(node, Node)
        self.assertEqual(node.id, "test1")
        self.assertEqual(node.type, "node")
        self.assertEqual(node.metadata["key"], "value")

    def test_parse_list(self):
        """Test parsing a JSON string to a list of nodes."""
        json_str = '[{"id": "test1", "type": "node"}, {"id": "test2", "type": "node"}]'
        nodes = self.formatter.parse(json_str)
        
        self.assertIsInstance(nodes, list)
        self.assertEqual(len(nodes), 2)
        self.assertIsInstance(nodes[0], Node)
        self.assertEqual(nodes[0].id, "test1")
        self.assertEqual(nodes[1].id, "test2")

    def test_parse_without_factory(self):
        """Test parsing without a node factory returns raw data."""
        formatter = JSONFormatter(node_factory=None)
        json_str = '{"id": "test1", "type": "node"}'
        result = formatter.parse(json_str)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["id"], "test1")

    def test_load_from_file_dict(self):
        """Test loading a single node from a file."""
        data = {"id": "test1", "type": "node", "metadata": {"key": "value"}}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(data, f)
            temp_file = f.name
        
        try:
            with open(temp_file, 'r') as f:
                node = self.formatter.load(f)
            
            self.assertIsInstance(node, Node)
            self.assertEqual(node.id, "test1")
            self.assertEqual(node.metadata["key"], "value")
        finally:
            os.unlink(temp_file)

    def test_load_from_file_list(self):
        """Test loading multiple nodes from a file."""
        data = [
            {"id": "test1", "type": "node"},
            {"id": "test2", "type": "requirement", "title": "Test", "description": "Desc"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(data, f)
            temp_file = f.name
        
        try:
            with open(temp_file, 'r') as f:
                nodes = self.formatter.load(f)
            
            self.assertIsInstance(nodes, list)
            self.assertEqual(len(nodes), 2)
            self.assertIsInstance(nodes[0], Node)
            self.assertIsInstance(nodes[1], Requirement)
            self.assertEqual(nodes[0].id, "test1")
            self.assertEqual(nodes[1].id, "test2")
        finally:
            os.unlink(temp_file)

    def test_load_without_factory(self):
        """Test loading from file without factory returns raw data."""
        formatter = JSONFormatter(node_factory=None)
        data = {"id": "test1", "type": "node"}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(data, f)
            temp_file = f.name
        
        try:
            with open(temp_file, 'r') as f:
                result = formatter.load(f)
            
            self.assertIsInstance(result, dict)
            self.assertEqual(result["id"], "test1")
        finally:
            os.unlink(temp_file)

    def test_roundtrip_single_node(self):
        """Test formatting and parsing a single node."""
        original = Node(id="test1", type="node", metadata={"key": "value"})
        
        # Format to JSON
        json_str = self.formatter.format(original.to_dict())
        
        # Parse back
        restored = self.formatter.parse(json_str)
        
        self.assertEqual(original.id, restored.id)
        self.assertEqual(original.type, restored.type)
        self.assertEqual(original.metadata, restored.metadata)

    def test_roundtrip_node_list(self):
        """Test formatting and parsing multiple nodes."""
        original = [
            Node(id="test1", type="node"),
            Requirement(id="req1", title="Test", description="Description")
        ]
        
        # Format to JSON
        json_str = self.formatter.format([n.to_dict() for n in original])
        
        # Parse back
        restored = self.formatter.parse(json_str)
        
        self.assertEqual(len(original), len(restored))
        self.assertEqual(original[0].id, restored[0].id)
        self.assertEqual(original[1].id, restored[1].id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
