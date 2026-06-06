import pandas as pd
from pathlib import Path
from typing import Dict, Any
from backend.agents.state import ExcelWorkflowState, WorkbookInsight, SheetProfile, FileArtifact
from backend.core.utils import get_dataframe_metadata

class DataExplorerAgent:
    def process(self, state: ExcelWorkflowState) -> ExcelWorkflowState:
        input_files = state.get("input_files", [])
        if not input_files:
            state["errors"] = state.get("errors", []) + ["No input files provided to explorer."]
            state["workflow_status"] = "failed"
            return state
            
        insights = []
        for artifact in input_files:
            try:
                file_path = Path(artifact.path)
                excel_file = pd.ExcelFile(file_path)
                sheet_profiles = []
                total_rows = 0
                
                # Update sheet names in artifact
                artifact.sheet_names = excel_file.sheet_names
                
                for sheet_name in excel_file.sheet_names:
                    # Load sheet
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    row_count, col_count = df.shape
                    total_rows += row_count
                    
                    # Generate metadata using our core utility
                    metadata = get_dataframe_metadata(df)
                    
                    sheet_profiles.append(
                        SheetProfile(
                            sheet_name=sheet_name,
                            row_count=int(row_count),
                            column_count=int(col_count),
                            headers=list(df.columns),
                            preview_rows=metadata.get("preview", [])
                        )
                    )
                
                artifact.row_count = total_rows
                
                insights.append(
                    WorkbookInsight(
                        artifact_id=artifact.artifact_id,
                        file_name=artifact.name,
                        file_path=file_path,
                        sheet_count=len(sheet_profiles),
                        total_rows=total_rows,
                        total_columns=sheet_profiles[0].column_count if sheet_profiles else 0,
                        sheet_profiles=sheet_profiles,
                        notes=[f"Successfully profiled {len(sheet_profiles)} sheet(s)"]
                    )
                )
            except Exception as e:
                state["errors"] = state.get("errors", []) + [f"Failed to profile {artifact.name}: {e}"]
                state["workflow_status"] = "failed"
                return state
                
        state["workbook_insights"] = insights
        state["active_agent"] = "data_explorer"
        
        # Add assistant message to history
        messages = state.get("messages", [])
        messages.append({
            "role": "assistant",
            "content": f"Successfully profiled workbook with {sum(ins.sheet_count for ins in insights)} sheet(s)."
        })
        state["messages"] = messages
        
        return state

def data_explorer_node(state: ExcelWorkflowState) -> ExcelWorkflowState:
    return DataExplorerAgent().process(state)
