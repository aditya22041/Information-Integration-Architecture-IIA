import torch
from sentence_transformers import SentenceTransformer, util
import csv
import json
import os

# Step 1: Load Metadata
def load_metadata(restaurant_csv, dish_json):
    restaurant_variants = []
    dish_variants = []
    
    with open(restaurant_csv, 'r', encoding='utf-8') as file:  # Specify UTF-8
        reader = csv.reader(file)
        for row in reader:
            restaurant_variants.extend([x.strip().lower() for x in row[0].split(',')])  # Adjust for single-column CSV
    
    with open(dish_json, 'r', encoding='utf-8') as file:  # Specify UTF-8
        dish_dict = json.load(file)
        for variations in dish_dict.values():
            dish_variants.extend([x.lower() for x in variations])
    
    return restaurant_variants, dish_variants

# Step 2: Perform Mean Pooling
def mean_pooling(embeddings):
    """
    Perform mean pooling on embeddings to get a single vector.
    Args:
        embeddings: A list of tensor embeddings to average.
    Returns:
        A single tensor representing the mean of all embeddings.
    """
    return torch.mean(torch.stack(embeddings), dim=0)

# Step 3: Generate Embeddings for Keywords
# Step 3: Generate Embeddings for Keywords
def generate_embeddings(model, keywords):
    """
    Generate a single mean-pooled embedding for a list of keywords.
    Args:
        model: The SentenceTransformer model.
        keywords: A list of keyword strings.
    Returns:
        A single tensor representing the mean-pooled embedding.
    """
    embeddings = model.encode(keywords, convert_to_tensor=True)  # Embedding shape: (n, d)
    return torch.mean(embeddings, dim=0)  # Compute mean along the batch dimension

# Step 4: Preprocess and Embed Text Files
def preprocess_and_embed_files(folder_path, model):
    file_embeddings = {}
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().lower()
            file_embeddings[file_name] = model.encode(content, convert_to_tensor=True)
    return file_embeddings

# Step 5: Find Relevant Files
def find_relevant_files(restaurant_embeddings, dish_embeddings, file_embeddings, threshold=0.3):
    relevant_files = []
    
    # Combine embeddings with mean pooling
    all_keywords_embeddings = mean_pooling([restaurant_embeddings, dish_embeddings])

    for file_name, file_embedding in file_embeddings.items():
        similarity = util.cos_sim(file_embedding, all_keywords_embeddings).item()
        if similarity >= threshold:
            relevant_files.append(file_name)
    
    return relevant_files

# Step 6: Main Process
def main():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)
    
    restaurant_csv = "Restaurant.csv"
    dish_json = "dishmeta.json"
    weeklydocfolder = "weeklydocfolder"
    
    # Load and Embed Keywords
    restaurant_variants, dish_variants = load_metadata(restaurant_csv, dish_json)
    restaurant_embeddings = generate_embeddings(model, restaurant_variants)
    dish_embeddings = generate_embeddings(model, dish_variants)
    
    # Embed Files
    file_embeddings = preprocess_and_embed_files(weeklydocfolder, model)
    
    # Find Relevant Files
    relevant_files = find_relevant_files(restaurant_embeddings, dish_embeddings, file_embeddings)
    
    print("Relevant Files:")
    print("\n".join(relevant_files))

# Run the main function
if __name__ == "__main__":
    main()
