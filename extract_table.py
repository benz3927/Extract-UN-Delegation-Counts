import pandas as pd
from docling.document_converter import DocumentConverter

pdf_path = "/Users/CS/Documents/DataExtraction/International Trade/aid_commitments/un.pdf"

# Initialize converter
converter = DocumentConverter()
docling_doc = converter.convert(pdf_path)

pages = docling_doc.pages[5:]

all_tables = []

# Collect all tables with metadata (page + index)
for page_num, page in enumerate(pages, start=6):
    for table_num, table in enumerate(page.tables, start=1):
        df = table.to_dataframe()
        sheet_name = f"Page{page_num}_Table{table_num}"
        all_tables.append((sheet_name, df))

# Save to separate sheets
if all_tables:
    output_excel = "docling_extracted_tables_by_sheet.xlsx"
    with pd.ExcelWriter(output_excel) as writer:
        for sheet_name, df in all_tables:
            # Excel sheet names must be ≤ 31 characters
            safe_sheet_name = sheet_name[:31]
            df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
    print(f"✅ Tables saved to: {output_excel} (each on its own sheet)")
else:
    print("⚠️ No tables found starting from page 6.")
