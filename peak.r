library(readxl)

base_dir <- "/Users/CS/Documents/DataExtraction/Summer2025/aid_commitments"

peek_excel <- function(filename, n=10) {
  path <- file.path(base_dir, filename)
  print(paste("Peeking:", filename))
  df <- read_excel(path, n_max = n, col_names = FALSE)
  print(df)
}

peek_excel("grants_oda.xlsx")
peek_excel("loans_oda.xlsx")
peek_excel("techn_oda.xlsx")
