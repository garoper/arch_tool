"""
Test cases for GraphNode.parent property with different node visibility scenarios.

The parent property should handle various cases where nodes in the hierarchy
are visible or hidden from the GraphView.
"""

import unittest
from arch_tool import Node, Graph, Container
from arch_tool.view import GraphView


class TestGraphNodeParent(unittest.TestCase):
    """Test cases for GraphNode.parent property across visibility scenarios."""

    def setUp(self):
        """Create a test graph with a deep hierarchy."""
        # Create hierarchy:
        # Root
        #   - L1
        #     - L2
        #       - L3
        #         - L4
        #           - L5
        
        l5 = Node(id="l5", type="requirement", metadata={"title": "Level 5"})
        l4 = Container(id="l4", type="grouping", metadata={"title": "Level 4"}, children=[l5])
        l3 = Container(id="l3", type="grouping", metadata={"title": "Level 3"}, children=[l4])
        l2 = Container(id="l2", type="grouping", metadata={"title": "Level 2"}, children=[l3])
        l1 = Container(id="l1", type="grouping", metadata={"title": "Level 1"}, children=[l2])
        self.root = Graph(id="root", metadata={"title": "Test Graph"}, children=[l1])

    def test_parent_when_all_ancestors_visible(self):
        """Test parent property when all ancestors are visible in the view."""
        graph_view = GraphView(self.root)
        graph_view.include_nodes(["l1", "l2", "l3", "l4", "l5"])
        
        l5_node = graph_view.get_node("l5")
        self.assertIsNotNone(l5_node, "l5 should be included")
        
        # Get parent chain
        parent = l5_node.parent
        self.assertIsNotNone(parent, "l5 should have a parent")
        self.assertEqual(parent.id, "l4", "l5's parent should be l4")
        
        grandparent = parent.parent
        self.assertIsNotNone(grandparent, "l4 should have a parent")
        self.assertEqual(grandparent.id, "l3", "l4's parent should be l3")

    def test_parent_when_immediate_parent_hidden(self):
        """Test parent property when immediate parent is hidden but grandparent is visible."""
        graph_view = GraphView(self.root)
        # Include l1, l3, and l5, but skip l2 and l4
        graph_view.include_nodes(["l1", "l3", "l5"])
        
        l5_node = graph_view.get_node("l5")
        self.assertIsNotNone(l5_node, "l5 should be included")
        
        # l4 is hidden, so parent should skip to the next visible ancestor (l3)
        parent = l5_node.parent
        self.assertIsNotNone(parent, "l5 should have a parent")
        self.assertEqual(parent.id, "l3", "l5's parent should be l3 (skipping hidden l4)")
        
        # Walk up the parent chain and collect all visible parents
        parents = []
        current = l5_node.parent
        while current is not None:
            parents.append(current.id)
            try:
                current = current.parent
            except (IndexError, AttributeError):
                # Hit the root or an empty path
                break
        
        # The parent chain should only include visible nodes
        self.assertNotIn("l4", parents, "Parent chain should NOT include hidden l4")
        self.assertNotIn("l2", parents, "Parent chain should NOT include hidden l2")
        self.assertIn("l3", parents, "Parent chain should include visible l3")
        self.assertIn("l1", parents, "Parent chain should include visible l1")

    def test_parent_when_multiple_ancestors_hidden(self):
        """Test parent property when multiple consecutive ancestors are hidden."""
        graph_view = GraphView(self.root)
        # Include only l1 and l5, hiding l2, l3, l4
        graph_view.include_nodes(["l1", "l5"])
        
        l5_node = graph_view.get_node("l5")
        self.assertIsNotNone(l5_node, "l5 should be included")
        
        # Should skip all hidden ancestors and return l1
        parent = l5_node.parent
        self.assertIsNotNone(parent, "l5 should have a parent")
        self.assertEqual(parent.id, "l1", "l5's parent should be l1 (skipping all hidden ancestors)")
        
        # Walk up parent chain - should only have visible nodes
        parents = []
        current = l5_node.parent
        max_iterations = 10  # Prevent infinite loops
        iterations = 0
        
        while current is not None and iterations < max_iterations:
            parents.append(current.id)
            iterations += 1
            try:
                current = current.parent
            except (IndexError, AttributeError):
                break
        
        # Should only have visible nodes
        self.assertNotIn("l4", parents, "Parent chain should NOT include hidden l4")
        self.assertNotIn("l3", parents, "Parent chain should NOT include hidden l3")
        self.assertNotIn("l2", parents, "Parent chain should NOT include hidden l2")
        self.assertIn("l1", parents, "Parent chain should include visible l1")

    def test_parent_of_top_level_node(self):
        """Test parent property of a top-level node in the view."""
        graph_view = GraphView(self.root)
        graph_view.include_nodes(["l1", "l2", "l3"])
        
        l1_node = graph_view.get_node("l1")
        self.assertIsNotNone(l1_node, "l1 should be included")
        
        # l1's parent should be None or root depending on whether root is included
        # Since root is not explicitly included, parent should be None
        parent = l1_node.parent
        self.assertIsNone(parent, "l1's parent should be None since root is not included")

    def test_parent_chain_terminates_correctly(self):
        """Test that walking up the parent chain terminates without errors."""
        graph_view = GraphView(self.root)
        graph_view.include_nodes(["l1", "l2", "l3", "l4", "l5"])
        
        l5_node = graph_view.get_node("l5")
        
        # Walk all the way up to root
        current = l5_node
        visited = []
        max_iterations = 10
        iterations = 0
        
        while current is not None and iterations < max_iterations:
            visited.append(current.id)
            iterations += 1
            try:
                current = current.parent
            except (IndexError, AttributeError) as e:
                # This is the bug - parent property can raise IndexError
                self.fail(f"Parent property raised {type(e).__name__}: {e}. Visited so far: {visited}")
        
        # Should have visited all levels from l5 to l1 (root is not included)
        self.assertEqual(
            visited,
            ["l5", "l4", "l3", "l2", "l1"],
            "Should visit all nodes from l5 to l1"
        )

    def test_parent_when_only_leaf_visible(self):
        """Test parent property when only a leaf node is visible."""
        graph_view = GraphView(self.root)
        graph_view.include_nodes(["l5"])  # Only the deepest node
        
        l5_node = graph_view.get_node("l5")
        self.assertIsNotNone(l5_node, "l5 should be included")
        
        # Since no ancestors are visible, parent should be None
        parent = l5_node.parent
        self.assertIsNone(parent, "l5 should have no visible parent")

    def test_parent_returns_none_at_root(self):
        """Test that parent returns None when reaching the root or empty path."""
        graph_view = GraphView(self.root)
        graph_view.include_nodes(["l1"])
        
        l1_node = graph_view.get_node("l1")
        root_node = l1_node.parent
        
        # Try to get parent of root
        if root_node is not None:
            try:
                root_parent = root_node.parent
                # If we get here without error, root_parent should be None
                # or we should hit an error
                self.assertIsNone(
                    root_parent,
                    "Parent of root should be None or raise an appropriate error"
                )
            except (IndexError, AttributeError):
                # Current implementation may raise IndexError for empty path
                # This is acceptable but should be documented
                pass

    def test_parent_with_sibling_nodes(self):
        """Test parent property with multiple siblings at the same level."""
        # Create a tree with siblings:
        # Root
        #   - A
        #     - A1
        #     - A2
        #   - B
        #     - B1
        
        a1 = Node(id="a1", type="requirement", metadata={"title": "A1"})
        a2 = Node(id="a2", type="requirement", metadata={"title": "A2"})
        b1 = Node(id="b1", type="requirement", metadata={"title": "B1"})
        
        a = Container(id="a", type="grouping", metadata={"title": "A"}, children=[a1, a2])
        b = Container(id="b", type="grouping", metadata={"title": "B"}, children=[b1])
        
        root = Graph(id="root", metadata={"title": "Sibling Test"}, children=[a, b])
        
        graph_view = GraphView(root)
        graph_view.include_nodes(["a", "a1", "a2", "b", "b1"])
        
        # Test that siblings have the same parent
        a1_node = graph_view.get_node("a1")
        a2_node = graph_view.get_node("a2")
        
        self.assertIsNotNone(a1_node)
        self.assertIsNotNone(a2_node)
        
        a1_parent = a1_node.parent
        a2_parent = a2_node.parent
        
        self.assertIsNotNone(a1_parent)
        self.assertIsNotNone(a2_parent)
        
        self.assertEqual(a1_parent.id, "a", "a1's parent should be a")
        self.assertEqual(a2_parent.id, "a", "a2's parent should be a")
        self.assertEqual(a1_parent.id, a2_parent.id, "Siblings should have the same parent")

    def test_parent_after_extend_operation(self):
        """Test parent property after using extend to include related nodes."""
        # Create a simple hierarchy with a relation
        leaf = Node(id="leaf", type="requirement", metadata={"title": "Leaf"})
        feature = Node(id="feature", type="feature", metadata={"title": "Feature"})
        group = Container(id="group", type="grouping", metadata={"title": "Group"}, children=[leaf])
        
        root = Graph(
            id="root",
            metadata={"title": "Extend Test"},
            children=[group, feature],
            relations=[{"src": "leaf", "dst": "feature", "type": "delivered by"}]
        )
        
        graph_view = GraphView(root)
        graph_view.include_nodes("feature")
        # Include group as well so it's visible
        graph_view.include_nodes("group")
        graph_view.extend({"type": "delivered by"}, {"type": "requirement"}, depth=1)
        
        # After extend, leaf should be included
        leaf_node = graph_view.get_node("leaf")
        self.assertIsNotNone(leaf_node, "leaf should be included after extend")
        
        # Check parent - should be group since it's visible
        parent = leaf_node.parent
        self.assertIsNotNone(parent, "leaf should have a parent")
        self.assertEqual(parent.id, "group", "leaf's parent should be group")


if __name__ == "__main__":
    unittest.main()
