"""Unit tests for Relation class."""

import unittest
import sys
import os

# Add parent directory to path to import arch_tool
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from arch_tool.relation import Relation


class TestRelation(unittest.TestCase):
    """Test cases for the Relation class."""

    def test_relation_creation_minimal(self):
        """Test basic relation creation with minimal arguments."""
        rel = Relation(src="node1", dst="node2", type="depends on")
        self.assertEqual(rel.src, "node1")
        self.assertEqual(rel.dst, "node2")
        self.assertEqual(rel.type, "depends on")
        self.assertIsNone(rel.comment)
        self.assertEqual(rel.metadata, {})
        self.assertEqual(rel.tags, [])

    def test_relation_creation_with_comment(self):
        """Test relation creation with a comment."""
        rel = Relation(
            src="req1",
            dst="feature1",
            type="delivered by",
            comment="Feature implements this requirement"
        )
        self.assertEqual(rel.src, "req1")
        self.assertEqual(rel.dst, "feature1")
        self.assertEqual(rel.type, "delivered by")
        self.assertEqual(rel.comment, "Feature implements this requirement")

    def test_relation_creation_with_metadata(self):
        """Test relation creation with metadata."""
        metadata = {"priority": "high", "verified": True}
        rel = Relation(
            src="comp1",
            dst="comp2",
            type="communicates with",
            metadata=metadata
        )
        self.assertEqual(rel.metadata, metadata)
        # Verify metadata is a copy, not the same object
        metadata["new_key"] = "new_value"
        self.assertNotIn("new_key", rel.metadata)

    def test_relation_creation_with_tags(self):
        """Test relation creation with tags."""
        tags = ["critical", "network", "security"]
        rel = Relation(
            src="sys1",
            dst="sys2",
            type="impacts",
            tags=tags
        )
        self.assertEqual(rel.tags, tags)

    def test_relation_creation_with_all_parameters(self):
        """Test relation creation with all optional parameters."""
        metadata = {"weight": 0.8, "verified": False}
        tags = ["important", "async"]
        rel = Relation(
            src="service1",
            dst="service2",
            type="calls",
            comment="REST API call",
            metadata=metadata,
            tags=tags
        )
        self.assertEqual(rel.src, "service1")
        self.assertEqual(rel.dst, "service2")
        self.assertEqual(rel.type, "calls")
        self.assertEqual(rel.comment, "REST API call")
        self.assertEqual(rel.metadata, metadata)
        self.assertEqual(rel.tags, tags)

    def test_relation_src_immutable(self):
        """Test that source cannot be changed after creation."""
        rel = Relation(src="a", dst="b", type="relates to")
        with self.assertRaises(AttributeError):
            rel.src = "new_src"

    def test_relation_dst_immutable(self):
        """Test that destination cannot be changed after creation."""
        rel = Relation(src="a", dst="b", type="relates to")
        with self.assertRaises(AttributeError):
            rel.dst = "new_dst"

    def test_relation_type_immutable(self):
        """Test that type cannot be changed after creation."""
        rel = Relation(src="a", dst="b", type="relates to")
        with self.assertRaises(AttributeError):
            rel.type = "new_type"

    def test_relation_comment_mutable(self):
        """Test that comment can be changed after creation."""
        rel = Relation(src="a", dst="b", type="relates to", comment="initial")
        rel.comment = "updated comment"
        self.assertEqual(rel.comment, "updated comment")

    def test_relation_metadata_immutable(self):
        """Test that metadata property cannot be reassigned."""
        rel = Relation(src="a", dst="b", type="relates to", metadata={"key": "value"})
        with self.assertRaises(AttributeError):
            rel.metadata = {}

    def test_relation_metadata_contents_mutable(self):
        """Test that metadata contents can be modified."""
        rel = Relation(src="a", dst="b", type="relates to", metadata={"key": "value"})
        rel.metadata["new_key"] = "new_value"
        self.assertEqual(rel.metadata["new_key"], "new_value")
        self.assertEqual(rel.metadata["key"], "value")

    def test_relation_tags_immutable(self):
        """Test that tags property cannot be reassigned."""
        rel = Relation(src="a", dst="b", type="relates to", tags=["tag1"])
        with self.assertRaises(AttributeError):
            rel.tags = []

    def test_relation_tags_contents_mutable(self):
        """Test that tags list contents can be modified."""
        rel = Relation(src="a", dst="b", type="relates to", tags=["tag1"])
        rel.tags.append("tag2")
        self.assertEqual(len(rel.tags), 2)
        self.assertIn("tag1", rel.tags)
        self.assertIn("tag2", rel.tags)

    def test_relation_empty_metadata_by_default(self):
        """Test that metadata defaults to empty dict."""
        rel = Relation(src="a", dst="b", type="relates to")
        self.assertIsInstance(rel.metadata, dict)
        self.assertEqual(len(rel.metadata), 0)

    def test_relation_empty_tags_by_default(self):
        """Test that tags defaults to empty list."""
        rel = Relation(src="a", dst="b", type="relates to")
        self.assertIsInstance(rel.tags, list)
        self.assertEqual(len(rel.tags), 0)

    def test_relation_none_comment_by_default(self):
        """Test that comment defaults to None."""
        rel = Relation(src="a", dst="b", type="relates to")
        self.assertIsNone(rel.comment)

    def test_relation_with_empty_strings(self):
        """Test relation creation with empty strings."""
        rel = Relation(src="", dst="", type="")
        self.assertEqual(rel.src, "")
        self.assertEqual(rel.dst, "")
        self.assertEqual(rel.type, "")

    def test_relation_different_types(self):
        """Test various relationship types."""
        types = [
            "depends on",
            "delivered by",
            "impacts",
            "calls",
            "extends",
            "implements",
            "uses",
        ]
        for rel_type in types:
            rel = Relation(src="a", dst="b", type=rel_type)
            self.assertEqual(rel.type, rel_type)

    def test_relation_metadata_isolation(self):
        """Test that modifying original metadata dict doesn't affect relation."""
        original_metadata = {"key1": "value1"}
        rel = Relation(src="a", dst="b", type="relates to", metadata=original_metadata)
        
        # Modify original
        original_metadata["key2"] = "value2"
        original_metadata["key1"] = "changed"
        
        # Relation should have copy of original state
        self.assertEqual(rel.metadata, {"key1": "value1"})
        self.assertNotIn("key2", rel.metadata)

    def test_relation_tags_isolation(self):
        """Test that modifying original tags list doesn't affect relation."""
        original_tags = ["tag1", "tag2"]
        rel = Relation(src="a", dst="b", type="relates to", tags=original_tags)
        
        # Modify original
        original_tags.append("tag3")
        original_tags[0] = "changed"
        
        # Relation should have copy of original state
        self.assertEqual(rel.tags, ["tag1", "tag2"])

    def test_relation_with_special_characters(self):
        """Test relation with special characters in strings."""
        rel = Relation(
            src="node:123",
            dst="node/456",
            type="depends on",
            comment="Special chars: !@#$%^&*()",
            tags=["tag-1", "tag_2", "tag.3"]
        )
        self.assertEqual(rel.src, "node:123")
        self.assertEqual(rel.dst, "node/456")
        self.assertEqual(rel.comment, "Special chars: !@#$%^&*()")
        self.assertEqual(len(rel.tags), 3)

    def test_relation_bidirectional_different(self):
        """Test that relations are directional (a->b != b->a)."""
        rel1 = Relation(src="a", dst="b", type="depends on")
        rel2 = Relation(src="b", dst="a", type="depends on")
        
        # These should be different relations
        self.assertEqual(rel1.src, "a")
        self.assertEqual(rel1.dst, "b")
        self.assertEqual(rel2.src, "b")
        self.assertEqual(rel2.dst, "a")

    def test_relation_repr(self):
        """Test that relation has string representation."""
        rel = Relation(src="node1", dst="node2", type="depends on")
        repr_str = repr(rel)
        # Just verify it doesn't crash and returns a string
        self.assertIsInstance(repr_str, str)

    def test_relation_from_dict_single(self):
        """Test Relation.from_dict with single source and destination."""
        data = {
            "src": "node1",
            "dst": "node2",
            "type": "depends on",
            "comment": "A depends on B",
            "metadata": {"key": "value"},
            "tags": ["tag1"]
        }
        relations = list(Relation.from_dict(data))
        self.assertEqual(len(relations), 1)
        rel = relations[0]
        self.assertEqual(rel.src, "node1")
        self.assertEqual(rel.dst, "node2")
        self.assertEqual(rel.type, "depends on")
        self.assertEqual(rel.comment, "A depends on B")
        self.assertEqual(rel.metadata, {"key": "value"})
        self.assertEqual(rel.tags, ["tag1"])

    def test_relation_from_dict_multiple(self):
        """Test Relation.from_dict with multiple sources and destinations."""
        data = {
            "src": ["node1", "node2"],
            "dst": ["node3", "node4"],
            "type": "relates to"
        }
        relations = list(Relation.from_dict(data))
        self.assertEqual(len(relations), 4)  # 2 sources x 2 destinations
        expected_pairs = {
            ("node1", "node3"),
            ("node1", "node4"),
            ("node2", "node3"),
            ("node2", "node4"),
        }
        actual_pairs = {(rel.src, rel.dst) for rel in relations}
        self.assertEqual(actual_pairs, expected_pairs)  

if __name__ == "__main__":
    unittest.main(verbosity=2)
