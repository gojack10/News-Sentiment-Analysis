from news import get_user_input, process_news
from visualizations import run_dashboard
import webbrowser
import threading
import time
import requests

def print_article_details(articles, topic):
    print(f"\nAnalyzed articles for topic: '{topic}'")
    print(f"Number of relevant articles found: {len(articles)}")
    print("\nArticles sorted by relevance score, then sentiment strength:\n")
    
    for article in articles:
        print(f"\nTitle: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"Published: {article['published_at']}")
        print(f"Relevance Score: {article['relevance_score']:.4f}")
        print(f"Sentiment Score: {article['sentiment_score']:.2f}")
        print(f"Sentiment Breakdown:")
        print(f"  Positive: {article['sentiment_percentages']['positive']}%")
        print(f"  Neutral: {article['sentiment_percentages']['neutral']}%")
        print(f"  Negative: {article['sentiment_percentages']['negative']}%")
        print(f"URL: {article['url']}")

def open_browser():
    webbrowser.open_new('http://127.0.0.1:8050/')

if __name__ == "__main__":
    topic, num_articles = get_user_input()
    articles = process_news(topic, num_articles)
    
    if articles:
        print_article_details(articles, topic)
        
        # Open the browser after a short delay
        threading.Timer(1, open_browser).start()
        
        # Run the dashboard
        run_dashboard(articles)
        
        # After the dashboard is closed, send a shutdown request
        try:
            requests.post('http://127.0.0.1:8050/shutdown')
        except:
            pass
        
        print("\nDashboard closed. Program exiting.")
    else:
        print("No articles to display. Exiting.")