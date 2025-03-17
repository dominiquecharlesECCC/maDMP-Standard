import pandas as pd
import json
import urllib.parse

def build_nested_dict(keys, value):
    if len(keys) == 1:
        return {keys[0]: value}
    return {keys[0]: {"type": "object", "properties": build_nested_dict(keys[1:], value)}}

def merge_dicts(d1, d2):
    for key in d2:
        if key in d1 and isinstance(d1[key], dict) and isinstance(d2[key], dict):
            merge_dicts(d1[key], d2[key])
        else:
            d1[key] = d2[key]

# Load data from Google Sheets
google_sheet_id = '1OfY5dKEfbvFhlhBjRb4UfdPKqQiB9mjZwe_60R7mu-A'
worksheet_name = 'GC maDMP Master Sheet'
encoded_worksheet_name = urllib.parse.quote(worksheet_name)
url = f'https://docs.google.com/spreadsheets/d/{google_sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_worksheet_name}'
df = pd.read_csv(url, encoding='utf-8')

# Initialize schema
light_schema = {
    "type": "object",
    "properties": {},
    "required": ["dmp"]
}

# Track arrays and dependencies
array_fields = []
dependencies = {}

# Process each row
for _, row in df.iterrows():
    field_path = row['Common standard fieldname\n(click on blue hyperlinks for RDA core maDMP field descriptions)'].split('/')
    cardinality = str(row['Cardinality']).strip().lower()
    dependency = row['"required IF/WHEN" dependency']
    
    # Basic property object
    property_obj = {"type": "string"}
    
    # Handle cardinality
    if cardinality in ['0..n', '1..n']:
        array_fields.append("/".join(field_path))
        
    # Track dependencies
    if pd.notna(dependency):
        dependencies["/".join(field_path)] = dependency
        
    # Build nested structure
    nested_dict = build_nested_dict(field_path, property_obj)
    merge_dicts(light_schema["properties"], nested_dict)

# Apply array transformations
def apply_arrays(schema, path=""):
    if isinstance(schema, dict):
        for key, value in list(schema.items()):
            current_path = f"{path}/{key}".strip("/")
            if current_path in array_fields:
                schema[key] = {
                    "type": "array",
                    "items": value
                }
            if isinstance(value, dict):
                apply_arrays(value, current_path)

apply_arrays(light_schema)

# Add dependencies information
light_schema["dependencies"] = dependencies

# Save the schema
with open('light_schema.json', 'w', encoding='utf-8') as f:
    json.dump(light_schema, f, indent=2)

print("Light schema has been generated successfully!")