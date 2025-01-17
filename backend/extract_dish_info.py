from tabulate import tabulate
import mysql.connector
import json
import re
import queryfed_json_files  # For using is_similar function
import json

# Database connection to global schema
global_conn = mysql.connector.connect(
    host="localhost",
    user="sqluser",
    password="password",
    database="global_schema",
    auth_plugin="mysql_native_password",
)

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

def vendor_query_results(transformed_query, details):
    try:
        vendor_conn = mysql.connector.connect(
            host=details['database_info']['ip'],
            user=details['database_info']['user'],
            password=details['database_info']['password'],
            database=details['database_info']['db_name'],
            auth_plugin='mysql_native_password'
        )
        vendor_cursor = vendor_conn.cursor()
        vendor_cursor.execute(transformed_query)
        results = vendor_cursor.fetchall()
        vendor_cursor.close()
        vendor_conn.close()
        return results
    except mysql.connector.Error as err:
        print(f"Error executing vendor query: {err}")
        print(f"Query that failed: {transformed_query}")
        return None

def transform_sql_query(global_query, schema_mappings):
    database_mapping = schema_mappings.get("database_mapping_global_schema", {})
    table_mappings = database_mapping.get("table_mappings", {})
    column_mappings = database_mapping.get("column_mappings", {})

    def replace_table_and_columns(match):
        full_identifier = match.group(0)
        table = match.group(1)
        column = match.group(2)
        actual_table = table_mappings.get(table, table) if table else None
        actual_column = (
            column_mappings.get(table, {}).get(column, column) if table else column
        )
        if actual_column is None:
            return ""
        if actual_table:
            return f"`{actual_table}`.`{actual_column}`"
        return f"`{actual_column}`"

    regex = r"`?([a-zA-Z_][a-zA-Z0-9_]*)`?\.`?([a-zA-Z_][a-zA-Z0-9_]*)`?"
    transformed_query = re.sub(regex, replace_table_and_columns, global_query)
    transformed_query = re.sub(r",\s*,", ", ", transformed_query)
    transformed_query = re.sub(r"\s*,\s*$", "", transformed_query)

    return transformed_query

def fed_query(global_query):
    global_query = ' '.join(global_query.split()).replace(' ,', ',')
    global_results = global_query_results(global_query)
    final_results = []

    if global_results:
        final_results.extend([row + ("Global Schema",) for row in global_results])

    with open('schema_mappings.json') as f:
        schema_mappings = json.load(f)

        for vendor_name, mapping in schema_mappings.items():
            transformed_query = transform_sql_query(global_query, mapping)
            vendor_results = vendor_query_results(transformed_query, mapping)
            if vendor_results:
                final_results.extend([row + (vendor_name,) for row in vendor_results])

    return final_results

def sort_and_print_dishes(dish_name, city_name, param=None, order="asc"):
    # Load the dish titles JSON
    with open("curr_dish_titles.json", "r") as f:
        dish_titles = json.load(f)

    # Load the city names JSON
    with open("curr_city_name.json", "r") as f:
        city_names = json.load(f)

    # Find matching dish names
    matched_dishes = []
    for key, similar_words in dish_titles.items():
        if queryfed_json_files.is_similar(dish_name, key):
            matched_dishes.append(key)

    # Collect all dish names to query
    dish_names_to_query = []
    for key in matched_dishes:
        dish_names_to_query.extend(dish_titles[key])

    if not dish_names_to_query:
        dish_names_to_query = [dish_name]

    # Find matching city names
    matched_cities = []
    for key, similar_words in city_names.items():
        if queryfed_json_files.is_similar(city_name, key):
            matched_cities.extend(city_names[key])

    if not matched_cities:
        matched_cities = [city_name]

    # Prepare final results
    json_results = []

    # Run queries for all dish and city combinations
    for dish in set(dish_names_to_query):
        for city in set(matched_cities):
            query = f"""
                SELECT `Restaurant`.`restaurant_id`, `Restaurant`.`Name`, `Restaurant`.`Address`, `Restaurant`.`City`, 
                       `Dishes`.`Dishname`, `Dishes`.`price`, `Dishes`.`rating`
                FROM `Restaurant` 
                JOIN `Dishes` ON `Restaurant`.`Restaurant_id` = `Dishes`.`restaurant_id`
                WHERE `Dishes`.`availability` = 1 AND `Dishes`.`Dishname` = '{dish}' AND `Restaurant`.`City` = '{city}';
            """
            results = fed_query(query)
            if not results:
                print(f"No results found for dish '{dish}' in city '{city}'")
                continue

            # Filter and sort results
            filtered_results = [
                {"vendor_name": row[-1], "restaurant_name": row[1], "dish_name": row[4], "price": row[5], "rating": row[6]}
                for row in results
            ]

            if param:
                is_descending = order == "desc"
                filtered_results.sort(key=lambda x: x["price"] if param == "price" else x["rating"], reverse=is_descending)

            # Add filtered results to JSON output
            json_results.extend(filtered_results)

            # Optionally print the table (debugging or visualization purposes)
            headers = ["Vendor Name", "Restaurant Name", "Dish Name", "Price", "Rating"]
            table_data = [[row["vendor_name"], row["restaurant_name"], row["dish_name"], row["price"], row["rating"]] for row in filtered_results]
            print(f"Results for Dish: {dish}, City: {city}")
            print(tabulate(table_data, headers=headers, tablefmt="grid"))

    return json_results

# Example Usage
if __name__ == "__main__":
    sort_and_print_dishes("matar panner", "Rme", param="Price", order="desc")
