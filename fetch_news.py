import requests
import json

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
                article['category'] = category  # Add category to each article
            all_articles.extend(articles)
            print(f"Fetched {len(articles)} articles for category: {category}")
        else:
            print(f"Unexpected response structure for category {category}: {json.dumps(news_data, indent=4)}")
    else:
        print(f"Failed to fetch news data for category {category}. Status code: {response.status_code}, Response: {response.text}")

with open('news_data.json', 'w') as json_file:
    json.dump({'articles': all_articles}, json_file)

print(f"Total articles fetched: {len(all_articles)}")
