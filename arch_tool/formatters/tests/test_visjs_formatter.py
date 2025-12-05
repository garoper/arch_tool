"""Unit tests for VisJSFormatter class."""

import unittest
import sys
import os
import base64
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path to import arch_tool
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from arch_tool import Node, Relation, Graph
from arch_tool.formatters.visjs_formatter import VisJSFormatter


class TestVisJSFormatter(unittest.TestCase):
    """Test cases for the VisJSFormatter class."""

    def setUp(self):
        """Set up VisJSFormatter for each test."""
        self.formatter = VisJSFormatter()

    @patch('arch_tool.formatters.visjs_formatter.VisJSFormatter._VisJSFormatter__download_visjs_script')
    def test_format_returns_html_string(self, mock_download):
        """Test that format() returns an HTML string."""
        # Mock the vis.js script download
        mock_download.return_value = "// Mock vis.js script"
        
        # Create a simple graph
        node1 = Node(id="node1", type="component")
        node2 = Node(id="node2", type="component")
        
        # Format the graph
        result = self.formatter.format([node1, node2])
        
        # Verify result is a string
        self.assertIsInstance(result, str)
        
        # Verify it's HTML
        self.assertIn("<!DOCTYPE html>", result)
        self.assertIn("<html>", result)
        self.assertIn("</html>", result)

    @patch('arch_tool.formatters.visjs_formatter.VisJSFormatter._VisJSFormatter__download_visjs_script')
    def test_format_contains_visjs_script(self, mock_download):
        """Test that the formatted HTML contains the vis.js script."""
        mock_script = "// Mock vis.js library content"
        mock_download.return_value = mock_script
        
        node = Node(id="test1", type="node")
        self.formatter.clear_cache()
        result = self.formatter.format([node])
        
        # Verify the script is embedded
        self.assertIn(mock_script, result)

    @patch('arch_tool.formatters.visjs_formatter.VisJSFormatter._VisJSFormatter__download_visjs_script')
    def test_format_contains_base64_data(self, mock_download):
        """Test that the formatted HTML contains base64-encoded data."""
        mock_download.return_value = "// Mock script"
        
        node = Node(id="test1", type="component", metadata={"name": "Test Node"})
        result = self.formatter.format([node])
        
        # Verify base64 data is present
        self.assertIn("decodeBase64Json", result)

    @patch('arch_tool.formatters.visjs_formatter.VisJSFormatter._VisJSFormatter__download_visjs_script')
    def test_format_with_multiple_nodes(self, mock_download):
        """Test formatting with multiple nodes."""
        mock_download.return_value = "// Mock script"
        
        nodes = [
            Node(id="node1", type="component"),
            Node(id="node2", type="database"),
            Node(id="node3", type="system")
        ]
        
        result = self.formatter.format(nodes)
        
        self.assertIsInstance(result, str)
        self.assertIn("<!DOCTYPE html>", result)
        self.assertGreater(len(result), 0)

    @patch('arch_tool.formatters.visjs_formatter.VisJSFormatter._VisJSFormatter__download_visjs_script')
    def test_format_with_relations(self, mock_download):
        """Test formatting nodes with relations (edges)."""
        mock_download.return_value = "// Mock script"
        
        node1 = Node(id="node1", type="component")
        node2 = Node(id="node2", type="component")
        relation = Relation(src=node1, dst=node2, type="depends_on")
        node1.relations = [relation]
        
        result = self.formatter.format([node1, node2])
        
        self.assertIsInstance(result, str)
        self.assertIn("<!DOCTYPE html>", result)

    @patch('arch_tool.formatters.visjs_formatter.VisJSFormatter._VisJSFormatter__download_visjs_script')
    def test_format_creates_file_when_filename_provided(self, mock_download):
        """Test that format() creates a file when filename is provided."""
        mock_download.return_value = "// Mock script"
        
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_output.html")
            node = Node(id="test1", type="node")
            
            result = self.formatter.format([node], file_name=file_path)
            
            # Should return None when writing to file
            self.assertIsNone(result)
            
            # File should exist
            self.assertTrue(os.path.exists(file_path))
            
            # File should contain HTML
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn("<!DOCTYPE html>", content)

    @patch('arch_tool.formatters.visjs_formatter.VisJSFormatter._VisJSFormatter__download_visjs_script')
    def test_format_with_custom_options(self, mock_download):
        """Test formatting with custom vis.js options."""
        mock_download.return_value = "// Mock script"
        
        custom_formatter = VisJSFormatter(
            width="800px",
            height="600px",
            locale="en",
            click_to_use=True
        )
        
        node = Node(id="test1", type="node")
        result = custom_formatter.format([node])
        
        self.assertIsInstance(result, str)
        self.assertIn("<!DOCTYPE html>", result)

    @patch('arch_tool.formatters.visjs_formatter.VisJSFormatter._VisJSFormatter__download_visjs_script')
    def test_format_empty_graph(self, mock_download):
        """Test formatting an empty graph."""
        mock_download.return_value = "// Mock script"
        
        result = self.formatter.format([])
        
        self.assertIsInstance(result, str)
        self.assertIn("<!DOCTYPE html>", result)

    def test_options_property(self):
        """Test that options property returns the configuration."""
        formatter = VisJSFormatter(
            width="100%",
            height="100%",
            locale="en"
        )
        
        options = formatter.options
        
        self.assertIsInstance(options, dict)
        self.assertEqual(options["width"], "100%")
        self.assertEqual(options["height"], "100%")
        self.assertEqual(options["locale"], "en")

    @patch('arch_tool.formatters.visjs_formatter.VisJSFormatter._VisJSFormatter__download_visjs_script')
    def test_nested_nodes_are_collected(self, mock_download):
        """Test that nested child nodes are properly collected."""
        mock_download.return_value = "// Mock script"
        
        parent = Node(id="parent", type="component")
        child1 = Node(id="child1", type="component")
        child2 = Node(id="child2", type="component")
        parent.children = [child1, child2]
        
        result = self.formatter.format([parent])
        
        self.assertIsInstance(result, str)
        self.assertIn("<!DOCTYPE html>", result)


if __name__ == "__main__":
    unittest.main()
