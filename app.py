# from flask import Flask, render_template, request, send_from_directory
# import pandas as pd
# import os

# app = Flask(__name__)

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/recommend', methods=['POST'])
# def recommend():
#     user_preferences = request.form.get('preferences').split(',')
#     print("User preferences:", user_preferences)
#     articles = recommend_articles(user_preferences)
#     print("Recommended articles:", articles)
#     return render_template('recommendations.html', articles=articles)

# def recommend_articles(preferences):
#     df = pd.read_csv('processed_news.csv')
#     print("DataFrame loaded from CSV:\n", df.head())

#     def match_topic(row, preferences):
#         topic = row['topic']
#         for pref in preferences:
#             if pref.lower() == topic:
#                 return True
#         return False

#     recommendations = df[df.apply(lambda row: match_topic(row, preferences), axis=1)]
#     print("Recommendations DataFrame:\n", recommendations.head())

#     return recommendations.to_dict(orient='records')

# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template, request, send_from_directory
import pandas as pd
import os
import requests
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Initialize Flask app
app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Recommendation route
@app.route('/recommend', methods=['POST'])
def recommend():
    user_preferences = request.form.get('preferences').split(',')
    print("User preferences:", user_preferences)
    articles = recommend_articles(user_preferences)
    print("Recommended articles:", articles)
    return render_template('recommendations.html', articles=articles)

# Function to recommend articles based on user preferences
def recommend_articles(preferences):
    df = pd.read_csv('processed_news.csv')
    print("DataFrame loaded from CSV:\n", df.head())

    def match_topic(row, preferences):
        topic = row['topic']
        for pref in preferences:
            if pref.lower() == topic:
                return True
        return False

    recommendations = df[df.apply(lambda row: match_topic(row, preferences), axis=1)]
    print("Recommendations DataFrame:\n", recommendations.head())

    return recommendations.to_dict(orient='records')

# Route for favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

# Function to fetch news articles using NewsAPI
def fetch_news():
    API_KEY = 'ef8b3f9a030b4a4b9537a77c307a68bd'  
    BASE_URL = 'https://newsapi.org/v2/top-headlines'

    categories = ['technology', 'sports', 'business', 'entertainment', 'health', 'science', 'travel', 'finance']
    all_articles = []

    for category in categories:
        url = f'{BASE_URL}?country=us&category={category}&apiKey={API_KEY}'
        response = requests.get(url)
        if response.status_code == 200:
            news_data = response.json()
            if 'articles' in news_data:
                articles = news_data['articles']
                for article in articles:
                    article['category'] = category
                all_articles.extend(articles)
                print(f"Fetched {len(articles)} articles for category: {category}")
            else:
                print(f"Unexpected response structure for category {category}: {json.dumps(news_data, indent=4)}")
        else:
            print(f"Failed to fetch news data for category {category}. Status code: {response.status_code}, Response: {response.text}")

    with open('news_data.json', 'w') as json_file:
        json.dump({'articles': all_articles}, json_file)

    print(f"Total articles fetched: {len(all_articles)}")

# Function to process news data
def process_data():
    # Download NLTK resources
    nltk.download('stopwords')
    nltk.download('punkt')

    # Load data
    with open('news_data.json', 'r') as file:
        news_data = json.load(file)

    if 'articles' in news_data:
        articles = news_data['articles']
        df = pd.DataFrame(articles)
        df = df[['title', 'description', 'url', 'content', 'category']]
        print("Initial DataFrame:\n", df.head())

        # Preprocess content
        stop_words = set(stopwords.words('english'))

        def preprocess(text):
            if text:
                tokens = word_tokenize(text.lower())
                filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
                return filtered_tokens
            return []

        df['tokens'] = df['content'].apply(preprocess)
        print("DataFrame after tokenization:\n", df.head())

        # Define keyword-based topic categorization
        def categorize(row):
            category_keywords = {
                'technology': {'technology', 'ai', 'apple', 'google', 'microsoft', 'android', 'iphone', 'software', 'hardware'},
                'sports': {'sports', 'nba', 'soccer', 'football', 'tennis', 'baseball', 'hockey', 'game', 'match'},
                'finance': {'finance', 'stock', 'market', 'investment', 'bank', 'money', 'economy'},
                'business': {'business', 'company', 'corporate', 'entrepreneur', 'industry'},
                'travel': {'travel', 'trip', 'flight', 'vacation', 'hotel', 'tourism'},
                'entertainment': {'entertainment', 'movie', 'film', 'music', 'celebrity', 'show'},
                'health': {'health', 'medicine', 'doctor', 'hospital', 'disease', 'fitness', 'wellness'},
                'science': {'science', 'research', 'study', 'space', 'biology', 'chemistry', 'physics'}
            }

            tokens = row['tokens']
            for category, keywords in category_keywords.items():
                if any(token in keywords for token in tokens):
                    return category
            return row['category']

        df['topic'] = df.apply(categorize, axis=1)
        print("DataFrame with topics:\n", df.head())

        # Print distribution of topics to debug
        print(df['topic'].value_counts())

        df.to_csv('processed_news.csv', index=False)
        print("Processed data saved to processed_news.csv")
    else:
        print("Key 'articles' not found in the JSON data")

# Unit tests for Flask app
def run_tests():
    import unittest
    class FlaskTestCase(unittest.TestCase):
        def test_home(self):
            tester = app.test_client(self)
            response = tester.get('/')
            self.assertEqual(response.status_code, 200)

        def test_recommend(self):
            tester = app.test_client(self)
            response = tester.post('/recommend', data=dict(preferences="technology"))
            self.assertEqual(response.status_code, 200)

    unittest.main()

# Main function
if __name__ == '__main__':
    # Uncomment the function you want to run
    # fetch_news()      # Fetch news articles
    # process_data()    # Process news data
    # run_tests()       # Run unit tests
    app.run(debug=True) # Start Flask app
