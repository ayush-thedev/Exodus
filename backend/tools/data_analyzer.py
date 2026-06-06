import pandas as pd
import numpy as np
from typing import Dict, Any, List

def get_dataframe_metadata(df: pd.DataFrame) -> Dict[str, Any]:
    """Extracts detailed metadata from a DataFrame for LLM context."""
    
    # Basic info
    info = {
        "shape": df.shape,
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "dtypes": {str(k): str(v) for k, v in df.dtypes.items()},
    }
    
    # Missing values summary
    null_counts = df.isnull().sum()
    info["missing_values"] = {
        col: int(count) for col, count in null_counts.items() if count > 0
    }
    
    # Detect date columns
    date_cols = []
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                # Try to convert to datetime to see if it's possible
                # We use a small sample to speed it up
                sample = df[col].dropna().head(10)
                if not sample.empty:
                    pd.to_datetime(sample)
                    date_cols.append(col)
            except (ValueError, TypeError):
                continue
    info["potential_date_columns"] = date_cols
    
    # Categorical vs Numeric
    numeric_df = df.select_dtypes(include=[np.number])
    categorical_df = df.select_dtypes(include=['object', 'category'])
    
    info["numeric_columns"] = list(numeric_df.columns)
    info["categorical_columns"] = list(categorical_df.columns)
    
    # Categorical unique values (top 5)
    info["categorical_unique_counts"] = {
        col: {
            "unique_count": df[col].nunique(),
            "top_values": [str(v) if isinstance(v, (pd.Timestamp, np.datetime64)) else v for v in df[col].value_counts().head(5).index]
        }
        for col in categorical_df.columns
    }
    
    # Numeric summary statistics
    if not numeric_df.empty:
        stats = numeric_df.describe().to_dict()
        info["numeric_stats"] = {
            col: {k: float(v) if not np.isnan(v) and not isinstance(v, (pd.Timestamp, np.datetime64)) else (str(v) if isinstance(v, (pd.Timestamp, np.datetime64)) else None) for k, v in col_stats.items()}
            for col, col_stats in stats.items()
        }
    
    # Data preview (head 5) - ensure all values are serializable
    preview = df.head(5).to_dict(orient='records')
    for row in preview:
        for key, val in row.items():
            if isinstance(val, (pd.Timestamp, np.datetime64)):
                row[key] = str(val)
            elif pd.isna(val):
                row[key] = None
    info["preview"] = preview
    
    return info

def extract_metadata_from_file(file_path: str, sheet_name: str = None) -> Dict[str, Any]:
    """Loads a file and extracts metadata."""
    ext = file_path.split('.')[-1].lower()
    
    try:
        if ext in ['xlsx', 'xls']:
            # If sheet_name is not provided, we might want to list all sheets first
            # but for metadata extraction we need a specific sheet
            df = pd.read_excel(file_path, sheet_name=sheet_name or 0)
        elif ext == 'csv':
            df = pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
            
        return get_dataframe_metadata(df)
    except Exception as e:
        return {"error": f"Failed to load file: {str(e)}"}
