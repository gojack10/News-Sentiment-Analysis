# Get the directory of the current script
script_dir <- dirname(rstudioapi::getActiveDocumentContext()$path)

# Set the working directory to the script's directory
setwd(script_dir)

# Load required libraries
library(tidyverse)
library(plotly)
library(heatmaply)

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

# Print heatmap data summary
print("Heatmap data summary:")
print(summary(heatmap_data))

# Convert to matrix
mat <- as.matrix(heatmap_data[, -1])
rownames(mat) <- heatmap_data$title

# Remove rows and columns with all NA values
mat <- mat[rowSums(!is.na(mat)) > 0, colSums(!is.na(mat)) > 0]

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
    heatmap <- tryCatch({
      heatmaply(mat,
                dendrogram = "none",
                xlab = "", ylab = "",
                main = "Sentiment Heatmap by Source and Article",
                scale = "none",
                margins = c(60, 100, 40, 20),
                grid_color = "white",
                grid_width = 0.00001,
                titleX = FALSE,
                hide_colorbar = FALSE,
                branches_lwd = 0.1,
                label_names = c("Article", "Source", "Sentiment Score"),
                fontsize_row = 5, fontsize_col = 7,
                labCol = colnames(mat),
                labRow = rownames(mat),
                colors = colorRampPalette(c("#CB1B4E", "#E2E2E2", "#23BBAC"))(100),
                limits = c(-1, 1),
                colorbar_len = 0.5,
                key.title = "Sentiment Score",
                na.rm = TRUE
      )
    }, error = function(e) {
      print(paste("Error in creating heatmap:", e$message))
      NULL
    })
    
    if (!is.null(heatmap)) {
      # Save without making it self-contained
      htmlwidgets::saveWidget(heatmap, "sentiment_heatmap.html", selfcontained = FALSE)
      print(paste("Heatmap created. Check sentiment_heatmap.html in", script_dir))
    } else {
      print("Failed to create heatmap.")
    }
  } else {
    print("Error: No valid columns for heatmap creation after removing zero variance columns.")
  }
}

# Create a bar chart of average sentiment by source
create_bar_chart <- function(data) {
  avg_sentiment <- data %>%
    group_by(source) %>%
    summarize(avg_sentiment = mean(sentiment_score, na.rm = TRUE))
  
  bar <- plot_ly(avg_sentiment, x = ~source, y = ~avg_sentiment, type = 'bar',
                 marker = list(color = ~avg_sentiment, 
                               colorscale = list(c(0, "#CB1B4E"),
                                                 c(0.5, "#E2E2E2"),
                                                 c(1, "#23BBAC")))) %>%
    layout(title = 'Average Sentiment by Source',
           xaxis = list(title = 'Source'),
           yaxis = list(title = 'Average Sentiment Score'),
           plot_bgcolor = "rgba(0,0,0,0)",
           paper_bgcolor = "rgba(0,0,0,0)")
  
  htmlwidgets::saveWidget(bar, "avg_sentiment_by_source.html", selfcontained = FALSE)
}

# Create visualizations
create_bar_chart(data)

print(paste("Visualizations created. Check avg_sentiment_by_source.html and sentiment_heatmap.html in", script_dir))