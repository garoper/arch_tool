
import unittest
import sys
import os

from arch_tool.view.graph_view import GraphView
from arch_tool import Node, System, Component

# Add parent directory to path to import arch_tool
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from arch_tool import Node, Graph, Container, Requirement, Relation, C4Formatter


class test_graph_view(unittest.TestCase):
    def test_get_node(self):
        """Test retrieving a node by ID."""
        graph = Graph(id="test_graph")
        node = Node(id="node1", type="node")
        graph.add_child(node)
        graph_view = GraphView(graph, include_all=True)

        retrieved_node = graph_view.get_node("node1")
        self.assertIsNotNone(retrieved_node)
        self.assertEqual(retrieved_node.id, "node1")

        non_existent_node = graph_view.get_node("nonexistent")
        self.assertIsNone(non_existent_node)

    def test_get_node_which_is_child_of_child(self):
        """Test retrieving a node by ID when it's a child of a child."""
        graph = Graph(id="test_graph")
        parent_node = Container(id="parent", type="node")
        child_node = Node(id="child", type="node")
        parent_node.add_child(child_node)
        graph.add_child(parent_node)
        graph_view = GraphView(graph, include_all=True)
        retrieved_node = graph_view.get_node("child")
        self.assertIsNotNone(retrieved_node)
        self.assertEqual(retrieved_node.id, "child")

    def test_get_node_that_no_longer_exists(self):
        """Test retrieving a node by ID that has been removed."""
        graph = Graph(id="test_graph")
        node = Node(id="node1", type="node")
        graph.add_child(node)
        graph_view = GraphView(graph, include_all=True)
        retrieved_node = graph_view.get_node("node1")
        self.assertIsNotNone(retrieved_node)
        self.assertEqual(retrieved_node.id, "node1")

        # Remove the node
        graph.remove_child("node1")
        graph_view.update()

        retrieved_node = graph_view.get_node("node1")
        self.assertIsNone(retrieved_node)


class TestGraphViewC4FormatterCompatibility(unittest.TestCase):
    """Test that GraphView fulfills all requirements to work with C4Formatter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.formatter = C4Formatter(
            type_map={
                "requirement": "Container",
                "node": "Component",
            },
            node_factory=Node.from_dict,
        )
        
    def test_graphview_relations_are_of_type_graphrelation(self):
        """Test that relations returned by GraphView are of type GraphRelation."""
        graph = Graph(id="test_root", type="root")
        node1 = Node(id="N1", type="node")
        node2 = Node(id="N2", type="node")
        graph.add_child(node1)
        graph.add_child(node2)
        graph.create_relation("N1", "N2", "depends on", tags=["dependency"])
        
        graph_view = GraphView(graph, include_all=True)
        
        relations = graph_view.relations
        self.assertIsNotNone(relations)
        
        relation_list = list(relations)
        self.assertEqual(len(relation_list), 1)
        
        rel = relation_list[0]
        from arch_tool.view.graph_relation import GraphRelation
        self.assertIsInstance(rel, GraphRelation)

    def test_graphview_has_id_attribute(self):
        """Test that GraphView has an 'id' attribute accessible via getattr."""
        graph = Graph(id="test_root", type="root")
        graph_view = GraphView(graph, include_all=True)
        
        # C4Formatter uses getattr to access node_obj.id
        self.assertTrue(hasattr(graph_view, "id"))
        self.assertEqual(graph_view.id, "test_root")
        
    def test_graphview_has_type_attribute(self):
        """Test that GraphView has a 'type' attribute accessible via getattr."""
        graph = Graph(id="test_root", type="root")
        graph_view = GraphView(graph, include_all=True)
        
        # C4Formatter uses node_obj.type
        self.assertTrue(hasattr(graph_view, "type"))
        self.assertEqual(graph_view.type, "root")
        
    def test_graphview_has_children_attribute(self):
        """Test that GraphView has a 'children' attribute accessible via getattr."""
        graph = Graph(id="test_root", type="root")
        child1 = Node(id="child1", type="node")
        child2 = Node(id="child2", type="node")
        graph.add_child(child1)
        graph.add_child(child2)
        
        graph_view = GraphView(graph, include_all=True)
        
        # C4Formatter uses getattr(node, "children", None)
        self.assertTrue(hasattr(graph_view, "children"))
        children = list(graph_view.children)
        self.assertEqual(len(children), 2)
        
    def test_graphview_children_are_iterable(self):
        """Test that GraphView.children returns an iterable."""
        graph = Graph(id="test_root", type="root")
        child1 = Node(id="child1", type="node")
        child2 = Node(id="child2", type="node")
        graph.add_child(child1)
        graph.add_child(child2)
        
        graph_view = GraphView(graph, include_all=True)
        
        # C4Formatter iterates over children
        children = graph_view.children
        self.assertIsNotNone(children)
        child_ids = [child.id for child in children]
        self.assertIn("child1", child_ids)
        self.assertIn("child2", child_ids)
        
    def test_graphview_has_relations_attribute(self):
        """Test that GraphView has a 'relations' attribute accessible via getattr."""
        graph = Graph(id="test_root", type="root")
        child1 = Node(id="child1", type="node")
        child2 = Node(id="child2", type="node")
        graph.add_child(child1)
        graph.add_child(child2)
        graph.create_relation("child1", "child2", "depends on")
        
        graph_view = GraphView(graph, include_all=True, title = "Test Graph")
        
        # C4Formatter uses getattr(root_node, "relations", None)
        self.assertTrue(hasattr(graph_view, "relations"))
        relations = list(graph_view.relations)
        self.assertGreater(len(relations), 0)
        
    def test_graphview_can_be_formatted_with_c4formatter(self):
        """Test that GraphView can be passed to C4Formatter.format()."""
        graph = Graph(id="test_root", type="root", metadata={"title": "Test Architecture"})
        req1 = Requirement(id="REQ1", title="Requirement 1", description="Test requirement")
        graph.add_child(req1)
        
        graph_view = GraphView(graph, include_all=True)
        
        # This should not raise an exception
        result = self.formatter.format(graph_view, include_header=True, include_footer=True)
        
        self.assertIsInstance(result, str)
        self.assertIn("@startuml", result)
        self.assertIn("@enduml", result)
        self.assertIn("title Test Architecture", result)
        self.assertIn("REQ1", result)
        
    def test_graphview_formatted_output_matches_graph(self):
        """Test that GraphView produces the same C4 output as Graph."""
        # Create identical graph structures
        graph = Graph(id="root", type="root", metadata={"title": "System"})
        req1 = Requirement(id="R1", title="Req 1", description="Description 1")
        req2 = Requirement(id="R2", title="Req 2", description="Description 2")
        graph.add_child(req1)
        graph.add_child(req2)
        graph.create_relation("R1", "R2", "depends on")
        
        graph_view = GraphView(graph, include_all=True)
        
        # Format both
        graph_output = self.formatter.format(graph, include_header=False, include_footer=False)
        view_output = self.formatter.format(graph_view, include_header=False, include_footer=False)
        
        # Outputs should be identical
        self.assertEqual(graph_output, view_output)
        
    def test_graphview_with_nested_children(self):
        """Test that GraphView works with nested children structures."""
        graph = Graph(id="root", type="root")
        container = Container(id="C1", type="container")
        child1 = Node(id="C1_1", type="node")
        child2 = Node(id="C1_2", type="node")
        container.add_child(child1)
        container.add_child(child2)
        graph.add_child(container)
        
        graph_view = GraphView(graph, include_all=True)
        
        # Format and check that nested structure is preserved
        result = self.formatter.format(graph_view, include_header=False, include_footer=False)
        
        self.assertIn("C1", result)
        self.assertIn("C1_1", result)
        self.assertIn("C1_2", result)
        self.assertIn("{", result)  # Container with children uses braces
        self.assertIn("}", result)
        
    def test_graphview_children_have_required_attributes(self):
        """Test that children returned by GraphView have id, type, and other required attributes."""
        graph = Graph(id="root", type="root")
        req = Requirement(id="REQ1", title="Test", description="Test desc", tags=["must"])
        graph.add_child(req)
        
        graph_view = GraphView(graph, include_all=True)
        
        children = list(graph_view.children)
        self.assertEqual(len(children), 1)
        
        child = children[0]
        # C4Formatter needs these attributes
        self.assertTrue(hasattr(child, "id"))
        self.assertTrue(hasattr(child, "type"))
        self.assertTrue(hasattr(child, "tags"))
        self.assertTrue(hasattr(child, "metadata"))
        
        self.assertEqual(child.id, "REQ1")
        self.assertEqual(child.type, "requirement")
        
    def test_graphview_supports_get_attribute_pattern(self):
        """Test that GraphView works with the get_attribute helper used by C4Formatter."""
        from arch_tool.formatters.c4_formatter import get_attribute
        
        graph = Graph(id="root", type="root", metadata={"custom": "value"})
        graph_view = GraphView(graph, include_all=True)
        
        # Test direct attribute access
        self.assertEqual(get_attribute(graph_view, "id"), "root")
        self.assertEqual(get_attribute(graph_view, "type"), "root")
        
        # Test metadata access
        metadata = get_attribute(graph_view, "metadata", {})
        self.assertEqual(metadata.get("custom"), "value")
        
        # Test default value
        self.assertEqual(get_attribute(graph_view, "nonexistent", "default"), "default")
    
    def test_graphview_extend_should_work_on_parent_child_relations(self):
        """Test that GraphView.extend() works with parent-child relations."""
        graph = Graph(id="root", type="root")
        parent = Container(id="parent", type="node")
        child = Node(id="child", type="node")
        parent.add_child(child)
        graph.add_child(parent)
        
        graph_view = GraphView(graph, include_all=False)
        graph_view.include_nodes("parent")
        
        # Extend by parent-child relations
        graph_view.extend({"type": "parent of"}, depth=1)
        
        # The child node should now be included
        included_nodes = [node.id for node in graph_view.get_nodes()]
        self.assertIn("child", included_nodes)

    def test_graphview_relations_are_iterable(self):
        """Test that GraphView.relations returns an iterable of Relation objects."""
        graph = Graph(id="root", type="root")
        node1 = Node(id="N1", type="node")
        node2 = Node(id="N2", type="node")
        graph.add_child(node1)
        graph.add_child(node2)
        graph.create_relation("N1", "N2", "depends on", tags=["dependency"])
        
        graph_view = GraphView(graph, include_all=True)
        
        relations = graph_view.relations
        self.assertIsNotNone(relations)
        
        relation_list = list(relations)
        self.assertEqual(len(relation_list), 1)
        
        rel = relation_list[0]
        # C4Formatter needs these attributes on relations
        self.assertTrue(hasattr(rel, "src"))
        self.assertTrue(hasattr(rel, "dst"))
        self.assertTrue(hasattr(rel, "type"))
        
    def test_graphview_roundtrip_with_c4formatter(self):
        """Test that GraphView can be formatted to PlantUML and the structure is correct."""
        graph = Graph(id="root", type="root", metadata={"title": "Architecture"})
        req1 = Requirement(id="R1", title="Requirement 1", description="Desc 1")
        req2 = Requirement(id="R2", title="Requirement 2", description="Desc 2")
        graph.add_child(req1)
        graph.add_child(req2)
        graph.create_relation("R1", "R2", "validates")
        
        graph_view = GraphView(graph, include_all=True)
        
        # Format to PlantUML
        plantuml = self.formatter.format(graph_view)
        
        # Verify structure
        self.assertIn("title Architecture", plantuml)
        self.assertIn("R1", plantuml)
        self.assertIn("R2", plantuml)
        self.assertIn("Requirement 1", plantuml)
        self.assertIn("Requirement 2", plantuml)
        self.assertIn("validates", plantuml)
        
    def test_graphview_empty_children(self):
        """Test that GraphView with no children works with C4Formatter."""
        graph = Graph(id="root", type="root")
        graph_view = GraphView(graph, include_all=True)
        
        # Should not raise an exception
        result = self.formatter.format(graph_view, include_header=False, include_footer=False)
        
        self.assertIsInstance(result, str)
        # Should only contain title, no children
        self.assertIn("title", result)
        
    def test_graphview_empty_relations(self):
        """Test that GraphView with no relations works with C4Formatter."""
        graph = Graph(id="root", type="root")
        node = Node(id="N1", type="node")
        graph.add_child(node)
        graph_view = GraphView(graph, include_all=True)
        
        # Should not raise an exception
        result = self.formatter.format(graph_view)
        
        self.assertIsInstance(result, str)
        self.assertIn("N1", result)
    
    def test_graphview_children_are_graphnodes(self):
        """Test that children returned by GraphView are GraphNode instances."""
        from arch_tool.view.graph_node import GraphNode
        
        graph = Graph(id="root", type="root")
        node1 = Node(id="N1", type="node")
        node2 = Node(id="N2", type="node")
        graph.add_child(node1)
        graph.add_child(node2)
        
        graph_view = GraphView(graph, include_all=True)
        
        children = list(graph_view.children)
        self.assertEqual(len(children), 2)
        
        for child in children:
            self.assertIsInstance(child, GraphNode)
    
    def test_graphview_graphnode_has_node_attributes(self):
        """Test that GraphNode proxies all Node attributes needed by C4Formatter."""
        graph = Graph(id="root", type="root")
        req = Requirement(
            id="REQ1",
            title="Test Requirement",
            description="Test Description",
            tags=["must", "security"],
            metadata={"priority": "high", "technology": "Python"}
        )
        graph.add_child(req)
        
        graph_view = GraphView(graph, include_all=True)
        children = list(graph_view.children)
        self.assertEqual(len(children), 1)
        
        graphnode = children[0]
        
        # Test all attributes that C4Formatter might access
        self.assertEqual(graphnode.id, "REQ1")
        self.assertEqual(graphnode.type, "requirement")
        self.assertEqual(graphnode.title, "Test Requirement")
        self.assertEqual(graphnode.description, "Test Description")
        # tags property is a generator, and order is not guaranteed (from a set)
        # so we convert to set for comparison
        self.assertEqual(set(graphnode.tags), {"must", "security", "requirement"})
        self.assertEqual(graphnode.metadata["priority"], "high")
        self.assertEqual(graphnode.metadata["technology"], "Python")
    
    def test_graphview_graphrelation_has_relation_attributes(self):
        """Test that GraphRelation proxies all Relation attributes needed by C4Formatter."""
        graph = Graph(id="root", type="root")
        node1 = Node(id="N1", type="node")
        node2 = Node(id="N2", type="node")
        graph.add_child(node1)
        graph.add_child(node2)
        
        # Create a Relation with metadata directly and add it to the graph
        from arch_tool import Relation
        rel = Relation(
            src="N1", dst="N2", type="depends on",
            description="Data flow",
            tags=["critical"],
            metadata={
                "technology": "REST",
                "direction": "right"
            }
        )
        graph.add_relation(rel)
        
        graph_view = GraphView(graph, include_all=True)
        relations = list(graph_view.relations)
        self.assertEqual(len(relations), 1)
        
        graph_rel = relations[0]
        
        # Test all attributes that C4Formatter might access
        self.assertEqual(graph_rel.src, "N1")
        self.assertEqual(graph_rel.dst, "N2")
        self.assertEqual(graph_rel.type, "depends on")
        self.assertEqual(graph_rel.tags, ["critical"])
        self.assertEqual(graph_rel.description, "Data flow")
        self.assertEqual(graph_rel.metadata["technology"], "REST")
        self.assertEqual(graph_rel.metadata["direction"], "right")
    
    def test_graphview_title_attribute_from_metadata(self):
        """Test that GraphView can access title from metadata."""
        from arch_tool.formatters.c4_formatter import get_attribute
        
        graph = Graph(id="root", type="root", metadata={"title": "Custom Title"})
        graph_view = GraphView(graph, include_all=True)
        
        # C4Formatter uses get_attribute to access title
        title = get_attribute(graph_view, "title")
        self.assertEqual(title, "Custom Title")
    
    def test_graphview_with_deeply_nested_children(self):
        """Test that GraphView preserves deeply nested structures for C4Formatter."""
        graph = Graph(id="root", type="root")
        
        # Create nested structure: root -> sys1 -> cont1 -> comp1 -> comp2
        sys1 = Container(id="sys1", type="container")
        cont1 = Container(id="cont1", type="container")
        comp1 = Component(id="comp1", title="Component 1", type="component")
        comp2 = Component(id="comp2", title="Component 2", type="component")
        
        comp1.add_child(comp2)
        cont1.add_child(comp1)
        sys1.add_child(cont1)
        graph.add_child(sys1)
        
        graph_view = GraphView(graph, include_all=True)
        
        # Format and verify all levels are present
        result = self.formatter.format(graph_view, include_header=False, include_footer=False)
        
        self.assertIn("sys1", result)
        self.assertIn("cont1", result)
        self.assertIn("comp1", result)
        self.assertIn("comp2", result)
        
        # Verify nested braces for containers with children
        self.assertIn("{", result)
        self.assertIn("}", result)
    
    def test_graphview_relations_with_all_optional_fields(self):
        """Test that GraphView relations support all optional C4 relation fields."""
        graph = Graph(id="root", type="root")
        node1 = Node(id="N1", type="node")
        node2 = Node(id="N2", type="node")
        graph.add_child(node1)
        graph.add_child(node2)
        
        # Create relation with all possible C4 fields using Relation constructor
        from arch_tool import Relation
        rel = Relation(
            src="N1", dst="N2", type="communicates",
            description="Sends data",
            tags=["async"],
            metadata={
                "technology": "HTTP/REST",
                "sprite": "arrow",
                "link": "http://example.com",
                "direction": "down"
            }
        )
        graph.add_relation(rel)
        
        graph_view = GraphView(graph, include_all=True)
        
        # Format should include all fields
        result = self.formatter.format(graph_view, include_header=False, include_footer=False)
        
        self.assertIn("communicates", result)
        # C4Formatter should handle all these fields
        formatted_correctly = (
            "N1" in result and
            "N2" in result and
            "communicates" in result
        )
        self.assertTrue(formatted_correctly)
    
    def test_graphview_filtered_view_formats_correctly(self):
        """Test that a filtered GraphView (not include_all) formats correctly."""
        graph = Graph(id="root", type="root", metadata={"title": "Filtered View"})
        node1 = Node(id="N1", type="node", metadata={"title": "Node 1"})
        node2 = Node(id="N2", type="node", metadata={"title": "Node 2"})
        node3 = Node(id="N3", type="node", metadata={"title": "Node 3"})
        graph.add_child(node1)
        graph.add_child(node2)
        graph.add_child(node3)
        graph.create_relation("N1", "N2", "depends on")
        graph.create_relation("N2", "N3", "uses")
        
        # Create filtered view with only N1 and N2
        graph_view = GraphView(graph, include_all=False)
        graph_view.include_nodes(["N1", "N2"])
        
        # Format should only include N1 and N2, not N3
        result = self.formatter.format(graph_view, include_header=False, include_footer=False)
        
        self.assertIn("N1", result)
        self.assertIn("N2", result)
        self.assertNotIn("N3", result)
    
    def test_graphview_extended_view_formats_correctly(self):
        """Test that an extended GraphView formats correctly with related nodes."""
        graph = Graph(id="root", type="root", metadata={"title": "Extended View"})
        req1 = Requirement(id="R1", title="Requirement 1")
        req2 = Requirement(id="R2", title="Requirement 2")
        comp1 = Component(id="C1", title="Component 1")
        
        graph.add_child(req1)
        graph.add_child(req2)
        graph.add_child(comp1)
        
        graph.create_relation("C1", "R1", "implements")
        graph.create_relation("R1", "R2", "depends on")
        
        # Create view starting with C1 and extend by "implements" relations
        # depth=1 means we process immediate neighbors that match the relation filter
        graph_view = GraphView(graph, include_all=False)
        graph_view.include_nodes("C1")
        graph_view.extend({"type": "implements"}, depth=1)
        
        # Format should include C1 and R1 (connected by "implements"), but not R2
        result = self.formatter.format(graph_view, include_header=False, include_footer=False)
        
        self.assertIn("C1", result)
        self.assertIn("R1", result)
        # R2 should NOT be included since it's not connected by "implements" relation
        self.assertNotIn("R2", result)
    
    def test_graphview_preserves_node_metadata_for_formatting(self):
        """Test that GraphView preserves all node metadata needed for C4 formatting."""
        graph = Graph(id="root", type="root")
        # Use Component which has a title property
        node = Component(
            id="N1",
            title="My Component",
            description="Does important things",
            type="component",
            metadata={
                "technology": "Python 3.11",
                "sprite": "gear",
                "link": "http://docs.example.com",
                "custom_field": "custom_value"
            },
            tags=["backend", "critical"]
        )
        graph.add_child(node)
        
        graph_view = GraphView(graph, include_all=True)
        
        # Get the child and verify all metadata is accessible
        children = list(graph_view.children)
        graphnode = children[0]
        
        self.assertEqual(graphnode.id, "N1")
        self.assertEqual(graphnode.type, "component")
        self.assertEqual(graphnode.title, "My Component")
        self.assertEqual(graphnode.description, "Does important things")
        self.assertEqual(graphnode.metadata["technology"], "Python 3.11")
        self.assertEqual(graphnode.metadata["sprite"], "gear")
        self.assertEqual(graphnode.metadata["link"], "http://docs.example.com")
        # Tags are in a set, so order is not guaranteed
        self.assertEqual(set(graphnode.tags), {"backend", "critical", "component"})
        self.assertEqual(graphnode.metadata["custom_field"], "custom_value")
        
        # Verify formatting works
        result = self.formatter.format(graph_view, include_header=False, include_footer=False)
        self.assertIn("N1", result)
        self.assertIn("My Component", result)
    
    def test_graphview_dump_to_file(self):
        """Test that GraphView can be dumped to a file using C4Formatter."""
        import tempfile
        import os
        
        graph = Graph(id="root", type="root", metadata={"title": "Test System"})
        req = Requirement(id="R1", title="Requirement", description="Test")
        graph.add_child(req)
        
        graph_view = GraphView(graph, include_all=True)
        
        # Test with text mode
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.puml') as f:
            temp_path = f.name
            self.formatter.dump(graph_view, f)
        
        try:
            with open(temp_path, 'r') as f:
                content = f.read()
            
            self.assertIn("@startuml", content)
            self.assertIn("@enduml", content)
            self.assertIn("title Test System", content)
            self.assertIn("R1", content)
        finally:
            os.unlink(temp_path)
    
    def test_graphview_iterating_children_multiple_times(self):
        """Test that GraphView.children can be iterated multiple times."""
        graph = Graph(id="root", type="root")
        node1 = Node(id="N1", type="node")
        node2 = Node(id="N2", type="node")
        graph.add_child(node1)
        graph.add_child(node2)
        
        graph_view = GraphView(graph, include_all=True)
        
        # First iteration
        children1 = list(graph_view.children)
        self.assertEqual(len(children1), 2)
        
        # Second iteration should work the same
        children2 = list(graph_view.children)
        self.assertEqual(len(children2), 2)
        
        # IDs should match
        ids1 = {c.id for c in children1}
        ids2 = {c.id for c in children2}
        self.assertEqual(ids1, ids2)
    
    def test_graphview_iterating_relations_multiple_times(self):
        """Test that GraphView.relations can be iterated multiple times."""
        graph = Graph(id="root", type="root")
        node1 = Node(id="N1", type="node")
        node2 = Node(id="N2", type="node")
        graph.add_child(node1)
        graph.add_child(node2)
        graph.create_relation("N1", "N2", "uses")
        
        graph_view = GraphView(graph, include_all=True)
        
        # First iteration
        relations1 = list(graph_view.relations)
        self.assertEqual(len(relations1), 1)
        
        # Second iteration should work the same
        relations2 = list(graph_view.relations)
        self.assertEqual(len(relations2), 1)
        
        # Relation types should match
        self.assertEqual(relations1[0].type, relations2[0].type)


class TestGraphViewFiltering(unittest.TestCase):
    """Test GraphView filtering methods: include_nodes, exclude_nodes, extend."""

    def setUp(self):
        """Set up a test graph with various nodes and relations."""
        self.graph = Graph(id="test_graph")
        
        # Create a hierarchy of components
        self.sys1 = System(id="sys1", title="System 1")
        self.sys2 = System(id="sys2", title="System 2")
        
        self.comp1 = Component(id="comp1", title="Component 1")
        self.comp2 = Component(id="comp2", title="Component 2")
        self.comp3 = Component(id="comp3", title="Component 3")
        
        self.sys1.add_child(self.comp1)
        self.sys1.add_child(self.comp2)
        self.sys2.add_child(self.comp3)
        
        self.graph.add_child(self.sys1)
        self.graph.add_child(self.sys2)
        
        # Create relations
        self.rel1 = self.graph.create_relation(
            from_id="comp1", to_id="comp2", type="depends_on"
        )
        self.rel2 = self.graph.create_relation(
            from_id="comp2", to_id="comp3", type="uses"
        )
        self.rel3 = self.graph.create_relation(
            from_id="comp1", to_id="comp3", type="calls"
        )

    def test_include_nodes_by_id_string(self):
        """Test including nodes by ID string."""
        view = GraphView(self.graph, include_all=False)
        view.include_nodes("comp1")
        
        nodes = list(view.get_nodes())
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].id, "comp1")

    def test_include_nodes_by_id_list(self):
        """Test including nodes by list of IDs."""
        view = GraphView(self.graph, include_all=False)
        view.include_nodes(["comp1", "comp2"])
        
        nodes = list(view.get_nodes())
        node_ids = {n.id for n in nodes}
        self.assertEqual(len(nodes), 2)
        self.assertIn("comp1", node_ids)
        self.assertIn("comp2", node_ids)

    def test_include_nodes_by_node_object(self):
        """Test including nodes by Node object."""
        view = GraphView(self.graph, include_all=False)
        view.include_nodes(self.comp1)
        
        nodes = list(view.get_nodes())
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].id, "comp1")

    def test_include_nodes_by_graphnode_object(self):
        """Test including nodes by GraphNode object."""
        view = GraphView(self.graph, include_all=True)
        comp1_node = view.get_node("comp1")
        
        view2 = GraphView(self.graph, include_all=False)
        view2.include_nodes(comp1_node)
        
        nodes = list(view2.get_nodes())
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].id, "comp1")

    def test_include_nodes_by_attribute_filter(self):
        """Test including nodes by attribute dictionary filter."""
        view = GraphView(self.graph, include_all=False)
        view.include_nodes({"type": "component"})
        
        nodes = list(view.get_nodes())
        self.assertEqual(len(nodes), 3)
        for node in nodes:
            self.assertEqual(node.type, "component")

    def test_include_nodes_by_callable_filter(self):
        """Test including nodes by callable filter function."""
        view = GraphView(self.graph, include_all=False)
        view.include_nodes(lambda n: n.id.startswith("comp"))
        
        nodes = list(view.get_nodes())
        self.assertEqual(len(nodes), 3)
        for node in nodes:
            self.assertTrue(node.id.startswith("comp"))

    def test_exclude_nodes_by_id_string(self):
        """Test excluding nodes by ID string."""
        view = GraphView(self.graph, include_all=True)
        view.exclude_nodes("comp1")
        
        nodes = list(view.get_nodes())
        node_ids = {n.id for n in nodes}
        self.assertNotIn("comp1", node_ids)
        self.assertIn("comp2", node_ids)
        self.assertIn("comp3", node_ids)

    def test_exclude_nodes_by_id_list(self):
        """Test excluding nodes by list of IDs."""
        view = GraphView(self.graph, include_all=True)
        view.exclude_nodes(["comp1", "comp2"])
        
        nodes = list(view.get_nodes())
        node_ids = {n.id for n in nodes}
        self.assertNotIn("comp1", node_ids)
        self.assertNotIn("comp2", node_ids)
        self.assertIn("comp3", node_ids)

    def test_exclude_nodes_by_attribute_filter(self):
        """Test excluding nodes by attribute dictionary filter."""
        view = GraphView(self.graph, include_all=True)
        view.exclude_nodes({"type": "Component"})
        
        nodes = list(view.get_nodes())
        for node in nodes:
            self.assertNotEqual(node.type, "Component")

    def test_exclude_nodes_by_callable_filter(self):
        """Test excluding nodes by callable filter function."""
        view = GraphView(self.graph, include_all=True)
        view.exclude_nodes(lambda n: n.id.startswith("comp"))
        
        nodes = list(view.get_nodes())
        for node in nodes:
            self.assertFalse(node.id.startswith("comp"))

    def test_include_exclude_combination(self):
        """Test combining include and exclude operations."""
        view = GraphView(self.graph, include_all=False)
        view.include_nodes({"type": "component"})  # Include all components
        view.exclude_nodes("comp2")  # Exclude comp2
        
        nodes = list(view.get_nodes())
        node_ids = {n.id for n in nodes}
        self.assertEqual(len(nodes), 2)
        self.assertIn("comp1", node_ids)
        self.assertNotIn("comp2", node_ids)
        self.assertIn("comp3", node_ids)

    def test_extend_depth_zero(self):
        """Test extend with depth=0 (no extension)."""
        view = GraphView(self.graph, include_all=False)
        view.include_nodes("comp1")
        
        initial_nodes = len(list(view.get_nodes()))
        view.extend({"type": "depends_on"}, depth=0)
        
        final_nodes = len(list(view.get_nodes()))
        self.assertEqual(initial_nodes, final_nodes)

    def test_extend_depth_one_outgoing(self):
        """Test extend with depth=1 following outgoing relations."""
        view = GraphView(self.graph, include_all=False)
        view.include_nodes("comp1")
        
        # comp1 -> comp2 (depends_on)
        view.extend({"type": "depends_on"}, depth=1)
        
        nodes = list(view.get_nodes())
        node_ids = {n.id for n in nodes}
        self.assertIn("comp1", node_ids)
        self.assertIn("comp2", node_ids)
        self.assertEqual(len(nodes), 2)

    def test_extend_depth_one_multiple_relations(self):
        """Test extend with depth=1 following multiple relation types."""
        view = GraphView(self.graph, include_all=False)
        view.include_nodes("comp1")
        
        # comp1 -> comp2 (depends_on), comp1 -> comp3 (calls)
        view.extend(lambda r: r.type in ["depends_on", "calls"], depth=1)
        
        nodes = list(view.get_nodes())
        node_ids = {n.id for n in nodes}
        self.assertIn("comp1", node_ids)
        self.assertIn("comp2", node_ids)
        self.assertIn("comp3", node_ids)
        self.assertEqual(len(nodes), 3)

    def test_extend_depth_two(self):
        """Test extend with depth=2 following chains of relations."""
        view = GraphView(self.graph, include_all=False)
        view.include_nodes("comp1")
        
        # comp1 -> comp2 -> comp3
        view.extend(lambda r: True, depth=2)
        
        nodes = list(view.get_nodes())
        node_ids = {n.id for n in nodes}
        self.assertIn("comp1", node_ids)
        self.assertIn("comp2", node_ids)
        self.assertIn("comp3", node_ids)

    def test_extend_with_node_filter(self):
        """Test extend with both relation and node filters."""
        view = GraphView(self.graph, include_all=False)
        view.include_nodes("comp1")
        
        # Only extend to nodes whose ID contains "2"
        view.extend(
            relation_filter=lambda r: True,
            node_filter=lambda n: "2" in n.id,
            depth=2
        )
        
        nodes = list(view.get_nodes())
        node_ids = {n.id for n in nodes}
        self.assertIn("comp1", node_ids)
        self.assertIn("comp2", node_ids)
        # comp3 should not be included even though reachable, because it doesn't match node filter
        self.assertNotIn("comp3", node_ids)

    def test_extend_includes_relations(self):
        """Test that extend includes the relations connecting extended nodes."""
        view = GraphView(self.graph, include_all=False)
        view.include_nodes("comp1")
        view.extend({"type": "depends_on"}, depth=1)
        
        relations = list(view.get_relations())
        self.assertEqual(len(relations), 1)
        self.assertEqual(relations[0].type, "depends_on")
        self.assertEqual(relations[0].src, "comp1")
        self.assertEqual(relations[0].dst, "comp2")

    def test_extend_bidirectional(self):
        """Test that extend works in both directions (predecessors and successors)."""
        view = GraphView(self.graph, include_all=False)
        view.include_nodes("comp2")
        
        # Should include comp1 (predecessor) and comp3 (successor)
        view.extend(lambda r: True, depth=1)
        
        nodes = list(view.get_nodes())
        node_ids = {n.id for n in nodes}
        self.assertIn("comp1", node_ids)  # predecessor
        self.assertIn("comp2", node_ids)  # original
        self.assertIn("comp3", node_ids)  # successor

    def test_extend_with_attribute_filter(self):
        """Test extend with attribute-based relation filter."""
        view = GraphView(self.graph, include_all=False)
        view.include_nodes("comp1")
        
        view.extend({"type": "calls"}, depth=1)
        
        nodes = list(view.get_nodes())
        node_ids = {n.id for n in nodes}
        self.assertIn("comp1", node_ids)
        self.assertIn("comp3", node_ids)
        self.assertNotIn("comp2", node_ids)  # Only connected via "depends_on"

    def test_extend_empty_graph(self):
        """Test extend on empty view does nothing."""
        view = GraphView(self.graph, include_all=False)
        
        view.extend(lambda r: True, depth=5)
        
        nodes = list(view.get_nodes())
        self.assertEqual(len(nodes), 0)

    def test_extend_no_matching_relations(self):
        """Test extend with filter that matches no relations."""
        view = GraphView(self.graph, include_all=False)
        view.include_nodes("comp1")
        
        view.extend({"type": "nonexistent_type"}, depth=5)
        
        nodes = list(view.get_nodes())
        self.assertEqual(len(nodes), 1)  # Only original node
        self.assertEqual(nodes[0].id, "comp1")


class TestGraphViewRealWorldScenario(unittest.TestCase):
    """Test GraphView with realistic scenarios similar to requirements mapping."""
    
    def setUp(self):
        """Set up a realistic graph structure with features and requirements."""
        self.graph = Graph(id="product_requirements", type="root")
        
        # Create a CPQ system with features
        cpq_system = Container(id="cpq_system", type="system")
        
        # Features (anonymized product features)
        quotation_feature = Component(id="quotation_tool", title="Quotation Tool", type="feature", tags=["standard"])
        pricing_feature = Component(id="pricing_engine", title="Pricing Engine", type="feature")
        config_frontend = Component(id="config_frontend", title="Configuration Frontend", type="feature")
        data_integration = Component(id="data_integration", title="System Integration", type="feature")
        
        cpq_system.add_child(quotation_feature)
        cpq_system.add_child(pricing_feature)
        cpq_system.add_child(config_frontend)
        cpq_system.add_child(data_integration)
        
        # Requirements (anonymized)
        req1 = Requirement(id="REQ-001", title="Modular Product Definition", description="System must support modular configuration")
        req2 = Requirement(id="REQ-002", title="Cost Management", description="Manage cost information from ERP")
        req3 = Requirement(id="REQ-003", title="Price Calculation", description="Calculate prices based on rules")
        req4 = Requirement(id="REQ-004", title="Target Cost Definition", description="Define target costs separately")
        req5 = Requirement(id="REQ-005", title="Component Maintenance", description="Maintain components in system")
        req6 = Requirement(id="REQ-006", title="User Interface", description="Intuitive user interface")
        req7 = Requirement(id="REQ-007", title="ERP Integration", description="Integration with ERP system")
        
        self.graph.add_child(cpq_system)
        self.graph.add_child(req1)
        self.graph.add_child(req2)
        self.graph.add_child(req3)
        self.graph.add_child(req4)
        self.graph.add_child(req5)
        self.graph.add_child(req6)
        self.graph.add_child(req7)
        
        # Create "delivered by" relations from requirements to features
        self.graph.create_relation("REQ-001", "quotation_tool", "delivered by")
        self.graph.create_relation("REQ-002", "quotation_tool", "delivered by")
        self.graph.create_relation("REQ-003", "pricing_engine", "delivered by")
        self.graph.create_relation("REQ-004", "pricing_engine", "delivered by")
        self.graph.create_relation("REQ-005", "quotation_tool", "delivered by")
        self.graph.create_relation("REQ-006", "config_frontend", "delivered by")
        self.graph.create_relation("REQ-007", "data_integration", "delivered by")
        
    def test_include_feature_and_extend_to_requirements(self):
        """Test starting from a feature and extending to all requirements it delivers."""
        graph_view = GraphView(self.graph, include_all=False, title="Feature Requirements Map")
        
        # Start with quotation_tool feature
        graph_view.include_nodes("quotation_tool")
        
        # Extend to all requirements connected by "delivered by" relation
        graph_view.extend({"type": "delivered by"}, {"type": "requirement"}, depth=1)
        
        # Verify the feature is included
        included_nodes = {node.id for node in graph_view.get_nodes()}
        self.assertIn("quotation_tool", included_nodes)
        
        # Verify all requirements delivered by quotation_tool are included
        self.assertIn("REQ-001", included_nodes)
        self.assertIn("REQ-002", included_nodes)
        self.assertIn("REQ-005", included_nodes)
        
        # Verify requirements NOT delivered by quotation_tool are excluded
        self.assertNotIn("REQ-003", included_nodes)
        self.assertNotIn("REQ-004", included_nodes)
        self.assertNotIn("REQ-006", included_nodes)
        self.assertNotIn("REQ-007", included_nodes)
        
        # Verify other features are excluded
        self.assertNotIn("pricing_engine", included_nodes)
        self.assertNotIn("config_frontend", included_nodes)
        self.assertNotIn("data_integration", included_nodes)
    
    def test_extend_with_node_type_filter(self):
        """Test extending with a node type filter to only include specific node types."""
        graph_view = GraphView(self.graph, include_all=False)
        
        # Start with quotation_tool
        graph_view.include_nodes("quotation_tool")
        
        # Extend by "delivered by" but only include nodes of type "requirement"
        graph_view.extend({"type": "delivered by"}, {"type": "requirement"}, depth=1)
        
        included_nodes = list(graph_view.get_nodes())
        
        # All included nodes (except the starting node) should be requirements
        for node in included_nodes:
            if node.id != "quotation_tool":
                self.assertEqual(node.type, "requirement")
    
    def test_extend_includes_relations(self):
        """Test that extending includes the matching relations."""
        graph_view = GraphView(self.graph, include_all=False)
        
        graph_view.include_nodes("quotation_tool")
        graph_view.extend({"type": "delivered by"}, {"type": "requirement"}, depth=1)
        
        # Get all relations in the view
        relations = list(graph_view.get_relations())
        
        # Should have 3 relations (REQ-001, REQ-002, REQ-005 -> quotation_tool)
        self.assertEqual(len(relations), 3)
        
        # All relations should be of type "delivered by"
        for rel in relations:
            self.assertEqual(rel.type, "delivered by")
        
        # All relations should have quotation_tool as destination
        for rel in relations:
            self.assertEqual(rel.dst, "quotation_tool")
    
    def test_multiple_features_extend(self):
        """Test extending from multiple features simultaneously."""
        graph_view = GraphView(self.graph, include_all=False)
        
        # Start with two features
        graph_view.include_nodes(["quotation_tool", "pricing_engine"])
        
        # Extend to requirements
        graph_view.extend({"type": "delivered by"}, {"type": "requirement"}, depth=1)
        
        included_nodes = {node.id for node in graph_view.get_nodes()}
        
        # Should include both starting features
        self.assertIn("quotation_tool", included_nodes)
        self.assertIn("pricing_engine", included_nodes)
        
        # Should include requirements for quotation_tool
        self.assertIn("REQ-001", included_nodes)
        self.assertIn("REQ-002", included_nodes)
        self.assertIn("REQ-005", included_nodes)
        
        # Should include requirements for pricing_engine
        self.assertIn("REQ-003", included_nodes)
        self.assertIn("REQ-004", included_nodes)
        
        # Should NOT include unrelated requirements
        self.assertNotIn("REQ-006", included_nodes)
        self.assertNotIn("REQ-007", included_nodes)
    
    def test_format_extended_view_with_c4formatter(self):
        """Test that extended GraphView can be formatted with C4Formatter."""
        formatter = C4Formatter(
            type_map={
                "requirement": "Container",
                "feature": "Component",
                "system": "System",
            },
            node_factory=Node.from_dict,
        )
        
        graph_view = GraphView(self.graph, include_all=False, title="Quotation Tool Requirements")
        graph_view.include_nodes("quotation_tool")
        graph_view.extend({"type": "delivered by"}, {"type": "requirement"}, depth=1)
        
        # Format the view
        result = formatter.format(graph_view, include_header=True, include_footer=True)
        
        # Verify output contains expected elements
        self.assertIn("@startuml", result)
        self.assertIn("@enduml", result)
        self.assertIn("title Quotation Tool Requirements", result)
        self.assertIn("quotation_tool", result)
        self.assertIn("REQ-001", result)
        self.assertIn("REQ-002", result)
        self.assertIn("REQ-005", result)
        
        # Verify relations are included
        self.assertIn("delivered by", result)
    
    def test_extend_depth_zero_includes_immediate_neighbors(self):
        """Test that depth=1 includes immediate neighbors, depth=0 does not extend."""
        # Test depth=0 (should not extend)
        graph_view_d0 = GraphView(self.graph, include_all=False)
        graph_view_d0.include_nodes("quotation_tool")
        graph_view_d0.extend({"type": "delivered by"}, {"type": "requirement"}, depth=0)
        
        included_d0 = {node.id for node in graph_view_d0.get_nodes()}
        # With depth=0, only the starting node should be included
        self.assertEqual(included_d0, {"quotation_tool"})
        
        # Test depth=1 (should include immediate neighbors)
        graph_view_d1 = GraphView(self.graph, include_all=False)
        graph_view_d1.include_nodes("quotation_tool")
        graph_view_d1.extend({"type": "delivered by"}, {"type": "requirement"}, depth=1)
        
        included_d1 = {node.id for node in graph_view_d1.get_nodes()}
        # With depth=1, should include quotation_tool and its connected requirements
        self.assertGreater(len(included_d1), 1)
        self.assertIn("quotation_tool", included_d1)
        self.assertIn("REQ-001", included_d1)
    
    def test_extend_without_node_filter_includes_all_connected_nodes(self):
        """Test extending without a node filter includes all connected nodes regardless of type."""
        graph_view = GraphView(self.graph, include_all=False)
        
        # Start with a requirement
        graph_view.include_nodes("REQ-001")
        
        # Extend by "delivered by" without node filter
        graph_view.extend({"type": "delivered by"}, depth=1)
        
        included_nodes = {node.id for node in graph_view.get_nodes()}
        
        # Should include the requirement
        self.assertIn("REQ-001", included_nodes)
        
        # Should include the feature it's delivered by
        self.assertIn("quotation_tool", included_nodes)
    
    def test_bidirectional_extend(self):
        """Test that extend works bidirectionally (both src and dst)."""
        graph_view = GraphView(self.graph, include_all=False)
        
        # Start with a requirement
        graph_view.include_nodes("REQ-001")
        
        # Extend to connected nodes (should find quotation_tool as destination)
        graph_view.extend({"type": "delivered by"}, depth=1)
        
        included_nodes = {node.id for node in graph_view.get_nodes()}
        
        # Should include both the requirement and the feature
        self.assertIn("REQ-001", included_nodes)
        self.assertIn("quotation_tool", included_nodes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
