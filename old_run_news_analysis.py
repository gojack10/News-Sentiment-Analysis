from news import get_user_input, process_news
import pandas as pd
import subprocess
import csv
import re
import os
import shutil

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

def save_articles_to_csv(articles, filename='articles_data.csv'):
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to the project root (assuming the script is in the project root)
    project_root = current_dir
    
    # Construct the full path for the CSV file
    csv_path = os.path.join(project_root, filename)
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'source', 'published_at', 'url', 'relevance_score', 'sentiment_score', 'positive_percent', 'neutral_percent', 'negative_percent']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for article in articles:
            # Remove punctuation and newlines from title
            clean_title = re.sub(r'[^\w\s]', '', article['title']).replace('\n', ' ')
            
            writer.writerow({
                'title': clean_title,
                'source': article['source'],
                'published_at': article['published_at'],
                'url': article['url'],
                'relevance_score': f"{article['relevance_score']:.4f}",
                'sentiment_score': f"{article['sentiment_score']:.4f}",
                'positive_percent': article['sentiment_percentages']['positive'],
                'neutral_percent': article['sentiment_percentages']['neutral'],
                'negative_percent': article['sentiment_percentages']['negative']
            })
    
    print(f"Data saved to {csv_path}")

if __name__ == "__main__":
    topic, num_articles = get_user_input()
    articles = process_news(topic, num_articles)
    
    if articles:
        print_article_details(articles, topic)
        save_articles_to_csv(articles)
        
        # Run R script for visualization
        r_script_path = os.path.join(os.path.dirname(__file__), 'visualizations.R')
        
        # Try to find Rscript in the system PATH
        rscript_cmd = shutil.which('Rscript')
        
        if rscript_cmd is None:
            print("Error: Rscript not found in system PATH.")
            print("Please ensure R is installed and added to your system PATH.")
            print("You can also try running the R script manually:")
            print(f"Rscript {r_script_path}")
        else:
            try:
                subprocess.run([rscript_cmd, r_script_path], check=True)
                print("\nVisualization complete. Check the generated plots.")
            except subprocess.CalledProcessError as e:
                print(f"Error running R script: {e}")
                print("You can try running the R script manually:")
                print(f"Rscript {r_script_path}")
    else:
        print("No articles to display. Exiting.")