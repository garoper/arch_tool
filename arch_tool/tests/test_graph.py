"""Unit tests for Graph.extend method."""

import unittest
import sys
import os

# Add parent directory to path to import arch_tool
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from arch_tool import Graph, Node, Requirement, Grouping, Relation, Container


class TestGraphExtend(unittest.TestCase):
    """Test cases for the Graph.extend method."""

    def setUp(self):
        """Set up a Graph for each test."""
        self.graph = Graph(id="test_graph")

    def test_append_with_single_node(self):
        """Test extending graph with a single node."""
        node = Node(id="node1", type="node")
        self.graph.append(node)

        self.assertEqual(len(self.graph.children), 1)
        self.assertEqual(next(iter(self.graph.children)).id, "node1")

    def test_append_with_node_list(self):
        """Test extending graph with a list of nodes."""
        nodes = [
            Node(id="node1", type="node"),
            Node(id="node2", type="node"),
            Requirement(id="req1", title="Test", description="Desc"),
        ]
        self.graph.append(nodes)

        graph_children = list(self.graph.children)
        self.assertEqual(len(graph_children), 3)
        self.assertEqual(graph_children[0].id, "node1")
        self.assertEqual(graph_children[1].id, "node2")
        self.assertEqual(graph_children[2].id, "req1")

    def test_append_with_dict_containing_children(self):
        """Test extending graph with a dictionary containing children."""
        data = {
            "id": "root",
            "type": "root",
            "children": [
                {"id": "node1", "type": "node"},
                {"id": "node2", "type": "node"},
            ],
        }
        self.graph.append(data)

        graph_children = list(self.graph.children)
        self.assertEqual(len(graph_children), 2)
        self.assertEqual(graph_children[0].id, "node1")
        self.assertEqual(graph_children[1].id, "node2")

    def test_append_with_dict_containing_relations(self):
        """Test extending graph with a dictionary containing relations."""
        data = {
            "id": "root",
            "type": "root",
            "relations": [
                {"src": "node1", "dst": "node2", "type": "depends on"},
                {"src": "node2", "dst": "node3", "type": "implements"},
            ],
        }
        self.graph.append(data)

        graph_relations = list(self.graph.relations)
        self.assertEqual(len(graph_relations), 2)
        self.assertEqual(graph_relations[0].src, "node1")
        self.assertEqual(graph_relations[0].dst, "node2")
        self.assertEqual(graph_relations[1].type, "implements")

    def test_append_with_dict_containing_both(self):
        """Test extending graph with dictionary containing both children and relations."""
        data = {
            "id": "root",
            "type": "root",
            "children": [
                {"id": "node1", "type": "node"},
                {"id": "node2", "type": "node"},
            ],
            "relations": [{"src": "node1", "dst": "node2", "type": "depends on"}],
        }
        self.graph.append(data)

        graph_children = list(self.graph.children)
        graph_relations = list(self.graph.relations)

        self.assertEqual(len(graph_children), 2)
        self.assertEqual(len(graph_relations), 1)
        self.assertEqual(graph_children[0].id, "node1")
        self.assertEqual(graph_relations[0].src, "node1")

    def test_append_preserves_existing_children(self):
        """Test that extend adds to existing children rather than replacing."""
        # Add initial children
        self.graph.add_child(Node(id="existing1", type="node"))
        self.assertEqual(len(self.graph.children), 1)

        # Extend with more
        self.graph.append([Node(id="new1", type="node"), Node(id="new2", type="node")])

        graph_children = list(self.graph.children)
        self.assertEqual(len(graph_children), 3)
        self.assertEqual(graph_children[0].id, "existing1")
        self.assertEqual(graph_children[1].id, "new1")
        self.assertEqual(graph_children[2].id, "new2")

    def test_append_preserves_existing_relations(self):
        """Test that extend adds to existing relations rather than replacing."""
        # Add initial relation
        self.graph.create_relation("a", "b", "depends on")
        self.assertEqual(len(list(self.graph.relations)), 1)

        # Extend with more
        data = {
            "id": "root",
            "type": "root",
            "relations": [{"src": "c", "dst": "d", "type": "implements"}],
        }
        self.graph.append(data)
        graph_relations = list(self.graph.relations)
        self.assertEqual(len(graph_relations), 2)
        # add_relation stores dicts with 'from'/'to', not 'src'/'dst'
        self.assertEqual(graph_relations[0].src, "a")
        # extend with dict uses Relation which has 'src'/'dst' attributes
        self.assertEqual(graph_relations[1].src, "c")

    def test_append_with_empty_list(self):
        """Test extending with an empty list does nothing."""
        self.graph.append([])
        self.assertEqual(len(self.graph.children), 0)

    def test_append_with_nested_children(self):
        """Test extending with nodes that have their own children."""
        grouping = Grouping(
            id="group1",
            title="Test Group",
            children=[Node(id="child1", type="node"), Node(id="child2", type="node")],
        )
        self.graph.append(grouping)

        graph_children = list(self.graph.children)
        self.assertEqual(len(graph_children), 1)
        self.assertEqual(graph_children[0].id, "group1")
        self.assertEqual(len(graph_children[0].children), 2)

    def test_append_with_multiple_dicts(self):
        """Test extending with a list of dictionaries."""
        data = [
            {
                "id": "root1",
                "type": "root",
                "children": [{"id": "node1", "type": "node"}],
            },
            {
                "id": "root2",
                "type": "root",
                "children": [{"id": "node2", "type": "node"}],
            },
        ]
        self.graph.append(data)

        graph_children = list(self.graph.children)
        # Should add all children from both dicts
        self.assertEqual(len(graph_children), 2)
        self.assertEqual(graph_children[0].id, "node1")
        self.assertEqual(graph_children[1].id, "node2")

    def test_append_with_relation_objects(self):
        """Test extending with Relation objects directly."""
        relations = [
            Relation(src="node1", dst="node2", type="depends on"),
            Relation(src="node2", dst="node3", type="implements"),
        ]

        data = {
            "id": "graph_with_relations",
            "type": "root",
            "children": [],
            "relations": relations,
        }
        self.graph.append(data)

        self.assertEqual(len(list(self.graph.relations)), 2)
        self.assertIsInstance(next(iter(self.graph.relations)), Relation)


class TestGraph(unittest.TestCase):
    """Test cases for the Graph class."""

    def test_constructor_with_relations(self):
        """Test Graph constructor with initial relations."""
        relations = [
            Relation(src="node1", dst="node2", type="depends on"),
            Relation(src="node2", dst="node3", type="implements"),
        ]
        graph = Graph(id="test_graph", relations=relations)

        self.assertEqual(len(list(graph.relations)), 2)
        self.assertIsInstance(next(iter(graph.relations)), Relation)

    def test_constructor_with_mixed_relations_and_dicts(self):
        """Test Graph constructor with mixed Relation objects and dicts."""
        relations = [
            Relation(src="node1", dst="node2", type="depends on"),
            {"src": "node2", "dst": "node3", "type": "implements"},
        ]
        graph = Graph(id="test_graph", relations=relations)

        graph_relations = list(graph.relations)
        self.assertEqual(len(graph_relations), 2)
        self.assertIsInstance(graph_relations[0], Relation)
        self.assertIsInstance(graph_relations[1], Relation)
        self.assertEqual(graph_relations[1].src, "node2")



if __name__ == "__main__":
    unittest.main(verbosity=2)
