import mysql.connector
import json
import os
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np

# Load Sentence Transformer model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  

# Define global schema
global_schema = {
    "Restaurant": ["Restaurant_id", "Name", "Address", "City", "Zip", "Rating", "availability"],
    "Dishes": ["dish_id", "Dishname", "price", "restaurant_id", "rating", "availability", "about"]
}

# Connect to global schema database
def connect_global_db():
    return mysql.connector.connect(
        host="localhost",
        user="sqluser",
        password="password",
        database="global_schema",
        auth_plugin='mysql_native_password'
    )

# Fetch schema from the vendor database
def fetch_vendor_schema(connection):
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    schema = {}
    for table in tables:
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        columns = [column[0] for column in cursor.fetchall()]
        schema[table] = columns
    cursor.close()
    return schema

# Calculate similarity between two lists of names
def calculate_similarity(global_names, vendor_names):
    global_embeddings = model.encode(global_names)
    vendor_embeddings = model.encode(vendor_names)
    return cosine_similarity(global_embeddings, vendor_embeddings)

# Debugging similarity scores
def debug_similarity_scores(entity_type, global_names, vendor_names, similarity_matrix):
    print(f"\n*** Similarity Scores for {entity_type} ***")
    for i, global_name in enumerate(global_names):
        print(f"{global_name} ->")
        for j, vendor_name in enumerate(vendor_names):
            print(f"    {vendor_name}: {similarity_matrix[i][j]:.2f}")

# Fallback for direct string matching
def fallback_direct_match(global_name, vendor_names):
    for vendor_name in vendor_names:
        if global_name.lower().replace("_", "") == vendor_name.lower().replace("_", ""):
            return vendor_name
    return None

# Map foreign keys with similarity and fallback logic
def map_foreign_keys(global_table, global_relations, column_mappings, table_mappings):
    foreign_key_mappings = {}
    if global_table in global_relations:
        foreign_key_mappings[global_table] = {}
        for global_col, (ref_table, ref_col) in global_relations[global_table].items():
            vendor_ref_table = table_mappings.get(ref_table)
            vendor_ref_col = column_mappings.get(ref_table, {}).get(ref_col)
            
            if not vendor_ref_table or not vendor_ref_col:
                ref_table_options = list(table_mappings.values())
                if ref_table_options:
                    ref_table_similarities = calculate_similarity([ref_table], ref_table_options)
                    best_ref_table_index = np.argmax(ref_table_similarities[0])
                    vendor_ref_table = ref_table_options[best_ref_table_index]

                    ref_col_options = column_mappings.get(vendor_ref_table, {}).values()
                    if ref_col_options:
                        ref_col_similarities = calculate_similarity([ref_col], list(ref_col_options))
                        best_ref_col_index = np.argmax(ref_col_similarities[0])
                        vendor_ref_col = list(ref_col_options)[best_ref_col_index]

                        # Debug similarity scores
                        debug_similarity_scores("Tables", [ref_table], ref_table_options, ref_table_similarities)
                        debug_similarity_scores("Columns", [ref_col], list(ref_col_options), ref_col_similarities)

                        if ref_table_similarities[0][best_ref_table_index] < 0.4 or ref_col_similarities[0][best_ref_col_index] < 0.4:
                            vendor_ref_table = None
                            vendor_ref_col = None

                # Fallback direct match
                if not vendor_ref_table or not vendor_ref_col:
                    vendor_ref_table = fallback_direct_match(ref_table, ref_table_options)
                    vendor_ref_col = fallback_direct_match(ref_col, ref_col_options)

            foreign_key_mappings[global_table][global_col] = (
                f"{vendor_ref_table}.{vendor_ref_col}" if vendor_ref_table and vendor_ref_col else None
            )
    return foreign_key_mappings

# Match schemas and foreign keys
def match_schemas(global_schema, vendor_schema, global_relations):
    table_mappings = {}
    column_mappings = {}

    # Map tables using semantic similarity
    global_tables = list(global_schema.keys())
    vendor_tables = list(vendor_schema.keys())
    table_similarity_matrix = calculate_similarity(global_tables, vendor_tables)
    
    for i, global_table in enumerate(global_tables):
        best_match_index = np.argmax(table_similarity_matrix[i])
        best_match_score = table_similarity_matrix[i][best_match_index]
        best_match_table = vendor_tables[best_match_index] if best_match_score > 0.4 else None
        table_mappings[global_table] = best_match_table

        # Map columns within matched tables
        global_columns = global_schema[global_table]
        column_mappings[global_table] = {}
        
        if best_match_table:
            vendor_columns = vendor_schema[best_match_table]
            column_similarity_matrix = calculate_similarity(global_columns, vendor_columns)

            for j, global_col in enumerate(global_columns):
                best_col_match_index = np.argmax(column_similarity_matrix[j])
                best_col_match_score = column_similarity_matrix[j][best_col_match_index]
                best_col_match = vendor_columns[best_col_match_index] if best_col_match_score > 0.4 else None
                column_mappings[global_table][global_col] = best_col_match
        else:
            for global_col in global_columns:
                column_mappings[global_table][global_col] = None

    # Map foreign keys
    foreign_keys = {}
    for global_table in global_schema:
        foreign_keys.update(map_foreign_keys(global_table, global_relations, column_mappings, table_mappings))

    return {
        "table_mappings": table_mappings,
        "column_mappings": column_mappings,
        "foreign_keys": foreign_keys
    }

# Save schema mapping
def save_schema_mapping(vendor_details, mappings, filename='schema_mappings.json'):
    mapping_data = {
        vendor_details['db_name']: {
            "database_info": vendor_details,
            "database_mapping_global_schema": mappings
        }
    }
    with open(filename, 'w') as file:
        json.dump(mapping_data, file, indent=4)
    print(f"Schema mapping saved to {filename}")

# Main function
def main():
    # Global database connection
    global_conn = connect_global_db()

    # Vendor database details
    vendor_details = {
        "db_name": "food_db",
        "user": "aditya",
        "password": "12345678",
        "ip": "192.168.45.182"
    }

    # Vendor database connection
    vendor_conn = mysql.connector.connect(
        host=vendor_details["ip"],
        user=vendor_details["user"],
        password=vendor_details["password"],
        database=vendor_details["db_name"],
        auth_plugin='mysql_native_password'
    )

    # Fetch vendor schema
    vendor_schema = fetch_vendor_schema(vendor_conn)

    # Define relationships
    global_relations = {
        "Dishes": {"restaurant_id": ("Restaurant", "Restaurant_id")}
    }

    # Match schemas
    mappings = match_schemas(global_schema, vendor_schema, global_relations)

    # Output schema mappings
    print("\n*** Schema Mapping ***")
    print(json.dumps(mappings, indent=4))

    # Save mappings
    save_choice = input("Save schema mapping? (yes/no): ").strip().lower()
    if save_choice == 'yes':
        save_schema_mapping(vendor_details, mappings)

if __name__ == "__main__":
    main()
