import pandas as pd
from pathlib import Path
from backend.agents.base import BaseAgent
from backend.agents.state import ExcelWorkflowState, AgentResult, FileArtifact
from backend.agents.prompts import WORKER_PROMPT
from backend.core.sandbox import execute_code_sandbox

class WorkerAgent(BaseAgent):
    def __init__(self):
        super().__init__("worker", WORKER_PROMPT)
        
    def process(self, state: ExcelWorkflowState) -> ExcelWorkflowState:
        queue = state.get("agent_queue", [])
        if not queue:
            return state
            
        # Get the next task (pop it)
        task = queue.pop(0)
        state["agent_queue"] = queue
        
        # Load sheets from input_files into a df_dict
        df_dict = {}
        input_files = state.get("input_files", [])
        for artifact in input_files:
            file_path = Path(artifact.path)
            if file_path.exists():
                try:
                    xls = pd.ExcelFile(file_path)
                    for sheet in xls.sheet_names:
                        df_dict[sheet] = pd.read_excel(file_path, sheet_name=sheet)
                except Exception as e:
                    state["errors"] = state.get("errors", []) + [f"Worker failed to load sheets from {artifact.name}: {e}"]
                    
        # Active sheet from task inputs
        sheet_name = task.inputs.get("sheet_name")
        if not sheet_name and df_dict:
            sheet_name = list(df_dict.keys())[0]
            
        # Get previous agent results to format context
        previous_results = ""
        agent_results = state.get("agent_results", {})
        if agent_results is None:
            agent_results = {}
            
        for tid, res in agent_results.items():
            previous_results += f"Task {tid} ({res.agent_name}): {res.summary}\n"
            
        # Format workbook profile for context
        workbook_insights = state.get("workbook_insights", [])
        profile_str = ""
        for insight in workbook_insights:
            for sheet in insight.sheet_profiles:
                if sheet.sheet_name == sheet_name:
                    profile_str += f"Active Sheet: {sheet.sheet_name}\n"
                    profile_str += f"Headers: {sheet.headers}\n"
                    profile_str += f"Dimensions: {sheet.row_count} rows x {sheet.column_count} columns\n"
                    if sheet.preview_rows:
                        profile_str += f"Preview: {sheet.preview_rows[:2]}\n"
                        
        prompt = self.system_prompt.format(
            workbook_profile=profile_str,
            task_instructions=task.instructions,
            task_inputs=str(task.inputs),
            previous_outputs=previous_results,
            sheet_name=sheet_name or "Sheet1"
        )
        
        # Generate code
        response_str = self.invoke(prompt)
        code = self.extract_code(response_str)
        
        # Run code in sandbox
        exec_res = execute_code_sandbox(code, df_dict)
        
        if exec_res.get("success"):
            # Update state with variables and fig
            result_val = exec_res.get("result")
            fig_val = exec_res.get("fig")
            
            # Store figure in shared data
            if fig_val is not None:
                if "shared_data" not in state or state["shared_data"] is None:
                    state["shared_data"] = {}
                charts = state["shared_data"].get("charts", [])
                charts.append(fig_val)
                state["shared_data"]["charts"] = charts
                
            # Convert result dataframe to dict preview
            result_preview = ""
            result_data = {}
            if isinstance(result_val, pd.DataFrame):
                result_preview = f"DataFrame of shape {result_val.shape}"
                result_data = {"columns": list(result_val.columns), "data": result_val.head(10).to_dict(orient="records")}
            elif isinstance(result_val, pd.Series):
                result_preview = f"Series of length {len(result_val)}"
                result_data = {"data": result_val.head(10).to_dict()}
            elif result_val is not None:
                result_preview = str(result_val)
                result_data = {"value": result_val}
            else:
                result_preview = "Task execution succeeded with no return value."
                
            summary = f"Successfully executed task: {task.instructions}. Output summary: {result_preview}"
            
            # Record success
            agent_results[task.task_id] = AgentResult(
                agent_name="worker",
                summary=summary,
                status="completed",
                outputs=[exec_res.get("stdout", ""), code],
                data=result_data
            )
            
            self.add_message(state, "assistant", f"Executed task: {task.instructions}\nResults: {result_preview}")
        else:
            # Record failure
            error_msg = exec_res.get("error", "Unknown runtime error.")
            summary = f"Failed task: {task.instructions}. Error: {error_msg}"
            agent_results[task.task_id] = AgentResult(
                agent_name="worker",
                summary=summary,
                status="failed",
                outputs=[exec_res.get("stdout", ""), code]
            )
            state["errors"] = state.get("errors", []) + [error_msg]
            
            self.add_message(state, "assistant", f"Failed task execution: {task.instructions}\nError: {error_msg}")
            
        state["agent_results"] = agent_results
        state["active_agent"] = "worker"
        
        return state

def worker_node(state: ExcelWorkflowState) -> ExcelWorkflowState:
    return WorkerAgent().process(state)
