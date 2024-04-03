from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast

app = Flask(__name__) 

# Load dataframes
df_cleaned = pd.read_csv('/Users/saieshwartadepalli/Downloads/Recommendation System/data/df_cleaned_use.csv')
df_images = pd.read_csv('/Users/saieshwartadepalli/Downloads/Recommendation System/data/combined_genres_df_until_2024_use.csv')

# Preprocessing
df_images.rename(columns={'title': 'Title'}, inplace=True)
df_images['imageURL'] = df_images['imageURL'].apply(lambda x: ast.literal_eval(x).get('imageUrl') if pd.notnull(x) else None)
df_joined = pd.merge(df_cleaned, df_images[['Title', 'imageURL']], on='Title', how='left')
df_joined.drop_duplicates(subset='Title', inplace=True)

# Ensure all relevant columns are of type string
for col in ['Star_1', 'Star_2', 'Star_3', 'Star_4', 'Director_Name']:
    df_joined[col] = df_joined[col].astype(str)

# Create the combined_features column
df_joined['combined_features'] = df_joined['Star_1'] + ' ' + df_joined['Star_2'] + ' ' + df_joined['Star_3'] + ' ' + df_joined['Star_4'] + ' ' + df_joined['Director_Name']
df_joined = pd.read_csv('/Users/saieshwartadepalli/Downloads/Recommendation System/data/df_joined_use.csv')

# Generate cosine similarity matrix
count_vectorizer = CountVectorizer(stop_words='english')
count_matrix = count_vectorizer.fit_transform(df_joined['combined_features'])
cosine_sim = cosine_similarity(count_matrix)

def get_recommendations(title, df=df_joined, cosine_sim=cosine_sim):
    filtered_df = df[df['Title'].str.contains(title, case=False, na=False)]
    if filtered_df.empty:
        return []  # Or return an appropriate response indicating no matches found
    
    idx = filtered_df.index[0]  # Proceed since we now know there is at least one match
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    movie_indices = [i[0] for i in sim_scores[1:19]]
    return df.iloc[movie_indices].to_dict(orient='records')

@app.route('/')
def index():
    sample_movies = df_joined.sample(n=18).to_dict(orient='records')
    return render_template('index.html', sample_movies=sample_movies)

@app.route('/recommend', methods=['GET'])
def recommend():
    title = request.args.get('title', '')
    recommendations = get_recommendations(title)
    return render_template('recommendations.html', recommendations=recommendations, title=title)

@app.route('/get-recommendations', methods=['GET'])
def get_recommendations_route():
    title = request.args.get('title')
    if not title:
        return jsonify({"error": "Missing title parameter"}), 400
    recommendations = get_recommendations(title)
    if recommendations:
        return jsonify(recommendations)
    else:
        return jsonify({"error": "No recommendations found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
