import mysql.connector
import json
import os
import google.generativeai as genai
# Configure API key for Generative AI
genai.configure(api_key="AIzaSyC4GdJWSMVUFKqP3eH4d-v-2TxDpTTCdzU")  

import re
global_schema="""
CREATE TABLE Restaurant (
    Restaurant_id  PRIMARY KEY,
    Name ,              
    Address ,City,              
    Zip,                
    Rating ,                   
    availability 
);
CREATE TABLE Dishes (
    dish_id PRIMARY KEY,
    Dishname,         
    price,                    
    restaurant_id , 
    rating,                  
    availability,
    about,
    FOREIGN KEY (restaurant_id) REFERENCES Restaurant(Restaurant_id) 
);


);"""

# Step 1: Connect to the global schema database
global_conn = mysql.connector.connect(
    host="localhost",
    user="sqluser",
    password="password",
    database="global_schema",
    auth_plugin='mysql_native_password'
)

# Fetch global schema and foreign keys
def fetch_schema_and_foreign_keys(conn, schema_name):
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    schema = {}
    for (table_name,) in tables:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = [row[0] for row in cursor.fetchall()]
        schema[table_name] = columns

    # Fetch foreign key relationships
    cursor.execute(
        "SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME "
        "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
        "WHERE CONSTRAINT_SCHEMA = %s AND REFERENCED_TABLE_NAME IS NOT NULL", (schema_name,)
    )
    foreign_keys = {}
    for table_name, column_name, ref_table_name, ref_column_name in cursor:
        if table_name not in foreign_keys:
            foreign_keys[table_name] = {}
        foreign_keys[table_name][column_name] = (ref_table_name, ref_column_name)
    
    return schema, foreign_keys

# Step 2: Get vendor database details
def get_vendor_details():
    vendor_db_name = "food_db"
    vendor_user = "aditya"
    vendor_password = "12345678"
    vendor_ip = "192.168.45.182"
    return {
        "db_name": vendor_db_name,
        "user": vendor_user,
        "password": vendor_password,
        "ip": vendor_ip
    }

# Step 3: Connect to the vendor database
def connect_vendor_db(vendor_details):
    conn = mysql.connector.connect(
        host=vendor_details["ip"],
        user=vendor_details["user"],
        password=vendor_details["password"],
        database=vendor_details["db_name"],
        auth_plugin='mysql_native_password'
    )
    return conn

def robust_json_parser(json_string):
    try:
        # Attempt direct parsing
        return json.loads(json_string)
    except json.JSONDecodeError:
        # Attempt to fix common JSON issues
        fixed_string = json_string.strip()
        fixed_string = re.sub(r',\s*([\]}])', r'\1', fixed_string)  # Remove trailing commas
        fixed_string = re.sub(r'(?<!")(\b\w+\b)(?=\s*:)', r'"\1"', fixed_string)  # Quote keys
        fixed_string = re.sub(r'(?<!\\)"(?=[^:{]*[:,])', r'\"', fixed_string)  # Escape quotes
        
        try:
            return json.loads(fixed_string)
        except json.JSONDecodeError as e:
           # print(f"Original string: {json_string}")
           # print(f"Fixed string: {fixed_string}")
            raise ValueError(f"Unable to parse JSON after fixes: {e}")


# Save schema mapping in the specified JSON format
MAPPING_FILE = 'schema_mappings.json'

def save_schema_mapping(vendor_details, imappings):
    database_name = vendor_details['db_name']
    # Prepare database information and mapping structure
    database_info = {
        "db_name": vendor_details["db_name"],
        "user": vendor_details["user"],
        "password": vendor_details["password"],
        "ip": vendor_details["ip"]
    }
    mappings=imappings.get("database_mapping_global_schema", {})
    mapping_data = {
        "database_info": database_info,
        "database_mapping_global_schema": {
            "table_mappings": mappings.get("table_mappings", {}),
            "column_mappings": mappings.get("column_mappings", {}),
            "foreign_keys": mappings.get("foreign_keys", {})
        }
    }

    # Check if the mapping file exists
    if not os.path.exists(MAPPING_FILE):
        # If the file doesn't exist, create it with the initial data
        with open(MAPPING_FILE, 'w') as file:
            json.dump({database_name: mapping_data}, file, indent=4)
    else:
        try:
            # Load existing data from the mapping file
            with open(MAPPING_FILE, 'r') as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = {}
            
            # Update or add the new database mapping
            existing_data[database_name] = mapping_data

            # Save the updated data back to the file
            with open(MAPPING_FILE, 'w') as file:
                json.dump(existing_data, file, indent=4)
        except Exception as e:
            print("Error saving schema mapping:", e)

    print(f"Schema mapping for '{database_name}' saved successfully.")


# Main function
def main():
    vendor_details = get_vendor_details()
    vendor_conn = connect_vendor_db(vendor_details)
    #fetch scxhema and foreign keys
    vschema, vforeign_keys = fetch_schema_and_foreign_keys(vendor_conn, vendor_details["db_name"])
    # ask for groq llm for schema mapping
    print("Global Schema:", vschema,vforeign_keys)
    prompt = """
    given the global schema {global_schema} and the schema of vendor that you need need to map  {vschema}  and the foreign keys in vendor schema {vforeign_keys}now generate the schema mapping where key is global schema table or column and value is the corresponding vendor schema table or column
    please output in the following format strictly WITHOUT any explaination OR ALTERNATE  and if there is no matching attribute map null in there please map all tables columns and foreign keys for in a way so that your response  can be decoded in json like the following
    {
        "database_mapping_global_schema": {
            "table_mappings": {
                "Restaurant": "restaurant",
                "Dishes": "dishes"
            },
            "column_mappings": {
                "Restaurant": {
                    "Restaurant_id": "restaurant_id",
                    "Name": "restaurant_name",
                    "Address": "restaurant_address",
                    "City": "city",
                    "Zip": null,
                    "Rating": "average_rating",
                    "availability": "is_available"
                },
                "Dishes": {
                    "dish_id": "dish_id",
                    "Dishname": "dish_name",
                    "price": "dish_price",
                    "restaurant_id": "associated_restaurant_id",
                    "rating": "dish_rating",
                    "availability": "is_available",
                    "about": null
                }
            },
            "foreign_keys": {
                "Dishes": {
                    "restaurant_id": "associated_restaurant_id"
                }
            }
        }
        
        
    }
}

    """
    model = genai.GenerativeModel('gemini-pro')

   
    #robustly convert the response from string to json
    response=model.generate_content(prompt)
    mapping = robust_json_parser(response.text)
    #print the json with proper indentation

    print(json.dumps(mapping, indent=4))
    print("do you approve of the schema mapping")
    x=input("tpye  0 for no ")
    if x=="0":
        print("please try another method")
        return
    save_schema_mapping(vendor_details, mapping)

    




if __name__ == "__main__":
    main()
