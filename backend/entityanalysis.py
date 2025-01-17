import os
import json
import pandas as pd
import re
from collections import defaultdict

# Step 1: Load metadata files
def load_metadata():
    # Load dish metadata
    with open('dishmeta.json', 'r', encoding='utf-8') as f:
        dish_meta = json.load(f)

    # Load restaurant metadata
    restaurants_df = pd.read_csv('Restaurant.csv', header=None, names=['Primary', 'Aliases'])
    restaurant_meta = {
        row['Primary'].strip().lower(): [alias.strip().lower() for alias in row['Aliases'].split(',')]
        for _, row in restaurants_df.iterrows()
    }

    # Load city metadata
    with open('citymeta.json', 'r', encoding='utf-8') as f:
        city_meta = json.load(f)

    return dish_meta, restaurant_meta, city_meta

# Step 2: Tokenize and preprocess text
def tokenize_text(text):
    text = re.sub(r'[^\w\s]', '', text)  # Remove special characters
    tokens = text.lower().split()  # Lowercase and split into words
    return tokens

# Step 3: Match tokens to metadata
def match_entities(tokens, dish_meta, restaurant_meta, city_meta):
    entities = defaultdict(lambda: None)

    # Match city
    for token in tokens:
        for city, aliases in city_meta.items():
            if token in aliases:
                entities['city'] = city
                break
        if entities['city']:
            break

    # Match restaurant
    for token in tokens:
        for restaurant, aliases in restaurant_meta.items():
            if token in aliases:
                entities['restaurant'] = restaurant
                break
        if entities['restaurant']:
            break

    # Match dish
    for token in tokens:
        for dish, aliases in dish_meta.items():
            if token in aliases:
                entities['dish'] = dish
                break
        if entities['dish']:
            break

    return dict(entities)

# Step 4: Process files in the directory
def process_documents(folder_path, dish_meta, restaurant_meta, city_meta):
    results = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                tokens = tokenize_text(text)
                entities = match_entities(tokens, dish_meta, restaurant_meta, city_meta)
                results.append({'file': filename, 'entities': entities})
    return results

# Step 5: Run the pipeline and display results
if __name__ == '__main__':
    # Load metadata
    dish_meta, restaurant_meta, city_meta = load_metadata()

    # Folder containing documents
    folder_path = 'weeklydocfolder'

    # Process documents
    results = process_documents(folder_path, dish_meta, restaurant_meta, city_meta)

    # Display results
    for result in results:
        print(f"File: {result['file']}")
        print(f"Extracted Entities: {result['entities']}")
        print("-" * 50)
