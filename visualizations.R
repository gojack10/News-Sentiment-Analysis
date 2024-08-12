# Get the directory of the current script
script_dir <- dirname(rstudioapi::getActiveDocumentContext()$path)

# Set the working directory to the script's directory
setwd(script_dir)

# Install and load required packages
if (!requireNamespace("pacman", quietly = TRUE)) install.packages("pacman")
pacman::p_load(tidyverse, plotly, heatmaply, gplots)

# Print the current working directory
print(paste("Current working directory:", getwd()))

# List files in the current directory
print("Files in the current directory:")
print(list.files())

# Construct the full path for the CSV file
csv_path <- file.path(script_dir, "articles_data.csv")
print(paste("Looking for CSV file at:", csv_path))

# Check if the file exists
if (!file.exists(csv_path)) {
  stop(paste("Error: articles_data.csv not found in", script_dir))
}

# Read the CSV file
data <- read_csv(csv_path)

# Print data summary
print("Data summary:")
print(summary(data))

# Print column names
print("Column names:")
print(colnames(data))

# Check for missing values
if (anyNA(data)) {
    print("Warning: The dataset contains missing values.")
    print("Missing value count by column:")
    print(colSums(is.na(data)))
} else {
    print("No missing values in the dataset.")
}

# Prepare data for heatmap
heatmap_data <- data %>%
  select(title, source, sentiment_score) %>%
  pivot_wider(names_from = source, values_from = sentiment_score)

# Remove columns with all NA values
heatmap_data <- heatmap_data %>%
  select_if(~!all(is.na(.)))

# Convert to matrix
mat <- as.matrix(heatmap_data[, -1])
rownames(mat) <- heatmap_data$title

# Remove rows with all NA values
mat <- mat[rowSums(!is.na(mat)) > 0, ]

# Replace any remaining NA values with 0
mat[is.na(mat)] <- 0

# If matrix is empty after removing NAs, stop heatmap creation
if (nrow(mat) == 0 || ncol(mat) == 0) {
  print("Error: No valid data for heatmap creation after removing NAs")
} else {
  # Calculate standard deviation for columns
  sds <- apply(mat, 2, function(x) sd(x, na.rm = TRUE))
  
  print("Standard deviations of columns:")
  print(sds)
  
  # Remove columns with zero standard deviation
  mat <- mat[, sds != 0]

# Proceed with heatmap creation if valid columns remain
if (ncol(mat) > 0) {
  # Sort the matrix by mean sentiment score (descending order)
  mean_scores <- rowMeans(mat, na.rm = TRUE)
  mat <- mat[order(mean_scores, decreasing = TRUE), ]
  
  # Create a color palette function
  sentiment_palette <- colorRampPalette(c("#CB1B4E", "#E2E2E2", "#23BBAC"))
  
  # Create row side colors based on mean sentiment scores
  row_colors <- data.frame(sentiment = sentiment_palette(100)[cut(mean_scores[order(mean_scores, decreasing = TRUE)], breaks = 100)])
  
  # Read overall sentiment from CSV
  overall_sentiment_path <- file.path(script_dir, "overall_sentiment.csv")
  overall_sentiment_df <- read.csv(overall_sentiment_path, stringsAsFactors = FALSE)
  overall_sentiment <- as.numeric(overall_sentiment_df$overall_sentiment[1])

  # Function to categorize sentiment
  categorize_sentiment <- function(score) {
    if (is.na(score)) return("unknown")
    else if (score < -0.75) return("very negative")
    else if (score < -0.25) return("negative")
    else if (score < -0.1) return("slightly negative")
    else if (score < 0.1) return("neutral")
    else if (score < 0.25) return("slightly positive")
    else if (score < 0.75) return("positive")
    else return("very positive")
  }

  sentiment_category <- categorize_sentiment(overall_sentiment)

  # Create annotation for overall sentiment
  overall_sentiment_annotation <- list(
    x = 0.5,
    y = 1.01,  # Adjusted to appear above the heatmap
    text = sprintf("Overall sentiment: %.4f, %s", overall_sentiment, sentiment_category),
    xref = "paper",
    yref = "paper",
    xanchor = "center",
    yanchor = "bottom",
    showarrow = FALSE,
    font = list(size = 14)
  )

  # Create interactive heatmap with heatmaply
  heatmap_interactive <- heatmaply(mat,
            dendrogram = "none",
            xlab = "", ylab = "",
            main = "Sentiment Heatmap by Source and Article",
            scale = "none",
            margins = c(60, 100, 60, 20),  # Increased top margin
            grid_color = "white",
            grid_width = 0.00001,
            titleX = FALSE,
            hide_colorbar = FALSE,
            branches_lwd = 0.1,
            label_names = c("Article", "Source", "Sentiment Score"),
            fontsize_row = 5, fontsize_col = 7,
            labCol = colnames(mat),
            labRow = NULL,  # Remove row labels
            colors = sentiment_palette(100),
            limits = c(-1, 1),
            colorbar_len = 0.5,
            key.title = "Sentiment Score",
            na.rm = TRUE,
            plot_method = "ggplot"
  ) %>%
    layout(
      yaxis = list(showticklabels = FALSE, title = ""),  # Remove y-axis labels and title
      annotations = overall_sentiment_annotation,  # Add overall sentiment annotation
      margin = list(t = 100)  # Increase top margin to accommodate annotation
    )
  
  # Save interactive heatmap
  htmlwidgets::saveWidget(heatmap_interactive, "sentiment_heatmap_interactive.html", selfcontained = FALSE)
}}

print(paste("Visualizations created. Check in", script_dir))