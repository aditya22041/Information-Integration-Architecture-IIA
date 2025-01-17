from tabulate import tabulate
import mysql.connector
import json
import re
import queryfed_json_files  # For using is_similar function
import queryfederator  # For using fed_query function


def get_dishes_by_restaurant_and_city(restaurant_name, city_name, vendor_name):
    # Load the restaurant names JSON
    with open("curr_restaurant_name.json", "r") as f:
        restaurant_names = json.load(f)

    # Load the city names JSON
    with open("curr_city_name.json", "r") as f:
        city_names = json.load(f)

    # Perform similarity check for restaurant names
    matched_restaurants = []
    for key, similar_words in restaurant_names.items():
        if queryfed_json_files.is_similar(restaurant_name, key):
            matched_restaurants.extend(restaurant_names[key])

    if not matched_restaurants:
        matched_restaurants = [restaurant_name]

    # Perform similarity check for city names
    matched_cities = []
    for key, similar_words in city_names.items():
        if queryfed_json_files.is_similar(city_name, key):
            matched_cities.extend(city_names[key])

    if not matched_cities:
        matched_cities = [city_name]

    # list of dictionaries to store final results
    final_results = []

    # Query for all matched restaurants and cities
    for restaurant in set(matched_restaurants):
        for city in set(matched_cities):
            query = f"""
                SELECT `Restaurant`.`Name` AS RestaurantName, `Restaurant`.`City`, 
                       `Dishes`.`Dishname`, `Dishes`.`price`, `Dishes`.`rating`, 
                       `Dishes`.`availability`
                FROM `Restaurant`
                JOIN `Dishes` ON `Restaurant`.`Restaurant_id` = `Dishes`.`restaurant_id`
                WHERE `Restaurant`.`Name` = '{restaurant}'
                  AND `Restaurant`.`City` = '{city}';
            """

            results = queryfederator.fedquerywithvendor(query)

            print("Results: ", results)

            # iterate over results and match vendor name to filter results
            for res in results:
                for row in res:
                    if row[-1] == vendor_name and row[5]:
                        final_results.append({
                            "RestaurantName": row[0],
                            "City": row[1],
                            "Dishname": row[2],
                            "Price": row[3],
                            "Rating": row[4],
                            "Availability": row[5]
                        })
    
    print(final_results)
    return final_results



# Example Usage
if __name__ == "__main__":
    get_dishes_by_restaurant_and_city("Pasta Palace", "rome", "local2")
