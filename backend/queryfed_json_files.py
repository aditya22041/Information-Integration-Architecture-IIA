import pymysql
import json
import fuzzy
import jellyfish
import queryfederator

# Functions for loading and saving dictionaries
def load_dict(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_dict(data, filename):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Saved data to {filename}")
    except Exception as e:
        print(f"Error saving data to {filename}: {e}")


# Initialize dictionaries
food_dict = load_dict(r'C:\Users\WASIF\OneDrive\Desktop\IIA\backend\backend\curr_dish_titles.json')
city_dict = load_dict(r'C:\Users\WASIF\OneDrive\Desktop\IIA\backend\backend\curr_city_name.json')
restaurant_dict = load_dict(r'C:\Users\WASIF\OneDrive\Desktop\IIA\backend\backend\curr_restaurant_name.json')

# Database connection setup
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='sqluser',
        password='password',
        database='global_schema',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# String similarity methods
def soundex(word):
    soundex_code = fuzzy.Soundex(4)  # Default length is 4
    return soundex_code(word)

def jaro_winkler_similarity(word1, word2):
    return jellyfish.jaro_winkler_similarity(word1, word2)

def levenshtein_distance(word1, word2):
    return jellyfish.levenshtein_distance(word1, word2)

def is_similar(title1, title2):
    # Check Soundex match
    if soundex(title1) == soundex(title2):
        return True
    # Check Jaro-Winkler similarity (threshold can be adjusted)
    elif jaro_winkler_similarity(title1, title2) >= 0.85:
        return True
    # Check Levenshtein distance (threshold set to 3; can be adjusted)
    elif levenshtein_distance(title1, title2) <= 3:
        return True
    return False

# Add to dictionary with similarity check
def add_to_dict(item, target_dict):
    for key, similar_items in target_dict.items():
        if is_similar(item, key):
            if item not in similar_items:
                similar_items.append(item)
            return
    target_dict[item] = [item]

# Process data for food titles, city names, and restaurant names
def process_data():
    connection = get_db_connection()
    try:
        # Fetch food data
        new_food_items_data = queryfederator.final_query_result("SELECT DISTINCT `Dishes`.`Dishname` FROM `Dishes`")
        for group in new_food_items_data:
            for dish in group:
                food_title = dish[0]  # Extract the actual dish name
                add_to_dict(food_title, food_dict)

        # Fetch city data
        new_city_names_data = queryfederator.final_query_result("SELECT DISTINCT `Restaurant`.`City` FROM `Restaurant`")
        for group in new_city_names_data:
            for city in group:
                city_name = city[0]  # Extract the actual city name
                add_to_dict(city_name, city_dict)

        # Fetch restaurant data
        new_restaurant_names_data = queryfederator.final_query_result("SELECT DISTINCT `Restaurant`.`Name` FROM `Restaurant`")
        for group in new_restaurant_names_data:
            for restaurant in group:
                restaurant_name = restaurant[0]  # Extract the actual restaurant name
                add_to_dict(restaurant_name, restaurant_dict)

    finally:
        connection.close()

# Run the function to process data
process_data()

# Save the updated dictionaries back to JSON files
save_dict(food_dict, r'C:\Users\WASIF\OneDrive\Desktop\IIA\backend\backend\curr_dish_titles.json')
save_dict(city_dict, r'C:\Users\WASIF\OneDrive\Desktop\IIA\backend\backend\curr_city_name.json')
save_dict(restaurant_dict, r'C:\Users\WASIF\OneDrive\Desktop\IIA\backend\backend\curr_restaurant_name.json')

# # Print the updated dictionaries
# print("Updated food dictionary:")
# for key, titles in food_dict.items():
#     print(f"{key}: {titles}")

# print("\nUpdated city dictionary:")
# for key, names in city_dict.items():
#     print(f"{key}: {names}")

# print("\nUpdated restaurant dictionary:")
# for key, names in restaurant_dict.items():
#     print(f"{key}: {names}")
