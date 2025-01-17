import mysql.connector
import json
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Token
from sqlparse.tokens import Keyword, DML
import pandas as pd
import groqllm

# Database connection to global schema
global_conn = mysql.connector.connect(
    host='localhost',
    user='sqluser',
    password='password',
    database='global_schema',
    auth_plugin='mysql_native_password'
)
def connect_vendor_db(vendor_details):
    conn = mysql.connector.connect(
        host=vendor_details["ip"],
        user=vendor_details["user"],
        password=vendor_details["password"],
        database=vendor_details["db_name"],
        auth_plugin='mysql_native_password'
    )
    return conn

def fetch_schema_and_foreign_keys(conn,schema_name):
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

def global_query_results(query):
    try:
        global_conn.ping(reconnect=True)
        global_cursor = global_conn.cursor()
        global_cursor.execute(query)
        results = global_cursor.fetchall()
        global_cursor.close()
        return results
    except mysql.connector.Error as err:
        print(f"Error executing global query: {err}")
        print(f"Query that failed: {query}")
        return None

import mysql.connector
import json

import mysql.connector
import json

def vendor_query_results(transformed_query, details):
    """
    Executes a transformed SQL query on a vendor's database and fetches the results.
    
    Args:
        transformed_query (str): The SQL query to execute.
        details (dict): Dictionary containing vendor database connection details.

    Returns:
        list: List of tuples containing query results, or None if an error occurred.
    """
    try:
        # Sanitize the query (strip surrounding quotes if any)
        transformed_query = transformed_query.strip('"\'')

        # Establish database connection
        vendor_conn = mysql.connector.connect(
            host=details['database_info']['ip'],
            user=details['database_info']['user'],
            password=details['database_info']['password'],
            database=details['database_info']['db_name'],
            auth_plugin='mysql_native_password'
        )
        vendor_cursor = vendor_conn.cursor()

        # Execute the transformed query
        print(f"Executing sanitized query: {transformed_query}")
        vendor_cursor.execute(transformed_query)
        print("Query executed successfully.")

        # Fetch and return all results
        results = vendor_cursor.fetchall()
        print(f"Fetched {len(results)} rows from {details['database_info']['db_name']}.")

        # Close cursor and connection
        vendor_cursor.close()
        vendor_conn.close()

        return results

    except mysql.connector.Error as err:
        print(f"Error while executing query: {err}")
        log_error_count(details['database_info']['db_name'])
        print(f"Query that failed: {transformed_query}")
        return None

def log_error_count(db_name):
    """
    Logs the error count for a database in a JSON file.
    
    Args:
        db_name (str): Name of the database where the error occurred.
    """
    try:
        # Load existing error log data
        with open('errorcountlog.json', 'r') as f:
            errorcountlog = json.load(f)
    except FileNotFoundError:
        print("Error log file not found. Creating a new one.")
        errorcountlog = {}
    except json.JSONDecodeError:
        print("Invalid JSON format in error log file. Resetting log.")
        errorcountlog = {}

    # Update error count for the database
    if db_name in errorcountlog:
        errorcountlog[db_name] += 1
    else:
        errorcountlog[db_name] = 1

    # Save updated log to file
    with open('errorcountlog.json', 'w') as f:
        json.dump(errorcountlog, f, indent=4)

    print(f"Updated error count for database '{db_name}' in error log.")


def transform_sql_query(global_query, schema_mappings):
    """
    Transforms a global schema SQL query into a vendor-specific query using mappings,
    excluding columns mapped to null.
    
    Args:
        global_query (str): The query in the global schema.
        schema_mappings (dict): Mappings that include table and column mappings.
    
    Returns:
        str: Transformed query for the vendor schema.
    """
    import re

    # Extract mappings
    database_mapping = schema_mappings.get("database_mapping_global_schema", {})
    table_mappings = database_mapping.get("table_mappings", {})
    column_mappings = database_mapping.get("column_mappings", {})

    def replace_table_and_columns(match):
        """
        Replaces table and column names in the SQL query.
        If a column maps to null, it is removed from the query.
        
        Args:
            match (re.Match): The regex match object.
        
        Returns:
            str: Transformed table.column or column, or an empty string for null mappings.
        """
        full_identifier = match.group(0)  # Full match
        table = match.group(1)  # Table or alias (optional)
        column = match.group(2)  # Column name

        # Transform table and column using mappings
        actual_table = table_mappings.get(table, table) if table else None
        actual_column = (
            column_mappings.get(table, {}).get(column, column) if table else column
        )

        if actual_column is None:
            # Exclude columns mapped to null
            return ""

        if actual_table:
            return f"{actual_table}.{actual_column}"
        return f"{actual_column}"

    # Regex for identifying `table`.`column` or `column`
    regex = r"`?([a-zA-Z_][a-zA-Z0-9_]*)`?\.`?([a-zA-Z_][a-zA-Z0-9_]*)`?"


    # Replace table and column names in the query
    transformed_query = re.sub(regex, replace_table_and_columns, global_query)

    # Remove any dangling commas or invalid syntax
    transformed_query = re.sub(r",\s*,", ", ", transformed_query)  # Remove extra commas
    transformed_query = re.sub(r"\s*,\s*$", "", transformed_query)  # Remove trailing comma

    return transformed_query

def transformequeryllm(global_query,schema,foreign_keys ):
    # use llm to transform the query
    prompt=f"""
    given this query {global_query} and the schema {schema} and the foreign keys {foreign_keys} please tranfor, this to  a query that can be executed on the vendor database pleae output it in this fashion strictly without any explaination : "SELECT tablename.columnname FROM tablename joinfrom tablename joinfrom tablename WHERE tablename.attribute = value;"
    """
    print(prompt)
    return groqllm.generate_intelligent_query(prompt)

import pandas as pd
def clean_llm_query(llm_query):
    # Strip unnecessary whitespace and newline characters
    cleaned_query = llm_query.strip()
    
   
    cleaned_query = cleaned_query.replace("\\_", "_")
    
    # Ensure proper formatting (optional, depends on the LLM output specifics)
    cleaned_query = " ".join(cleaned_query.split())  # Remove excessive spaces
    
    return cleaned_query

def compare_results(global_results, vendor_results,global_schema_query):
    # Replace None with empty DataFrame if necessary
    if global_results is None:
        print("global_results is None. Setting size to 0.")
        global_results = pd.DataFrame()  # Create an empty DataFrame
    elif isinstance(global_results, list):
        global_results = pd.DataFrame(global_results)  # Convert list to DataFrame

    if vendor_results is None:
        print("vendor_results is None. Setting size to 0.")
        vendor_results = pd.DataFrame()  # Create an empty DataFrame
    elif isinstance(vendor_results, list):
        vendor_results = pd.DataFrame(vendor_results)  # Convert list to DataFrame

    # Get the number of rows
    no_rows = (len(global_results), len(vendor_results))
    
    # Ensure we access the DataFrame correctly for columns
    no_columns = (len(global_results.columns) if not global_results.empty else 0,
                  len(vendor_results.columns) if not vendor_results.empty else 0)

    # Get the first 7 rows
    global_results_head = global_results.head(7)
    vendor_results_head = vendor_results.head(7)
    
    prompt = f""" given the {global_schema_query}we generated two two queries and got the following results:Given the first 7 tuples for two outputs for the query according to some global schema, we got two results named as manual results and the LLM results {vendor_results_head} 
    and the metadata of the results is {no_rows} rows and {no_columns} columns in respective order. 
    Now please compare the results and tell which is better in just one word: manual or LLM. No other word  OR EXplaination allowed.
    """
    
    output = groqllm.generate_intelligent_query(prompt)
    print("Output of comparison:", output)
    return output
def fed_query(global_query):
    # Clean up the query
    global_query = ' '.join(global_query.split()).replace(' ,', ',')
    #print(f"Executing global query: {global_query}")
    
    # Step 1: Execute the global query
    global_results = global_query_results(global_query)
    # print("Global Results:", global_results)
    final_results = []
    final_results.append(global_results)
    
    
    if global_results:
        #try:
            # Load the schema_mappings.json file
            with open('schema_mappings.json') as f:
                schema_mappings = json.load(f)
                
                # Process each vendor schema
                for vendor_name, mapping in schema_mappings.items():
                    other_relevant_details = {
                        'database_info': mapping['database_info']
                        
                    }
                    
                    transformed_query = transform_sql_query(
                        global_query, 
                        mapping
                    )

                    print()
                    print("Transformed Query", transformed_query)
                    #get the connection to vendor database

                    vendor_conn = connect_vendor_db(mapping['database_info'])
                    #fetch schema and foreign keys
                    vschema, vforeign_keys = fetch_schema_and_foreign_keys(vendor_conn, mapping['database_info']['db_name'])
                    print("Vendor Schema:", vschema)
                    print("Vendor Foreign Keys:", vforeign_keys)
                    llm_query=transformequeryllm(global_query,vschema,vforeign_keys)
                
                    print(f"Transformed query for {vendor_name}:", transformed_query)
                    #clean the query
                    llm_query = clean_llm_query(llm_query)
                    
                    # Execute the transformed query
                    vendor_results = vendor_query_results(transformed_query, mapping)
                    #execute llm query
                    llm_results = vendor_query_results(llm_query, mapping)
                    # compare the results
                    if (not vendor_results) and (not llm_results):
                        print(f"No results found for {vendor_name}")
                        #increase the failed query count and later mark it for modification 
                        continue
                    else :
                        #comapre the results
                        comparison=compare_results(vendor_results,llm_results,global_query)
                        # 
                        if comparison=="llm":
                            final_results.append(llm_results)
                        else:
                            final_results.append(vendor_results)


                    
                  
            
            return final_results if final_results else None
            
    else:
        return None

def final_query_result(query):
    result = fedquerywithvendor(query)
    print("Final Results:", result)
    return result
def fedquerywithvendor(global_query):
    # Clean up the query
    global_query = ' '.join(global_query.split()).replace(' ,', ',')
    
    # Step 1: Execute the global query
    global_results = global_query_results(global_query)
    final_results = []
    
    # Add vendor name to each tuple in global results
    # if global_results:
    global_results_with_vendor = [tuple(list(result) + ["global_schema"]) for result in global_results]
    print("Global Results:", global_results_with_vendor)
    final_results.append(global_results_with_vendor)
    
    # Load the schema_mappings.json file
    with open('schema_mappings.json') as f:
        schema_mappings = json.load(f)
        
        # Process each vendor schema
        for vendor_name, mapping in schema_mappings.items():
            other_relevant_details = {
                'database_info': mapping['database_info']
            }
            
            transformed_query = transform_sql_query(
                global_query, 
                mapping
            )
            
            print("Transformed Query", transformed_query)
            #get the connection to vendor database
            vendor_conn = connect_vendor_db(mapping['database_info'])
            #fetch schema and foreign keys
            vschema, vforeign_keys = fetch_schema_and_foreign_keys(vendor_conn, mapping['database_info']['db_name'])
            
            llm_query=transformequeryllm(global_query,vschema,vforeign_keys)
            llm_query = clean_llm_query(llm_query)
            print("CLEANED LLM QUERY:", llm_query)
            print()
            vendor_results = vendor_query_results(transformed_query, mapping)
            #execute llm query
            llm_results = vendor_query_results(llm_query, mapping)
                # compare the results
            
            if (not vendor_results) and (not llm_results):
                print(f"No results found for {vendor_name}")
                continue
            else:
                # Compare the results
                comparison = compare_results(vendor_results, llm_results, global_query)
                
                # Add vendor name to each result tuple
                if comparison == "llm":
                    vendor_results_with_name = [tuple(list(result) + [vendor_name]) for result in llm_results]
                    final_results.append(vendor_results_with_name)
                else:
                    vendor_results_with_name = [tuple(list(result) + [vendor_name]) for result in vendor_results]
                    final_results.append(vendor_results_with_name)
        
    return final_results if final_results else None
   

# Example Execution
if __name__ == "__main__":
    sample_query = """
      SELECT Restaurant.Name, Dishes.Dishname, Dishes.price 
    FROM Restaurant 
    JOIN Dishes ON Restaurant.Restaurant_id = Dishes.restaurant_id 
    WHERE Restaurant.City = 'Gotham' AND Dishes.availability = 1;

    """


    results = fedquerywithvendor(sample_query)
    print("Final Results:", results)