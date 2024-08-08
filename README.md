# News Sentiment Analysis

This project is a news aggregator that collects articles on a specific topic, performs sentiment analysis, and displays the results in an interactive dashboard. It uses the NewsAPI to fetch articles, NLTK's VADER for sentiment analysis, machine learning for relevance scoring, and creates visualizations using Plotly and Dash.

## Features

- Fetch news articles on a user-defined topic using NewsAPI
- Perform sentiment analysis on each article using NLTK's VADER
- Calculate relevance scores for articles using machine learning-based sentence embeddings
- Display an interactive heatmap of sentiment scores by article and source
- Provide detailed information for each article on demand
- Visualize sentiment distribution and relevance scores

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/news-sentiment-analysis.git
   cd news-sentiment-analysis
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Obtain a NewsAPI key from [https://newsapi.org/](https://newsapi.org/) and replace the placeholder in `news.py` with your actual API key.

## Usage

To run the News Sentiment Analysis Dashboard:

1. Open a terminal and navigate to the project directory.

2. Run the following command:
   ```
   python run_news_analysis.py
   ```

3. When prompted, enter a topic of interest and the number of articles you want to analyze (default is 20, max is 50).

4. The program will fetch and analyze the articles, then launch an interactive dashboard in your default web browser.

5. Explore the dashboard:
   - The heatmap shows sentiment scores for each article by source.
   - Click on a cell in the heatmap to view detailed information about the article.
   - Hover over cells to see quick sentiment information.

6. To exit the program, close the browser window or press Ctrl+C in the terminal.

## How It Works

1. **Article Fetching**: The program uses NewsAPI to fetch articles related to the user-defined topic.

2. **Content Extraction**: For each article, it attempts to extract the full content using the Newspaper3k library.

3. **Relevance Scoring**: 
   - The project uses a pre-trained SentenceTransformer model ('paraphrase-MiniLM-L6-v2') to compute relevance scores.
   - This model converts the article text and the user's topic into high-dimensional vector representations (embeddings).
   - The cosine similarity between the topic embedding and the article embedding is calculated to determine the relevance score.
   - This machine learning approach allows for a more nuanced understanding of relevance beyond simple keyword matching.

4. **Sentiment Analysis**: NLTK's VADER (Valence Aware Dictionary and sEntiment Reasoner) is used to perform sentiment analysis on the article's title and description.

5. **Data Processing**: Articles are sorted based on relevance and sentiment strength. Articles with low relevance scores are filtered out to ensure the most pertinent content is presented.

6. **Visualization**: The processed data is used to create an interactive dashboard using Plotly and Dash, featuring a sentiment heatmap and detailed article information.

## Project Structure

- `news.py`: Contains functions for fetching and processing news articles, including the machine learning-based relevance scoring.
- `run_news_analysis.py`: The main script that orchestrates the news analysis process.
- `visualizations.py`: Creates and runs the interactive dashboard.

## Contributing

Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

## Acknowledgments

- [NewsAPI](https://newsapi.org/) for providing access to news articles.
- [NLTK](https://www.nltk.org/) for natural language processing tools.
- [SentenceTransformers](https://www.sbert.net/) for the pre-trained model used in relevance scoring.
- [Plotly](https://plotly.com/) and [Dash](https://dash.plotly.com/) for interactive visualizations.
- [Newspaper3k](https://newspaper.readthedocs.io/) for article content extraction
