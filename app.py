from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from main import (
    load_and_preprocess_data,
    extract_laptop_features,
    build_preprocessing_pipeline,
    perform_clustering,
    perform_pca,
    map_clusters_to_use_cases,
    recommend_laptops
)
import os

app = Flask(__name__, static_folder='static')
CORS(app)

# Preload and preprocess data once on startup
print("Loading and preprocessing data...")
df = load_and_preprocess_data()
df = extract_laptop_features(df)
nums = ['ram_gb', 'storage_capacity_gb', 'weight_kg']
cats = ['brand', 'processor', 'storage_type', 'graphics']
X, prep = build_preprocessing_pipeline(df, nums, cats)
df['cluster'] = perform_clustering(X)
pca_res = perform_pca(X, n_components=2)
df['pca1'], df['pca2'] = pca_res[:, 0], pca_res[:, 1]
df = map_clusters_to_use_cases(df)
print("✅ Data processing complete!")

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/recommend', methods=['GET'])
def recommend():
    use_case = request.args.get('use_case', default='budget', type=str)
    max_price = request.args.get('max_price', default=None, type=int)
    top_n = request.args.get('top_n', default=5, type=int)
    
    recs = recommend_laptops(use_case, df, top_n, max_price)
    if recs is None or recs.empty:
        return jsonify({"error": "No laptops found matching your criteria. Try increasing your budget or selecting a different use case."}), 404
    
    # Convert DataFrame to JSON-serializable format
    results = []
    for _, row in recs.iterrows():
        laptop = {
            'name': row['name'],
            'price': float(row['price']),
            'brand': row['brand'],
            'processor': row['processor'],
            'ram_gb': int(row['ram_gb']),
            'storage_capacity_gb': int(row['storage_capacity_gb']),
            'storage_type': row.get('storage_type', 'Unknown'),
            'graphics': row['graphics'],
            'weight_kg': float(row['weight_kg']),
            'image_url': row.get('image_url', '/api/placeholder/300/200'),
            'product_url': row.get('product_url', '#'),
            'source': row.get('source', 'Unknown')
        }
        results.append(laptop)
    
    return jsonify(results)

@app.route('/usecases', methods=['GET'])
def get_use_cases():
    return jsonify(["budget", "programming", "design", "gaming", "portable", "all-purpose"])

@app.route('/api/placeholder/<width>/<height>')
def placeholder(width, height):
    # For demonstration, we'll redirect to a placeholder image service
    return f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" preserveAspectRatio="none"><rect width="100%" height="100%" fill="#777"/><text text-anchor="middle" x="50%" y="50%" fill="#555" dy=".3em">Image {width}x{height}</text></svg>'

if __name__ == '__main__':
    # Create static folder if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Save the HTML file to static folder
    with open('static/index.html', 'w') as f:
        f.write(open('index.html').read() if os.path.exists('index.html') else '')
    
    print("🚀 Server starting on http://localhost:5000")
    app.run(debug=True, port=5000)