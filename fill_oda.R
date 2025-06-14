library(readxl)
library(dplyr)
library(tidyr)
library(openxlsx)

base_dir <- "/Users/CS/Documents/DataExtraction/Summer2025/aid_commitments"

# Map file names to column names
file_to_column <- list(
  "all_oda.xlsx" = "all_oda",
  "grants_oda.xlsx" = "grants_oda", 
  "loans_oda.xlsx" = "loans_oda",
  "techn_oda.xlsx" = "technical_oda"
)

read_oda_file <- function(filename, column_name) {
  path <- file.path(base_dir, filename)
  
  # Read the Excel file
  raw <- read_excel(path, skip = 6, col_names = FALSE)
  
  # First row has years, first column has countries
  years <- as.numeric(raw[1, -1])
  
  countries <- raw[-1, 1][[1]]
  
  # Get the data matrix
  data_matrix <- raw[-1, 2:(length(years)+1)]
  data_matrix <- data_matrix[1:length(countries), 1:length(years)]
  
  # Convert to long format
  result <- expand.grid(country = countries, year = years, stringsAsFactors = FALSE)
  result$value <- as.numeric(as.matrix(data_matrix))
  
  # Rename value column
  names(result)[3] <- column_name
  
  # Remove duplicates
  result <- result %>% distinct(country, year, .keep_all = TRUE)
  
  return(result)
}

# Read all ODA files
oda_data_list <- list()
for(filename in names(file_to_column)) {
  column_name <- file_to_column[[filename]]
  oda_data_list[[column_name]] <- read_oda_file(filename, column_name)
}

# Merge all ODA data
merged_oda <- oda_data_list[[1]]
for(i in 2:length(oda_data_list)) {
  merged_oda <- full_join(merged_oda, oda_data_list[[i]], 
                         by = c("country", "year"), 
                         relationship = "one-to-one")
}

# Read master file
master_path <- file.path(base_dir, "tofill_commitments_1990_2022.xlsx")
master_df <- read_excel(master_path)

# Update the existing ODA columns with new data
final_df <- master_df %>%
  select(-any_of(c("all_oda", "grants_oda", "loans_oda", "technical_oda"))) %>%
  left_join(merged_oda, by = c("country", "year"))

# Reorder columns to match original master file exactly
final_df <- final_df[, names(master_df)]

# Write output
output_path <- file.path(base_dir, "tofill_commitments_merged_1990_2022.xlsx")
write.xlsx(final_df, output_path)

cat("✅ Done! Filled ODA columns with data from Excel files, columns reordered to match original.\n")
cat("Output written to:", output_path, "\n")
