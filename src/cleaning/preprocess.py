import os
from pathlib import Path

import pandas as pd


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_and_clean_data(file_path: str | os.PathLike, output_path: str | os.PathLike | None = None) -> pd.DataFrame:
    project_root = get_project_root()
    raw_path = Path(file_path)

    if not raw_path.is_absolute():
        raw_path = project_root / raw_path

    if not raw_path.exists():
        raise FileNotFoundError(f"Dataset not found: {raw_path}")

    print(f"Loading dataset from: {raw_path}")
    df = pd.read_excel(raw_path)
    print(f"Original shape: {df.shape}")

    original_rows = len(df)

    # Remove completely empty rows
    df = df.dropna(how='all').copy()

    # Standardize column names
    df.columns = df.columns.str.strip()

    # Remove rows with missing essential values
    required_columns = ['InvoiceNo', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'UnitPrice', 'CustomerID', 'Country']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    df = df.dropna(subset=['CustomerID', 'InvoiceDate', 'Quantity', 'UnitPrice'])

    # Remove cancelled transactions
    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]

    # Remove invalid numeric values
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
    df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')
    df = df.dropna(subset=['Quantity', 'UnitPrice'])

    # Keep only valid transactions
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]

    # Make invoice date consistent
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
    df = df.dropna(subset=['InvoiceDate'])

    # Convert CustomerID to integer and keep valid IDs
    df['CustomerID'] = pd.to_numeric(df['CustomerID'], errors='coerce')
    df = df.dropna(subset=['CustomerID'])
    df['CustomerID'] = df['CustomerID'].astype(int)

    # Add derived metrics for analysis
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    df['InvoiceMonth'] = df['InvoiceDate'].dt.to_period('M').astype(str)

    # Optional cleanup for description text
    df['Description'] = df['Description'].fillna('Unknown').astype(str).str.strip()
    df['Country'] = df['Country'].fillna('Unknown').astype(str).str.strip()

    if output_path is None:
        output_dir = project_root / 'data' / 'processed'
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / 'cleaned_online_retail.csv'
    else:
        output_path = Path(output_path)
        if not output_path.is_absolute():
            output_path = project_root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)

    removed_rows = original_rows - len(df)
    print(f"Rows removed: {removed_rows}")
    print(f"Cleaned shape: {df.shape}")
    print(f"Cleaned data saved to: {output_path}")

    return df


if __name__ == "__main__":
    project_root = get_project_root()
    raw_file_path = project_root / 'data' / 'raw' / 'Online Retail.xlsx'

    if raw_file_path.exists():
        load_and_clean_data(raw_file_path)
    else:
        print(f"Error: File not found at {raw_file_path}")
        print("Please ensure the dataset exists in the expected folder: data/raw/Online Retail.xlsx")
