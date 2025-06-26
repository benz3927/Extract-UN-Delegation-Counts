import pandas as pd
import os
import re
import numpy as np

def clean_numeric(x):
    if pd.isna(x):
        return np.nan
    try:
        x = str(x).replace(' ', '').replace(',', '')
        return float(x)
    except:
        return np.nan

def process_file_custom(filepath):
    # Extract year from filename
    year_match = re.search(r'(\d{4})', filepath)
    year = int(year_match.group(1)) if year_match else None
    print(f"Processing {filepath} for year {year}")

    # Determine skiprows
    skiprows = 2 if year and (2000 <= year <= 2010) else 0

    # Read the Excel file
    try:
        df = pd.read_excel(filepath, skiprows=skiprows, dtype=str)
    except Exception as e:
        print(f"Failed to read {filepath}: {e}")
        return pd.DataFrame()

    if df.shape[1] < 3:
        print(f"Skipping {filepath}: less than 3 non-empty column names.")
        return pd.DataFrame()

    if df.empty or df.columns.empty:
        print(f"Empty or invalid Excel structure in {filepath}, skipping.")
        return pd.DataFrame()

    df.columns = df.columns.astype(str).str.strip()
    country_col = df.columns[0]

    data = pd.DataFrame()
    data['country'] = df[country_col].str.strip()

    if year and 2000 <= year <= 2010:
        annual_col = df.columns[5] if len(df.columns) > 5 else None
        outstanding_col = df.columns[8] if len(df.columns) > 8 else None

        annual = df[annual_col].apply(clean_numeric) if annual_col else np.nan
        outstanding = df[outstanding_col].apply(clean_numeric) if outstanding_col else np.nan

        net = (
            annual.fillna(0) + outstanding.fillna(0)
            if isinstance(annual, pd.Series) and isinstance(outstanding, pd.Series)
            else np.nan
        )
        net[(annual.isna()) & (outstanding.notna())] = outstanding
        net[(outstanding.isna()) & (annual.notna())] = annual

    elif year and 2011 <= year <= 2016:
        annual = np.nan
        outstanding = np.nan
        net_col = df.columns[8] if len(df.columns) > 8 else None
        net = df[net_col].apply(clean_numeric) if net_col else np.nan
    else:
        print(f"Year {year} out of range or missing, skipping file")
        return pd.DataFrame()

    data['year'] = year
    data['annual_contributions'] = annual
    data['total_outstanding_contributions'] = outstanding
    data['assessed_contributions'] = net

    return data

def merge_all_custom(folder_path):
    all_data = []
    for fname in sorted(os.listdir(folder_path)):
        if not fname.endswith('.xlsx') or fname.startswith('~$'):
            continue
        fp = os.path.join(folder_path, fname)
        df = process_file_custom(fp)
        if not df.empty:
            all_data.append(df)

    if all_data:
        merged = pd.concat(all_data, ignore_index=True)
        return merged
    else:
        print("No data found")
        return pd.DataFrame()

# --- Main usage ---
if __name__ == "__main__":
    folder = 'excel_outputs'
    merged_df = merge_all_custom(folder)

    print("\nFinal merged data:")
    print(merged_df.head())

    # Save to Excel with final column order
    output_path = 'contributions_2000-2016.xlsx'
    merged_df = merged_df[['year', 'country', 'annual_contributions',
                           'total_outstanding_contributions', 'assessed_contributions']]
    merged_df.to_excel(output_path, index=False)
    print(f"\nSaved merged data to {output_path}")
