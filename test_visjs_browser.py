"""
Test script to generate a vis.js visualization and open it in a browser.
"""

import sys
import os
import tempfile
import webbrowser

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from arch_tool import Node, Relation
from arch_tool.formatters.visjs_formatter import VisJSFormatter


def create_sample_graph():
    """Create a sample graph with nodes and relations."""
    # Create nodes
    system1 = Node(id="system1", type="system", metadata={"label": "Web Application"})
    system2 = Node(id="system2", type="system", metadata={"label": "Database"})
    system3 = Node(id="system3", type="system", metadata={"label": "API Gateway", "tooltip": "API Gateway to Web App"})
    
    component1 = Node(id="comp1", type="component", metadata={"label": "Frontend"})
    component2 = Node(id="comp2", type="component", metadata={"label": "Backend"})
    component3 = Node(id="comp3", type="component", metadata={"label": "Cache"})
    
    db1 = Node(id="db1", type="database", metadata={"label": "PostgreSQL"})
    db2 = Node(id="db2", type="database", metadata={"label": "Redis"})
    
    person = Node(id="user1", type="person", metadata={"label": "User", "link": "https://example.com"})
    
    # Create relations using node IDs
    rel1 = Relation(src="user1", dst="system3", type="uses", metadata={"label": "HTTP"})
    rel2 = Relation(src="system3", dst="system1", type="routes_to", metadata={"label": "forwards"})
    rel3 = Relation(src="system1", dst="system2", type="depends_on", metadata={"label": "queries"})
    rel4 = Relation(src="comp1", dst="comp2", type="calls", metadata={"label": "API"})
    rel5 = Relation(src="comp2", dst="db1", type="reads_from", metadata={"label": "SQL"})
    rel6 = Relation(src="comp2", dst="db2", type="reads_from", metadata={"label": "cache"})
    rel7 = Relation(src="comp3", dst="db2", type="manages", metadata={"label": "manages"})
    
    # Assign relations to nodes
    person.relations = [rel1]
    system3.relations = [rel2]
    system1.relations = [rel3]
    component1.relations = [rel4]
    component2.relations = [rel5, rel6]
    component3.relations = [rel7]
    
    # Add child nodes
    system1.children = [component1, component2, component3]
    system2.children = [db1, db2]
    
    return [person, system1, system2, system3]


def main():
    """Main function to create visualization and open in browser."""
    print("Creating sample graph...")
    nodes = create_sample_graph()
    
    print("Initializing VisJSFormatter...")
    formatter = VisJSFormatter(
        width="1200px",
        height="800px",
        layout={
            "improvedLayout": True,
        },
        physics={
            "enabled": True,
            "barnesHut": {
                "springLength": 200,
                "springConstant": 0.05,
                "damping": 0.09
            },
            "solver": "barnesHut"
        }
    )
    formatter.clear_cache()
    
    print("Generating HTML...")
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        temp_path = f.name
        print(f"Temporary file: {temp_path}")
    
    # Generate and save HTML
    formatter.format(nodes, file_name=temp_path)
    
    print("Opening in browser...")
    # Open in default browser
    webbrowser.open(f'file:///{temp_path.replace(os.sep, "/")}')
    
    print(f"\nVisualization opened in browser!")
    print(f"Temporary file location: {temp_path}")
    print("Press Enter to exit and clean up the temporary file...")
    input()
    
    # Clean up
    try:
        os.unlink(temp_path)
        print("Temporary file cleaned up.")
    except Exception as e:
        print(f"Could not delete temporary file: {e}")


if __name__ == "__main__":
    main()
