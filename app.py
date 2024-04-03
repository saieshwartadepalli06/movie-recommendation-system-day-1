from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast
import os

app = Flask(__name__)

# Load dataframes
df_cleaned = pd.read_csv('/workspaces/movie-recommendation-system-day-1/data/df_cleaned_use.csv')
df_images = pd.read_csv('/workspaces/movie-recommendation-system-day-1/data/combined_genres_df_until_2024_use.csv')

# Preprocessing
df_images.rename(columns={'title': 'Title'}, inplace=True)
df_images['imageURL'] = df_images['imageURL'].apply(ast.literal_eval).apply(lambda x: x.get('imageUrl') if x else None)
df_joined = pd.merge(df_cleaned, df_images[['Title', 'imageURL']], on='Title', how='left').drop_duplicates(subset='Title')

# Ensure all relevant columns are of type string
df_joined = df_joined.fillna('Unknown')  # Replace NaN with 'Unknown'
df_joined['combined_features'] = df_joined[['Star_1', 'Star_2', 'Star_3', 'Star_4', 'Director_Name']].agg(' '.join, axis=1)

# Generate cosine similarity matrix
count_vectorizer = CountVectorizer(stop_words='english')
count_matrix = count_vectorizer.fit_transform(df_joined['combined_features'])
cosine_sim = cosine_similarity(count_matrix)

def get_recommendations(title, cosine_sim=cosine_sim):
    df = df_joined.copy()
    df['Title'] = df['Title'].str.lower()  # Convert to lower case for case insensitive matching
    title = title.lower()  # Convert the search title to lower case as well

    if title not in df['Title'].values:
        return jsonify({"error": "Movie not found"}), 404

    idx = df.index[df['Title'] == title][0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    movie_indices = [i[0] for i in sim_scores[1:11]]

    return df.iloc[movie_indices].to_dict(orient='records')

@app.route('/')
def index():
    sample_movies = df_joined.sample(n=18).to_dict(orient='records')
    return render_template('/workspaces/movie-recommendation-system-day-1/templates/index.html', sample_movies=sample_movies)

@app.route('/recommend', methods=['GET'])
def recommend():
    title = request.args.get('title', '').strip()
    recommendations = get_recommendations(title)
    return render_template('/workspaces/movie-recommendation-system-day-1/templates/recommendations.html', recommendations=recommendations, title=title)

# This route is for your API endpoint that returns JSON
@app.route('/api/get-recommendations', methods=['GET'])
def get_recommendations_route():
    title = request.args.get('title', '').strip()
    recommendations = get_recommendations(title)
    return jsonify(recommendations)

if __name__ == '__main__':
    # Set debug to False when deploying to production
    app.run(debug=False)
