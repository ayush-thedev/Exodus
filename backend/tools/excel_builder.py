import pandas as pd
import xlsxwriter
import os
from typing import Dict, Any, List, Optional

def create_excel_report(
    file_path: str,
    df: pd.DataFrame,
    analysis_results: Dict[str, Any],
    visualization_results: Optional[Dict[str, Any]] = None,
    output_name: str = "exodus_report.xlsx"
) -> str:
    """Creates a professional multi-sheet Excel report using XlsxWriter."""
    
    output_path = os.path.join(os.path.dirname(file_path), output_name)
    workbook = xlsxwriter.Workbook(output_path)
    
    # Formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#636EFA',
        'font_color': 'white',
        'border': 1
    })
    
    # Sheet 1: Data
    data_sheet = workbook.add_worksheet("Data")
    for col_num, value in enumerate(df.columns.values):
        data_sheet.write(0, col_num, value, header_format)
    
    for row_num, row_data in enumerate(df.values):
        for col_num, value in enumerate(row_data):
            data_sheet.write(row_num + 1, col_num, value)
    
    # Sheet 2: Analysis
    analysis_sheet = workbook.add_worksheet("Analysis")
    analysis_sheet.write(0, 0, "Analysis Summary", header_format)
    analysis_sheet.write(1, 0, analysis_results.get("summary", "No summary provided"))
    
    if "stdout" in analysis_results:
        analysis_sheet.write(3, 0, "Execution Output", header_format)
        analysis_sheet.write(4, 0, analysis_results["stdout"])
        
    # Sheet 3: Charts
    chart_sheet = workbook.add_worksheet("Charts")
    if visualization_results and "chart_spec" in visualization_results:
        spec = visualization_results["chart_spec"]
        if spec:
            chart_type = spec.get("type", "column")
            chart = workbook.add_chart({'type': chart_type})
            
            # This is a simplification. Real data mapping is complex.
            # We assume the chart data is in the Data sheet.
            # For now, we'll just add a placeholder or simple mapping.
            chart_sheet.write(0, 0, f"Chart: {spec.get('title', 'Generated Chart')}")
            
    # Sheet 4: Summary
    summary_sheet = workbook.add_worksheet("Summary")
    summary_sheet.write(0, 0, "Exodus AI Insights", header_format)
    summary_sheet.write(2, 0, "Key Metrics")
    # ... Add automated metrics ...
    
    workbook.close()
    return output_path
