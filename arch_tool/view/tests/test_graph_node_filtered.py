"""
Test cases for GraphNode.__filtered parameter behavior.

The __filtered parameter controls whether GraphNode should respect the GraphView's
included/excluded node filtering or provide access to all nodes in the underlying graph.
"""

import unittest
from arch_tool import Node, Graph, Container
from arch_tool.view import GraphView


class TestGraphNodeFiltered(unittest.TestCase):
    """Test cases for GraphNode.__filtered parameter behavior."""

    def setUp(self):
        """Create a test graph with a hierarchy and relations."""
        # Create hierarchy:
        # Root
        #   - Parent
        #     - Child1
        #     - Child2
        #   - Sibling
        #     - Nephew
        
        child1 = Node(id="child1", type="requirement", metadata={"title": "Child 1"})
        child2 = Node(id="child2", type="requirement", metadata={"title": "Child 2"})
        nephew = Node(id="nephew", type="requirement", metadata={"title": "Nephew"})
        
        parent = Container(
            id="parent",
            type="grouping",
            metadata={"title": "Parent"},
            children=[child1, child2]
        )
        sibling = Container(
            id="sibling",
            type="grouping",
            metadata={"title": "Sibling"},
            children=[nephew]
        )
        
        self.root = Graph(
            id="root",
            metadata={"title": "Test Graph"},
            children=[parent, sibling],
            relations=[
                {"src": "child1", "dst": "nephew", "type": "relates to"},
                {"src": "child2", "dst": "nephew", "type": "depends on"}
            ]
        )

    def test_parent_with_filtered_true(self):
        """Test that parent respects filtering when filtered=True (default)."""
        graph_view = GraphView(self.root)
        # Include child1 and parent, but not the intermediate nodes if any
        graph_view.include_nodes(["parent", "child1"])
        
        child1_node = graph_view.get_node("child1")
        self.assertIsNotNone(child1_node, "child1 should be included")
        
        # With filtering enabled, parent should return the visible parent
        parent = child1_node.parent
        self.assertIsNotNone(parent, "child1 should have a visible parent")
        self.assertEqual(parent.id, "parent", "child1's parent should be 'parent'")

    def test_parent_with_filtered_false(self):
        """Test that parent ignores filtering when filtered=False."""
        graph_view = GraphView(self.root)
        # Include only child1, exclude parent
        graph_view.include_nodes(["child1"])
        
        # Get child1 with filtered=False to access all nodes
        child1_node = graph_view.get_node("child1", all=True)
        self.assertIsNotNone(child1_node, "child1 should exist in graph")
        
        # Create an unfiltered GraphNode manually (simulating internal access)
        from arch_tool.view.graph_node import GraphNode
        unfiltered_child1 = GraphNode(
            graph_view._GraphView__index.get_path("child1"),
            graph_view,
            filtered=False
        )
        
        # With filtering disabled, parent should return parent even if not included
        parent = unfiltered_child1.parent
        self.assertIsNotNone(parent, "child1 should have a parent (unfiltered)")
        self.assertEqual(parent.id, "parent", "child1's parent should be 'parent' (unfiltered)")

    def test_children_with_filtered_true(self):
        """Test that children respects filtering when filtered=True (default)."""
        graph_view = GraphView(self.root)
        # Include parent and child1, but exclude child2
        graph_view.include_nodes(["parent", "child1"])
        
        parent_node = graph_view.get_node("parent")
        self.assertIsNotNone(parent_node, "parent should be included")
        
        # Get children - should only return visible children
        children = list(parent_node.children)
        child_ids = [child.id for child in children]
        
        self.assertIn("child1", child_ids, "child1 should be in children (visible)")
        self.assertNotIn("child2", child_ids, "child2 should NOT be in children (hidden)")

    def test_children_with_filtered_false(self):
        """Test that children ignores filtering when filtered=False."""
        graph_view = GraphView(self.root)
        # Include only parent, exclude both children
        graph_view.include_nodes(["parent"])
        
        # Create an unfiltered GraphNode manually
        from arch_tool.view.graph_node import GraphNode
        unfiltered_parent = GraphNode(
            graph_view._GraphView__index.get_path("parent"),
            graph_view,
            filtered=False
        )
        
        # Get children - should return ALL children, regardless of visibility
        children = list(unfiltered_parent.children)
        child_ids = [child.id for child in children]
        
        self.assertIn("child1", child_ids, "child1 should be in children (unfiltered)")
        self.assertIn("child2", child_ids, "child2 should be in children (unfiltered)")

    def test_get_relations_with_filtered_true(self):
        """Test that get_relations respects filtering when filtered=True (default)."""
        graph_view = GraphView(self.root)
        # Include child1 and nephew, exclude child2
        graph_view.include_nodes(["child1", "nephew"])
        # Need to extend to include relations
        graph_view.extend({"type": "relates to"}, None, depth=1)
        
        child1_node = graph_view.get_node("child1")
        self.assertIsNotNone(child1_node, "child1 should be included")
        
        # Get relations - should only return relations where both endpoints are visible
        relations = list(child1_node.get_relations("outgoing"))
        relation_types = [rel.type for rel in relations]
        
        # child1 -> nephew relation should be visible
        self.assertIn("relates to", relation_types, "child1->nephew relation should be visible")
        
        # Now test child2 - it's not included, so we shouldn't get it
        child2_node = graph_view.get_node("child2")
        self.assertIsNone(child2_node, "child2 should not be included (filtered)")

    def test_get_relations_with_filtered_false(self):
        """Test that get_relations ignores filtering when filtered=False."""
        graph_view = GraphView(self.root)
        # Include only child1, exclude nephew and child2
        graph_view.include_nodes(["child1"])
        
        # Create an unfiltered GraphNode manually
        from arch_tool.view.graph_node import GraphNode
        unfiltered_child1 = GraphNode(
            graph_view._GraphView__index.get_path("child1"),
            graph_view,
            filtered=False
        )
        
        # Get relations - should return ALL relations, regardless of endpoint visibility
        relations = list(unfiltered_child1.get_relations("outgoing"))
        
        # child1 has one outgoing relation (to nephew)
        self.assertEqual(len(relations), 1, "child1 should have 1 outgoing relation (unfiltered)")
        self.assertEqual(relations[0].dst, "nephew", "relation target should be nephew")

    def test_descendants_with_filtered_true(self):
        """Test that descendants respects filtering when filtered=True (default)."""
        graph_view = GraphView(self.root)
        # Include parent and child1, exclude child2
        graph_view.include_nodes(["parent", "child1"])
        
        parent_node = graph_view.get_node("parent")
        self.assertIsNotNone(parent_node, "parent should be included")
        
        # Get descendants - should only return visible descendants
        descendants = list(parent_node.descendants)
        descendant_ids = [desc.id for desc in descendants]
        
        self.assertIn("child1", descendant_ids, "child1 should be in descendants (visible)")
        self.assertNotIn("child2", descendant_ids, "child2 should NOT be in descendants (hidden)")

    def test_descendants_with_filtered_false(self):
        """Test that descendants ignores filtering when filtered=False."""
        graph_view = GraphView(self.root)
        # Include only parent, exclude children
        graph_view.include_nodes(["parent"])
        
        # Create an unfiltered GraphNode manually
        from arch_tool.view.graph_node import GraphNode
        unfiltered_parent = GraphNode(
            graph_view._GraphView__index.get_path("parent"),
            graph_view,
            filtered=False
        )
        
        # Get descendants - should return ALL descendants
        descendants = list(unfiltered_parent.descendants)
        descendant_ids = [desc.id for desc in descendants]
        
        self.assertIn("child1", descendant_ids, "child1 should be in descendants (unfiltered)")
        self.assertIn("child2", descendant_ids, "child2 should be in descendants (unfiltered)")

    def test_successors_with_filtered_true(self):
        """Test that successors respects filtering when filtered=True (default)."""
        graph_view = GraphView(self.root)
        # Include child1 and nephew
        graph_view.include_nodes(["child1", "nephew"])
        graph_view.extend({"type": "relates to"}, None, depth=1)
        
        child1_node = graph_view.get_node("child1")
        self.assertIsNotNone(child1_node, "child1 should be included")
        
        # Get successors via "relates to" relation
        successors = list(child1_node.successors(type="relates to"))
        successor_ids = [succ.id for succ in successors]
        
        self.assertIn("nephew", successor_ids, "nephew should be a successor of child1")

    def test_successors_with_filtered_false(self):
        """Test that successors ignores filtering when filtered=False."""
        graph_view = GraphView(self.root)
        # Include only child1, exclude nephew
        graph_view.include_nodes(["child1"])
        
        # Create an unfiltered GraphNode manually
        from arch_tool.view.graph_node import GraphNode
        unfiltered_child1 = GraphNode(
            graph_view._GraphView__index.get_path("child1"),
            graph_view,
            filtered=False
        )
        
        # Get successors - should return nephew even though it's not included
        successors = list(unfiltered_child1.successors(type="relates to"))
        successor_ids = [succ.id for succ in successors]
        
        self.assertIn("nephew", successor_ids, "nephew should be a successor (unfiltered)")

    def test_predecessors_with_filtered_true(self):
        """Test that predecessors respects filtering when filtered=True (default)."""
        graph_view = GraphView(self.root)
        # Include nephew, child1, and child2
        graph_view.include_nodes(["nephew", "child1", "child2"])
        graph_view.extend({"type": ["relates to", "depends on"]}, None, depth=1)
        
        nephew_node = graph_view.get_node("nephew")
        self.assertIsNotNone(nephew_node, "nephew should be included")
        
        # Get predecessors
        predecessors = list(nephew_node.predecessors())
        predecessor_ids = [pred.id for pred in predecessors]
        
        # Both child1 and child2 point to nephew
        self.assertIn("child1", predecessor_ids, "child1 should be a predecessor")
        self.assertIn("child2", predecessor_ids, "child2 should be a predecessor")

    def test_predecessors_with_filtered_false(self):
        """Test that predecessors ignores filtering when filtered=False."""
        graph_view = GraphView(self.root)
        # Include only nephew, exclude child1 and child2
        graph_view.include_nodes(["nephew"])
        
        # Create an unfiltered GraphNode manually
        from arch_tool.view.graph_node import GraphNode
        unfiltered_nephew = GraphNode(
            graph_view._GraphView__index.get_path("nephew"),
            graph_view,
            filtered=False
        )
        
        # Get predecessors - should return both child1 and child2 even if hidden
        predecessors = list(unfiltered_nephew.predecessors())
        predecessor_ids = [pred.id for pred in predecessors]
        
        self.assertIn("child1", predecessor_ids, "child1 should be a predecessor (unfiltered)")
        self.assertIn("child2", predecessor_ids, "child2 should be a predecessor (unfiltered)")

    def test_has_descendant_with_filtered_true(self):
        """Test that has_descendant respects filtering when filtered=True (default)."""
        graph_view = GraphView(self.root)
        # Include parent and child1, exclude child2
        graph_view.include_nodes(["parent", "child1"])
        
        parent_node = graph_view.get_node("parent")
        self.assertIsNotNone(parent_node, "parent should be included")
        
        # Check for visible descendant
        self.assertTrue(
            parent_node.has_descendant({"id": "child1"}),
            "parent should have child1 as descendant (visible)"
        )
        
        # Check for hidden descendant
        self.assertFalse(
            parent_node.has_descendant({"id": "child2"}),
            "parent should NOT have child2 as descendant (hidden)"
        )

    def test_has_descendant_with_filtered_false(self):
        """Test that has_descendant ignores filtering when filtered=False."""
        graph_view = GraphView(self.root)
        # Include only parent, exclude children
        graph_view.include_nodes(["parent"])
        
        # Create an unfiltered GraphNode manually
        from arch_tool.view.graph_node import GraphNode
        unfiltered_parent = GraphNode(
            graph_view._GraphView__index.get_path("parent"),
            graph_view,
            filtered=False
        )
        
        # Check for descendants - should find both even if hidden
        self.assertTrue(
            unfiltered_parent.has_descendant({"id": "child1"}),
            "parent should have child1 as descendant (unfiltered)"
        )
        self.assertTrue(
            unfiltered_parent.has_descendant({"id": "child2"}),
            "parent should have child2 as descendant (unfiltered)"
        )

    def test_has_child_with_filtered_true(self):
        """Test that has_child respects filtering when filtered=True (default)."""
        graph_view = GraphView(self.root)
        # Include parent and child1, exclude child2
        graph_view.include_nodes(["parent", "child1"])
        
        parent_node = graph_view.get_node("parent")
        self.assertIsNotNone(parent_node, "parent should be included")
        
        # Check for visible child
        self.assertTrue(
            parent_node.has_child({"id": "child1"}),
            "parent should have child1 as child (visible)"
        )
        
        # Check for hidden child
        self.assertFalse(
            parent_node.has_child({"id": "child2"}),
            "parent should NOT have child2 as child (hidden)"
        )

    def test_has_child_with_filtered_false(self):
        """Test that has_child ignores filtering when filtered=False."""
        graph_view = GraphView(self.root)
        # Include only parent, exclude children
        graph_view.include_nodes(["parent"])
        
        # Create an unfiltered GraphNode manually
        from arch_tool.view.graph_node import GraphNode
        unfiltered_parent = GraphNode(
            graph_view._GraphView__index.get_path("parent"),
            graph_view,
            filtered=False
        )
        
        # Check for children - should find both even if hidden
        self.assertTrue(
            unfiltered_parent.has_child({"id": "child1"}),
            "parent should have child1 as child (unfiltered)"
        )
        self.assertTrue(
            unfiltered_parent.has_child({"id": "child2"}),
            "parent should have child2 as child (unfiltered)"
        )

    def test_has_relation_with_filtered_true(self):
        """Test that has_relation respects filtering when filtered=True (default)."""
        graph_view = GraphView(self.root)
        # Include child1 and nephew
        graph_view.include_nodes(["child1", "nephew"])
        graph_view.extend({"type": "relates to"}, None, depth=1)
        
        child1_node = graph_view.get_node("child1")
        self.assertIsNotNone(child1_node, "child1 should be included")
        
        # Check for relation to visible node
        self.assertTrue(
            child1_node.has_relation({"type": "relates to"}),
            "child1 should have 'relates to' relation (visible)"
        )

    def test_has_relation_with_filtered_false(self):
        """Test that has_relation ignores filtering when filtered=False."""
        graph_view = GraphView(self.root)
        # Include only child1, exclude nephew
        graph_view.include_nodes(["child1"])
        
        # Create an unfiltered GraphNode manually
        from arch_tool.view.graph_node import GraphNode
        unfiltered_child1 = GraphNode(
            graph_view._GraphView__index.get_path("child1"),
            graph_view,
            filtered=False
        )
        
        # Check for relation - should find it even if target is hidden
        self.assertTrue(
            unfiltered_child1.has_relation({"type": "relates to"}),
            "child1 should have 'relates to' relation (unfiltered)"
        )

    def test_filtered_parameter_propagation_through_children(self):
        """Test that filtered parameter propagates correctly when accessing children."""
        graph_view = GraphView(self.root)
        graph_view.include_nodes(["parent", "child1"])
        
        # Get parent with filtered=True (default)
        parent_filtered = graph_view.get_node("parent")
        
        # Get children - they should also be filtered
        children_filtered = list(parent_filtered.children)
        self.assertEqual(len(children_filtered), 1, "Should have 1 visible child")
        
        # Create unfiltered parent
        from arch_tool.view.graph_node import GraphNode
        parent_unfiltered = GraphNode(
            graph_view._GraphView__index.get_path("parent"),
            graph_view,
            filtered=False
        )
        
        # Get children - should have all children
        children_unfiltered = list(parent_unfiltered.children)
        self.assertEqual(len(children_unfiltered), 2, "Should have 2 children (unfiltered)")

    def test_filtered_parameter_propagation_through_parent(self):
        """Test that filtered parameter propagates correctly when accessing parent."""
        graph_view = GraphView(self.root)
        graph_view.include_nodes(["child1"])  # Exclude parent
        
        # Create unfiltered child
        from arch_tool.view.graph_node import GraphNode
        child_unfiltered = GraphNode(
            graph_view._GraphView__index.get_path("child1"),
            graph_view,
            filtered=False
        )
        
        # Get parent - should return parent even if it's not included
        parent = child_unfiltered.parent
        self.assertIsNotNone(parent, "Should have parent (unfiltered)")
        self.assertEqual(parent.id, "parent", "Parent should be 'parent'")


if __name__ == "__main__":
    unittest.main()
