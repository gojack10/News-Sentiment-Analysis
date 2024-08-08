import requests
import nltk
import string
import threading
import sys
import os
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from newspaper import Article
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from dotenv import load_dotenv
from newsapi import NewsApiClient
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

vader = SentimentIntensityAnalyzer()

load_dotenv()
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def get_user_input():
    topic = input("Enter a topic of interest: ")
    while True:
        num_articles = input("Enter the number of articles to fetch (default is 20, max is 50): ")
        if num_articles == "":
            num_articles = 20
            break
        if num_articles.isdigit() and 1 <= int(num_articles) <= 50:
            num_articles = int(num_articles)
            break
        print("Please enter a valid number between 1 and 50.")
    return topic, num_articles

def fetch_articles(topic, num_articles):
    articles = []
    try:
        # Fetch top headlines
        top_headlines = newsapi.get_top_headlines(q=topic, language='en', page_size=min(num_articles // 2, 20))
        articles.extend(top_headlines['articles'])

        # Fetch everything
        all_articles = newsapi.get_everything(q=topic, language='en', sort_by='relevancy', page_size=num_articles - len(articles))
        articles.extend(all_articles['articles'])

        print(f"Fetched {len(articles)} articles related to '{topic}'")
        return articles
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return []

def extract_full_content(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except:
        return ""

def compute_relevance_score(topic_embedding, article_embedding):
    return cosine_similarity(topic_embedding.reshape(1, -1), article_embedding.reshape(1, -1))[0][0]

def process_articles(articles, topic):
    processed_articles = []
    omitted_count = 0

    # Compute topic embedding
    topic_embedding = model.encode(topic)

    for article in articles:
        title = article.get('title', '')
        description = article.get('description', '')
        source = article.get('source', {}).get('name', '')
        published_at = article.get('publishedAt', '')
        url = article.get('url', '')

        # Check for placeholder or invalid articles
        if (title == '[Removed]' or description == '[Removed]' or
            source == '[Removed]' or published_at == '1970-01-01T00:00:00Z' or
            url == 'https://removed.com' or not title or not description):
            omitted_count += 1
            continue

        # Compute article embedding
        article_text = f"{title} {description}"
        article_embedding = model.encode(article_text)

        # Compute relevance score
        relevance_score = compute_relevance_score(topic_embedding, article_embedding)

        # Set a threshold for relevance (you can adjust this value)
        if relevance_score < 0.2:
            omitted_count += 1
            continue

        # Extract full content
        full_content = extract_full_content(url)

        processed_articles.append({
            'title': title,
            'description': description,
            'full_content': full_content,
            'source': source,
            'published_at': published_at,
            'url': url,
            'relevance_score': relevance_score
        })
        print(f"Accepted: {title} (Relevance: {relevance_score:.4f})")

    if omitted_count > 0:
        print(f"Omitted {omitted_count} article(s) due to missing, invalid data, or low relevance.")

    if len(processed_articles) == 0:
        print("No valid articles found. Try a different search term.")
    
    return processed_articles

def analyze_sentiment(articles):
    for article in articles:
        text = article['title'] + ". " + article['description']
        vader_scores = vader.polarity_scores(text)
        compound_score = vader_scores['compound']
        article['sentiment_score'] = compound_score
        
        # Convert compound score to percentages
        if compound_score >= 0:
            positive_percent = int(compound_score * 100)
            negative_percent = 0
            neutral_percent = 100 - positive_percent
        else:
            negative_percent = int(abs(compound_score) * 100)
            positive_percent = 0
            neutral_percent = 100 - negative_percent
        
        article['sentiment_percentages'] = {
            'positive': positive_percent,
            'neutral': neutral_percent,
            'negative': negative_percent
        }
    return articles

def sort_articles(articles):
    return sorted(articles, key=lambda x: (x['relevance_score'], abs(x['sentiment_score'])), reverse=True)

def process_news(topic, num_articles):
    print(f"\nFetching articles for topic: '{topic}'")
    raw_articles = fetch_articles(topic, num_articles)
    
    if not raw_articles:
        print("No articles were fetched. Please check your API key and internet connection.")
        return None

    try:
        processed_articles = process_articles(raw_articles, topic)
    except Exception as e:
        print(f"Error processing articles: {e}")
        return None

    if not processed_articles:
        print("No valid articles could be processed. Try a different search term or check the API response.")
        return None

    analyzed_articles = analyze_sentiment(processed_articles)
    sorted_articles = sort_articles(analyzed_articles)
    
    return sorted_articles