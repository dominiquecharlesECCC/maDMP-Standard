import json
import networkx as nx

def create_network_from_schema(schema_path):
    # Read the JSON schema
    with open(schema_path, 'r') as f:
        schema = json.load(f)

    # Create a directed graph
    G = nx.DiGraph()
    
    def process_properties(properties, parent_name=None, path=""):
        for prop_name, prop_value in properties.items():
            current_path = f"{path}/{prop_name}".strip("/")
            
            # Create node attributes
            node_attrs = {
                "label": prop_name,
                "id": current_path
            }
            
            # Add dependency information if exists
            if current_path in schema.get("dependencies", {}):
                node_attrs["dependency"] = schema["dependencies"][current_path]
            
            # Add cardinality information if it's an array
            if isinstance(prop_value, dict) and prop_value.get("type") == "array":
                node_attrs["cardinality"] = "0..n"
                prop_value = prop_value.get("items", {})
            
            # Add node to graph
            G.add_node(current_path, **node_attrs)
            
            # Add edge from parent if exists
            if parent_name:
                G.add_edge(parent_name, current_path)
            
            # Process nested properties
            if isinstance(prop_value, dict) and "properties" in prop_value:
                process_properties(prop_value["properties"], current_path, current_path)

    # Start processing from root properties
    process_properties(schema["properties"])
    return G

def export_graph(G, output_base_path):
    # Export as GraphML
    nx.write_graphml(G, f"{output_base_path}.graphml")
    
    # Export as GML
    nx.write_gml(G, f"{output_base_path}.gml")
    
    print(f"Network has been exported as:")
    print(f"- {output_base_path}.graphml")
    print(f"- {output_base_path}.gml")

def main():
    # Generate network from light schema
    G = create_network_from_schema('light_schema.json')
    
    # Export in different formats
    export_graph(G, 'schema_network')

if __name__ == "__main__":
    main()