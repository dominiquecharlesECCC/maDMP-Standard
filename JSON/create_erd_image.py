import json
import graphviz

def create_erd_from_schema(schema_path, output_path='schema_erd'):
    # Read the JSON schema
    with open(schema_path, 'r') as f:
        schema = json.load(f)

    # Create a new directed graph
    dot = graphviz.Digraph(comment='Schema ERD')
    dot.attr(rankdir='LR')  # Left to right layout
    
    # Set node styles
    dot.attr('node', shape='box', style='rounded')
    
    def process_properties(properties, parent_name=None, path=""):
        for prop_name, prop_value in properties.items():
            current_path = f"{path}/{prop_name}".strip("/")
            
            # Create node label
            node_label = f"{prop_name}"
            if current_path in schema.get("dependencies", {}):
                node_label += f"\n[depends on: {schema['dependencies'][current_path]}]"
            
            # Check if it's an array
            if isinstance(prop_value, dict) and prop_value.get("type") == "array":
                node_label += "\n[0..n]"
                prop_value = prop_value.get("items", {})
            
            # Create node
            dot.node(current_path, node_label)
            
            # Create edge from parent if exists
            if parent_name:
                dot.edge(parent_name, current_path)
            
            # Process nested properties
            if isinstance(prop_value, dict) and "properties" in prop_value:
                process_properties(prop_value["properties"], current_path, current_path)

    # Start processing from root properties
    process_properties(schema["properties"])

    # Save the diagram
    dot.render(output_path, format='png', cleanup=True)
    print(f"ERD has been generated as {output_path}.png")

# Generate ERD from the light schema
create_erd_from_schema('light_schema.json')