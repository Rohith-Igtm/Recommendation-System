# -*- coding: utf-8 -*-

import re
import pandas as pd
from pymongo import MongoClient
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv
load_dotenv()


def load_and_preprocess_data():
    """
    Load structured laptop data from MongoDB collections and perform basic preprocessing.
    Returns a cleaned DataFrame containing laptops.
    """
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client["product_scraper"]

    # Load Amazon and Flipkart data
    amazon_docs = list(db["Amazon_structured_products"].find())
    flipkart_docs = list(db["Flipkart_structured_products"].find())

    amazon_df = pd.DataFrame(amazon_docs)
    flipkart_df = pd.DataFrame(flipkart_docs)

    # Tag data source
    amazon_df['source'] = 'Amazon'
    flipkart_df['source'] = 'Flipkart'

    # Concatenate into one DataFrame
    combined_df = pd.concat([amazon_df, flipkart_df], ignore_index=True)

    # Drop MongoDB _id if present
    if '_id' in combined_df.columns:
        combined_df.drop('_id', axis=1, inplace=True)

    # Convert price to numeric and drop missing price entries
    combined_df['price'] = pd.to_numeric(combined_df['price'], errors='coerce')
    combined_df.dropna(subset=['price'], inplace=True)
    combined_df.fillna("N/A", inplace=True)

    # Determine the title field
    possible_title_fields = ['product_name', 'title', 'name']
    title_field = next((field for field in possible_title_fields if field in combined_df.columns), None)
    if not title_field:
        raise KeyError(f"❌ No title column found. Expected one of: {possible_title_fields}")

    # Filter for genuine laptops using keywords
    def is_valid_product(name):
        name = name.lower()
        include_keywords = [
            'laptop', 'notebook', 'macbook', 'chromebook',
            'i3', 'i5', 'i7', 'i9', 'ryzen', 'celeron',
            'pentium', 'intel', 'amd'
        ]
        exclude_keywords = [
            'stand', 'table', 'toy', 'educational', 'cooling pad',
            'sleeve', 'cover', 'bag', 'case', 'screen guard',
            'stylus', 'sticker', 'webcam', 'mouse', 'keyboard',
            'adapter', 'charger', 'dock', 'enclosure'
        ]
        return any(k in name for k in include_keywords) and not any(k in name for k in exclude_keywords)

    combined_df = combined_df[combined_df[title_field].apply(is_valid_product)]
    combined_df.reset_index(drop=True, inplace=True)

    print(f"✅ Final filtered dataset: {len(combined_df)} laptop products.")
    return combined_df


def extract_laptop_features(df):
    """
    Extract key laptop features from text (from 'name' and 'description') using regex.
    Returns a DataFrame with new columns: brand, processor, ram_gb, storage_capacity_gb,
    storage_type, graphics, weight_kg.
    """
    def extract_storage_capacity(text):
        matches = re.findall(r'(\d+)\s?(GB|TB)', text, re.IGNORECASE)
        capacity = 0
        for value, unit in matches:
            value = int(value)
            if unit.lower() == 'tb':
                capacity = value * 1024  # Convert TB to GB
            elif unit.lower() == 'gb':
                capacity = max(capacity, value)
        return capacity
    
    def enrich_frontend_fields(df):
        df['description_keys'] = df['description'].apply(lambda x: list(x.keys()) if isinstance(x, dict) else [])
        df['image_url'] = df['image_url']
        df['product_url'] = df['product_url']
        df['star_ratings'] = df['star_ratings']
        return df

    def detect_storage_type(text, capacity):
        text_lower = text.lower()
        if 'ssd' in text_lower and 'hdd' in text_lower:
            return 'Hybrid'
        elif 'ssd' in text_lower:
            return 'SSD'
        elif 'hdd' in text_lower:
            return 'HDD'
        else:
            # Use capacity as a proxy if no explicit mention
            if 0 < capacity <= 1024:
                return 'SSD'
            elif capacity > 1024:
                return 'HDD'
            else:
                return 'N/A'

    def extract_weight(text):
        text = text.lower()
        # Search for explicit weight mention
        match = re.search(r'(?:weight|wt)[:\s]*(\d+(?:\.\d+)?)\s*(kg|g)\b', text, re.IGNORECASE)
        if not match:
            # Fallback pattern
            match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|g)\b', text, re.IGNORECASE)
            if not match:
                return None
        weight_value = float(match.group(1))
        unit = match.group(2).lower()
        if unit == 'g':
            weight_value /= 1000.0
        # Validate realistic laptop weight range
        if 0.3 <= weight_value <= 10:
            return round(weight_value, 2)
        return None

    def extract_processor(text):
        matches = re.findall(r'\b(i[3579]|ryzen\s?\d|celeron|pentium|athlon silver|mediatek|'
                             r'snapdragon|m[12-9](?:\s?(pro|max|ultra))?)\b', text)
        if matches:
            return matches[0][0] if isinstance(matches[0], tuple) else matches[0]
        return 'unknown'

    def extract_ram(text):
        matches = re.findall(r'(\d{1,3})\s?gb\s?(?:ram|ddr\d|memory)?', text)
        return int(matches[0]) if matches else 0

    def extract_graphics(text):
        if any(keyword in text.lower() for keyword in ['nvidia', 'geforce', 'gtx', 'rtx', 'radeon']):
            return 'dedicated'
        return 'integrated'

    def extract_specs(text):
        text = str(text).lower()
        brand_matches = re.findall(
            r'\b(asus|hp|dell|lenovo|acer|msi|apple|honor|infinix|realme|lg|samsung|jiobook)\b', text
        )
        specs = {
            'brand': brand_matches[0] if brand_matches else 'unknown',
            'processor': extract_processor(text),
            'ram_gb': extract_ram(text),
            'storage_capacity_gb': extract_storage_capacity(text),
            'storage_type': None,   # To be determined below
            'graphics': extract_graphics(text),
            'weight_kg': None       # To be determined below
        }
        specs['storage_type'] = detect_storage_type(text, specs['storage_capacity_gb'])
        weight = extract_weight(text)
        specs['weight_kg'] = weight if weight is not None else 1.7  # default average weight
        return pd.Series(specs)

    # Ensure text columns are valid strings
    df['name'] = df['name'].astype(str).fillna('')
    df['description'] = df['description'].astype(str).fillna('')
    combined_text = df['name'] + ' ' + df['description']
    df[['brand', 'processor', 'ram_gb', 'storage_capacity_gb', 'storage_type', 'graphics', 'weight_kg']] = combined_text.apply(extract_specs)
    
    return df


def build_preprocessing_pipeline(df, features, categorical):
    """
    Build and fit a ColumnTransformer preprocessing pipeline for the numeric and categorical features.
    Returns the transformed feature matrix.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical)
        ]
    )
    X = df[features + categorical]
    return preprocessor.fit_transform(X), preprocessor


def perform_clustering(X_preprocessed, n_clusters=5):
    """
    Apply KMeans clustering to the preprocessed data.
    Returns the cluster labels.
    """
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X_preprocessed)
    return clusters


def perform_pca(X_preprocessed, n_components=2):
    """
    Apply PCA for dimension reduction to allow 2D visualization.
    Returns the PCA results.
    """
    pca = PCA(n_components=n_components)
    return pca.fit_transform(X_preprocessed.toarray())


def map_clusters_to_use_cases(df):
    """
    Map the cluster labels to human-readable use-case labels.
    """
    cluster_labels = {
        0: "High-End Productivity",
        1: "Mid-Range Balanced",
        2: "Budget",
        3: "High-Performance/Gaming",
        4: "Outlier"
    }
    df['use_case'] = df['cluster'].map(cluster_labels)
    return df


def recommend_laptops(use_case, df, top_n=5, max_price=None):
    """
    Recommend laptops based on the given use-case and optional price filter.
    The use-case is mapped to a cluster id.
    """
    # Refined mapping of use-case (desired recommendations) to cluster IDs
    cluster_map = {
        "budget": 2,
        "programming": 1,
        "design": 0,
        "gaming": 4,
        "portable": 3,
        "all-purpose": 1
    }
    use_case = use_case.lower()
    if use_case not in cluster_map:
        print("Invalid use-case. Valid options: budget, programming, design, gaming, portable, all-purpose")
        return None
    
    cluster_id = cluster_map[use_case]
    recs = df[df['cluster'] == cluster_id]
    
    if max_price is not None:
        recs = recs[recs['price'] <= max_price]
    
    # Add description features extraction
    recs = recs.copy()

    recs_sorted = recs.sort_values(by='price').head(top_n)
    
    return recs_sorted[[
        'name', 'price','brand', 'processor', 'ram_gb', 
        'graphics', 'storage_capacity_gb','storage_type', 'weight_kg','source','image_url', 'product_url'
    ]]


# def plot_clusters(df):
#     """
#     Plot the clusters using PCA-reduced features and use-case labels.
#     """
#     plt.figure(figsize=(10, 6))
#     sns.scatterplot(data=df, x='pca1', y='pca2', hue='use_case', palette='Set2',
#                     s=100, edgecolor="k")
#     plt.title("Laptop Clusters - PCA Visualization with Use-Case Labels")
#     plt.xlabel("Principal Component 1")
#     plt.ylabel("Principal Component 2")
#     plt.legend(title="Use Case", loc="best")
#     plt.show()


# Main script execution
if __name__ == '__main__':
    
    # Load and process data
    df = load_and_preprocess_data()
    df = extract_laptop_features(df)
    
    # Define features for ML pipeline
    numeric_features = ['ram_gb', 'storage_capacity_gb', 'weight_kg']
    categorical_features = ['brand', 'processor', 'storage_type', 'graphics']
    
    X_preprocessed, preprocessor = build_preprocessing_pipeline(df, numeric_features, categorical_features)
    print("Preprocessed feature shape:", X_preprocessed.shape)
    
    # Perform clustering
    df['cluster'] = perform_clustering(X_preprocessed, n_clusters=5)
    print("Cluster counts:")
    print(df['cluster'].value_counts())
    
    # Perform PCA and add results to DataFrame for visualization
    # pca_result = perform_pca(X_preprocessed, n_components=2)
    # df['pca1'] = pca_result[:, 0]
    # df['pca2'] = pca_result[:, 1]
    
    # Map clusters to use-case labels and plot
    df = map_clusters_to_use_cases(df)
    print(df[['name', 'price', 'cluster', 'use_case']].head(10))
    print("\nUse-case counts:")
    print(df['use_case'].value_counts())
    # plot_clusters(df)
    
    # Test the recommendation function
    usecase="design"
    recs = recommend_laptops(usecase, df, top_n=10, max_price=30000)
    print(f"\nRecommended Laptops for {usecase} Use-Case:")
    
    print(recs)