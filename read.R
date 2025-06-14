library(readxl)
library(dplyr)

base_dir <- "/Users/CS/Documents/DataExtraction/Summer2025/aid_commitments"
oda_files <- c("all_oda", "grants_oda", "loans_oda", "techn_oda")
oda_paths <- file.path(base_dir, paste0(oda_files, ".xlsx"))

inspect_file <- function(filepath, name) {
  cat("\n📄 File:", name, "\n")
  df <- read_excel(filepath, skip = 6)
  print(colnames(df))
  print(head(df, 3))
}

for (i in seq_along(oda_paths)) {
  inspect_file(oda_paths[i], oda_files[i])
}

cat("\n📄 File: master (tofill_commitments_panel_1990_2022.xlsx)\n")
master_path <- file.path(base_dir, "tofill_commitments_panel_1990_2022.xlsx")
master_df <- read_excel(master_path)
print(colnames(master_df))
print(head(master_df, 3))
