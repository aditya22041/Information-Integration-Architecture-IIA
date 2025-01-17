from tabulate import tabulate
import mysql.connector
import json
import queryfed_json_files
import queryfederator

# Database connection to global schema
global_conn = mysql.connector.connect(
    host="localhost",
    user="sqluser",
    password="password",
    database="global_schema",
    auth_plugin="mysql_native_password",
)


def get_similar_cities(city_name):
    """
    Retrieves a list of similar city names based on the input.
    """
    try:
        with open("curr_city_name.json", "r") as f:
            city_names = json.load(f)

        # Match similar cities
        matched_cities = []
        for key, similar_words in city_names.items():
            if queryfed_json_files.is_similar(city_name, key):
                matched_cities.extend(city_names[key])

        return matched_cities if matched_cities else [city_name]
    except FileNotFoundError:
        print("City names mapping file (curr_city_name.json) not found.")
        return [city_name]


def get_similar_restaurants(restaurant_name):
    """
    Retrieves a list of similar restaurant names based on the input.
    """
    try:
        with open("curr_restaurant_name.json", "r") as f:
            restaurant_names = json.load(f)

        # Match similar restaurant names
        matched_restaurants = []
        for key, similar_names in restaurant_names.items():
            if queryfed_json_files.is_similar(restaurant_name, key):
                matched_restaurants.extend(restaurant_names[key])

        return matched_restaurants if matched_restaurants else [restaurant_name]
    except FileNotFoundError:
        print("Restaurant names mapping file (curr_restaurant_name.json) not found.")
        return [restaurant_name]


def transform_results(raw_results):
    """
    Transforms raw database results into the desired JSON format, including vendor name.
    """
    transformed = []
    
    # Debug: Print raw results to see their structure
    print("Raw query results:", raw_results)

    for result in raw_results:
        if isinstance(result, tuple) and len(result) > 0:
            # The first element is the tuple
            row = result
            
            # Ensure it's a tuple and not a different data type
            if isinstance(row, tuple) and len(row) >= 7:
                restaurant = {
                    "name": row[1],
                    "city": row[3],
                    "rating": row[4],
                    "address": row[2],
                    "vendor_name": row[-1],  # Added vendor name to the JSON output.
                }
                transformed.append(restaurant)
            else:
                print("Unexpected row structure:", row)
        else:
            print("Unexpected result format:", result)

    return transformed


def print_table_for_query(query, city_name=None, restaurant_name=None):
    results = []

    if city_name and restaurant_name:
        # Get similar city names and restaurant names
        similar_cities = get_similar_cities(city_name)
        similar_restaurants = get_similar_restaurants(restaurant_name)

        for city in similar_cities:
            for restaurant in similar_restaurants:
                # Replace placeholders in the query with actual values
                modified_query = query.replace("{CITY_NAME}", city).replace("{RESTAURANT_NAME}", restaurant)
                query_results = queryfederator.fedquerywithvendor(modified_query)
                
                if query_results:
                    # Flatten nested lists into a single list
                    results.extend([item for sublist in query_results for item in sublist])

        if results:
            # Print results in tabular format
            headers = ["Restaurant ID", "Name", "Address", "City", "Rating", "Availability", "Vendor Name"]
            print(tabulate(results, headers=headers, tablefmt="pretty"))

            # Transform results into desired JSON format including vendor name
            transformed_results = transform_results(results)
            print(json.dumps(transformed_results, indent=4))
            return json.dumps(transformed_results, indent=4)

    # If no results are found
    print("No results found")
    return json.dumps({"message": "No results found"})


# Example Usage
if __name__ == "__main__":
    # Query to fetch restaurant information by city and restaurant name
    restaurant_query = """
         SELECT `Restaurant`.`restaurant_id`, `Restaurant`.`Name`, `Restaurant`.`Address`, `Restaurant`.`City`, 
           `Restaurant`.`Rating`, `Restaurant`.`availability`
            FROM `Restaurant`
            WHERE `Restaurant`.`City` = '{CITY_NAME}' AND `Restaurant`.`Name` = '{RESTAURANT_NAME}';
        """
    print_table_for_query(restaurant_query, city_name="New York", restaurant_name="Burger Hub")
