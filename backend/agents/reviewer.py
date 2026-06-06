import os
import pandas as pd
from pathlib import Path
from backend.agents.base import BaseAgent
from backend.agents.state import ExcelWorkflowState, FileArtifact, AgentResult
from backend.agents.prompts import REVIEWER_PROMPT
from backend.config import settings
from backend.core.utils import create_excel_report, embed_chart_in_excel

class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__("reviewer", REVIEWER_PROMPT)
        
    def process(self, state: ExcelWorkflowState) -> ExcelWorkflowState:
        workbook_insights = state.get("workbook_insights", [])
        user_request = state.get("user_request", "")
        agent_results = state.get("agent_results", {})
        
        # 1. Format profile and findings for LLM prompt
        profile_str = ""
        for insight in workbook_insights:
            profile_str += f"File: {insight.file_name} ({insight.sheet_count} sheets)\n"
            
        results_str = ""
        for tid, res in agent_results.items():
            results_str += f"Task {tid}: {res.summary}\n"
            
        prompt = self.system_prompt.format(
            workbook_profile=profile_str,
            user_request=user_request or "None (General Profile Summary)",
            agent_results=results_str or "No worker tasks were executed."
        )
        
        # 2. Generate summary report markdown
        summary_report = self.invoke(prompt)
        state["final_summary"] = summary_report
        
        # 3. Create Excel/CSV report file
        input_files = state.get("input_files", [])
        if input_files:
            primary_input = input_files[0]
            try:
                # Load primary dataframe to create structured report
                df = pd.read_excel(primary_input.path)
                
                # Setup output file info
                os.makedirs(settings.EXPORT_DIR, exist_ok=True)
                export_filename = f"report_{state.get('session_id', 'session')}_{primary_input.name}"
                export_path = Path(settings.EXPORT_DIR) / export_filename
                
                # Create base spreadsheet bytes
                analysis_results_dict = {
                    "summary": summary_report,
                    "findings": [res.summary for res in agent_results.values()]
                }
                report_bytes = create_excel_report(df, analysis_results_dict)
                
                # Embed any charts generated during tasks
                charts = state.get("shared_data", {}).get("charts", [])
                if charts:
                    try:
                        report_bytes = embed_chart_in_excel(report_bytes, charts, df)
                    except Exception as chart_err:
                        state["errors"] = state.get("errors", []) + [f"Failed to embed charts: {chart_err}"]
                
                # Write to disk
                with open(export_path, "wb") as f:
                    f.write(report_bytes)
                
                # Store output file artifact
                output_artifact = FileArtifact(
                    artifact_id=f"output_{primary_input.artifact_id}",
                    name=export_filename,
                    path=export_path,
                    source="generation"
                )
                state["output_files"] = state.get("output_files", []) + [output_artifact]
                
            except Exception as e:
                state["errors"] = state.get("errors", []) + [f"Reviewer report generation failed: {e}"]
                
        state["workflow_status"] = "completed"
        state["active_agent"] = "reviewer"
        
        self.add_message(state, "assistant", f"Workflow execution complete. Prepared the final report summary.")
        return state

def reviewer_node(state: ExcelWorkflowState) -> ExcelWorkflowState:
    return ReviewerAgent().process(state)
