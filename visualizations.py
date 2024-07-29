import pandas as pd
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from flask import request
import threading

def create_dashboard(articles):
    df = pd.DataFrame(articles)
    
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    app.layout = dbc.Container([
        html.H1("News Sentiment Analysis Dashboard"),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='heatmap')
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(id='article-details')
            ], width=12)
        ])
    ])
    
    @app.callback(
        Output('heatmap', 'figure'),
        Input('heatmap', 'relayoutData')
    )
    def update_heatmap(relayoutData):
        # Create a list of unique sources and sort them
        sources = sorted(df['source'].unique())
        
        # Create a pivot table with articles as rows and sources as columns
        pivot_df = df.pivot(index='title', columns='source', values='sentiment_score')
        
        # Fill NaN values with a sentinel value (e.g., 999) to distinguish from actual data
        pivot_df = pivot_df.fillna(999)
        
        # Create custom color scale
        color_scale = [
            [0, "rgb(178,24,43)"],  # Dark red for very negative
            [0.25, "rgb(239,138,98)"],  # Light red for slightly negative
            [0.5, "rgb(253,219,199)"],  # Very light orange for neutral
            [0.75, "rgb(161,217,155)"],  # Light green for slightly positive
            [1, "rgb(49,163,84)"]  # Dark green for very positive
        ]
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_df.values,
            y=pivot_df.index,
            x=pivot_df.columns,
            colorscale=color_scale,
            zmin=-1, zmax=1,
            hoverongaps=False,
            hovertemplate='Article: %{y}<br>Source: %{x}<br>Sentiment: %{z:.2f}<extra></extra>',
            showscale=True
        ))
        
        fig.update_layout(
            title='Sentiment Heatmap by Article and Source',
            xaxis_title='Sources',
            yaxis_title='Articles',
            height=800,  # Increased height to accommodate more articles
            margin=dict(l=150, r=50, t=50, b=50),
            plot_bgcolor='rgba(0,0,0,0)',
        )
        
        # Update x-axis (sources)
        fig.update_xaxes(
            side='bottom', 
            tickfont=dict(size=10),
            gridcolor='lightgrey'
        )
        
        # Update y-axis (articles)
        fig.update_yaxes(
            side='left', 
            tickfont=dict(size=8),
            gridcolor='lightgrey'
        )
        
        # Add borders to cells
        fig.update_traces(
            xgap=2,  # gap between columns
            ygap=2,  # gap between rows
        )
        
        # Update color bar
        fig.update_coloraxes(colorbar=dict(
            title="Sentiment Score",
            titleside="right",
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["-1<br>(Very Negative)", "-0.5", "0<br>(Neutral)", "0.5", "1<br>(Very Positive)"],
            lenmode="fraction", len=0.75,
            yanchor="middle", y=0.5,
            ticks="outside", ticklen=5,
            outlinewidth=1, outlinecolor="black"
        ))
        
        return fig
    
    @app.callback(
        Output('article-details', 'children'),
        Input('heatmap', 'clickData')
    )
    def display_article_details(clickData):
        if clickData is None:
            return "Click on a cell to see article details."
        
        y_index = clickData['points'][0]['y']
        x_index = clickData['points'][0]['x']
        
        article = df[(df['source'] == x_index) & (df['title'] == y_index)]
        if article.empty:
            return "No article details available for this cell."
        
        article = article.iloc[0]
        
        return dbc.Card([
            dbc.CardHeader(f"Article Details: {article['title']}"),
            dbc.CardBody([
                html.P(f"Source: {article['source']}"),
                html.P(f"Published: {article['published_at']}"),
                html.P(f"Relevance Score: {article['relevance_score']:.4f}"),
                html.P(f"Sentiment Score: {article['sentiment_score']:.2f}"),
                html.P("Sentiment Breakdown:"),
                html.Ul([
                    html.Li(f"Positive: {article['sentiment_percentages']['positive']}%"),
                    html.Li(f"Neutral: {article['sentiment_percentages']['neutral']}%"),
                    html.Li(f"Negative: {article['sentiment_percentages']['negative']}%")
                ]),
                html.A("Read Full Article", href=article['url'], target="_blank")
            ])
        ])
    
    return app

def run_dashboard(articles):
    app = create_dashboard(articles)
    
    stop_server = threading.Event()
    
    @app.server.route('/shutdown', methods=['POST'])
    def shutdown():
        stop_server.set()
        return 'Server shutting down...'
    
    print("\nLaunching interactive dashboard...")
    print("The dashboard will open in your default web browser.")
    print("Close the browser window or press Ctrl+C in this terminal to exit the program.")
    
    app.run_server(debug=False, use_reloader=False)