"""
Test for GraphView.children bug where included nodes are missing from children property.

Bug: When a node has multiple ancestors in its path that are included, but some intermediate
ancestors are not included, the node may not appear in GraphView.children even though it
should be rendered at the top level of the diagram.

Example hierarchy:
- Root
  - A (included)
    - B (NOT included)
      - C (included)

In this case, C should appear in graph_view.children because its nearest included ancestor
(A) is not at the bottom of the tree. However, the current logic excludes C because there
are 2 included nodes in the path (A and C), not exactly 1.

The bug manifests when:
1. A node is included in the view
2. The node has relations pointing to it
3. But the node doesn't appear in graph_view.children
4. Result: Relations are rendered in C4 diagrams, but the target node is not rendered
"""

import unittest
from arch_tool import Node, Graph, Relation, Container
from arch_tool.view import GraphView


class TestGraphViewChildrenBug(unittest.TestCase):
    """Test cases for GraphView.children property filtering bug."""

    def setUp(self):
        """Create a test graph with hierarchical structure."""
        # Create a hierarchy:
        # Root
        #   - GroupA
        #     - GroupB (will not be included)
        #       - LeafC (will be included)
        #   - Feature1 (will be included)

        leaf_c = Node(id="leaf_c", type="requirement", metadata={"title": "Leaf C"})
        feature_1 = Node(
            id="feature_1", type="feature", metadata={"title": "Feature 1"}
        )
        group_b = Container(
            id="group_b",
            type="grouping",
            metadata={"title": "Group B"},
            children=[leaf_c],
        )
        group_a = Container(
            id="group_a",
            type="grouping",
            metadata={"title": "Group A"},
            children=[group_b],
        )

        # Build hierarchy with relations
        self.root = Graph(
            id="root",
            metadata={"title": "Test Graph"},
            children=[group_a, feature_1],
            relations=[Relation(src="leaf_c", dst="feature_1", type="delivered by")],
        )

    def test_included_node_with_non_included_parent_appears_in_children(self):
        """
        Test that an included node appears in children even when its immediate parent
        is not included but a grandparent is included.
        """
        graph_view = GraphView(self.root)

        # Include feature_1 and use extend to include leaf_c via the relation
        graph_view.include_nodes("feature_1")
        graph_view.extend({"type": "delivered by"}, {"type": "requirement"}, depth=1)

        # Verify that leaf_c is included in the view
        leaf_c = graph_view.get_node("leaf_c")
        self.assertIsNotNone(leaf_c, "leaf_c should be included in the view")

        # Verify that group_a is included (since it's an ancestor)
        # Note: This depends on how extend works - it may or may not include ancestors
        group_a = graph_view.get_node("group_a")

        # Verify that group_b is NOT included
        group_b = graph_view.get_node("group_b")
        self.assertIsNone(group_b, "group_b should NOT be included in the view")

        # Get the list of children
        children_ids = [child.id for child in graph_view.children]

        # BUG: leaf_c should appear in children because:
        # 1. It's included in the view
        # 2. Its immediate parent (group_b) is not included
        # 3. It should be "promoted" to appear at the level of its nearest included ancestor

        # The expected behavior is that leaf_c should appear in the children list
        # because it needs to be rendered in the diagram, but its parent is hidden
        self.assertIn(
            "leaf_c",
            children_ids,
            "leaf_c should appear in graph_view.children because its parent is not included",
        )

    def test_relation_to_missing_child_node(self):
        """
        Test that relations point to nodes that are actually rendered in children.

        This is the manifestation of the bug: a relation exists pointing to a node,
        but that node doesn't appear in the children list, causing the C4 formatter
        to render a relation to a non-existent node.
        """
        graph_view = GraphView(self.root)

        # Include feature_1 and use extend to include leaf_c via the relation
        graph_view.include_nodes("feature_1")
        graph_view.extend({"type": "delivered by"}, {"type": "requirement"}, depth=1)

        # Get all relations
        relations = list(graph_view.get_relations())

        # Get all children
        children_ids = set(child.id for child in graph_view.children)

        # Verify that all relation endpoints are in the children list
        for relation in relations:
            self.assertIn(
                relation.src,
                children_ids,
                f"Relation source {relation.src} should appear in graph_view.children",
            )
            self.assertIn(
                relation.dst,
                children_ids,
                f"Relation destination {relation.dst} should appear in graph_view.children",
            )

    def test_multiple_levels_of_hidden_parents(self):
        """
        Test with multiple levels of hidden parent nodes.
        """
        # Create deeper hierarchy:
        # Root
        #   - L1 (included)
        #     - L2 (not included)
        #       - L3 (not included)
        #         - L4 (included)

        l4 = Node(id="l4", type="requirement", metadata={"title": "Level 4"})
        l3 = Container(
            id="l3", type="grouping", metadata={"title": "Level 3"}, children=[l4]
        )
        l2 = Container(
            id="l2", type="grouping", metadata={"title": "Level 2"}, children=[l3]
        )
        l1 = Container(
            id="l1", type="grouping", metadata={"title": "Level 1"}, children=[l2]
        )
        root = Graph(id="root", metadata={"title": "Deep Test"}, children=[l1])

        graph_view = GraphView(root)
        graph_view.include_nodes(["l1", "l4"])

        # Verify l4 is included
        self.assertIsNotNone(graph_view.get_node("l4"))

        # Verify intermediate levels are not included
        self.assertIsNone(graph_view.get_node("l2"))
        self.assertIsNone(graph_view.get_node("l3"))

        # Get children
        child_ids = [c.id for c in graph_view.get_node("l1").children]

        # l4 should appear as a child of l1 (since l2 and l3 are hidden)
        # Note: This depends on whether we expect l4 to be promoted to l1's child
        # or to appear at the root level
        self.assertIn(
            "l4", child_ids, "l4 should appear somewhere in the children hierarchy"
        )


if __name__ == "__main__":
    unittest.main()
