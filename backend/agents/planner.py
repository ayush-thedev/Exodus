import json
from backend.agents.base import BaseAgent
from backend.agents.state import ExcelWorkflowState, AgentTask
from backend.agents.prompts import PLANNER_PROMPT

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__("planner", PLANNER_PROMPT)
        
    def process(self, state: ExcelWorkflowState) -> ExcelWorkflowState:
        workbook_insights = state.get("workbook_insights", [])
        user_request = state.get("user_request", "")
        
        if not user_request.strip():
            state["agent_queue"] = []
            return state
            
        profile_str = ""
        for insight in workbook_insights:
            profile_str += f"File: {insight.file_name} ({insight.sheet_count} sheets, total {insight.total_rows} rows)\n"
            for sheet in insight.sheet_profiles:
                profile_str += f"- Sheet: {sheet.sheet_name}\n"
                profile_str += f"  Rows: {sheet.row_count}, Columns: {sheet.column_count}\n"
                profile_str += f"  Headers: {sheet.headers}\n"
                if sheet.preview_rows:
                    profile_str += f"  Preview: {sheet.preview_rows[:2]}\n"
                    
        prompt = self.system_prompt.format(
            workbook_profile=profile_str,
            user_request=user_request
        )
        
        response_str = self.invoke(prompt, response_format={"type": "json_object"})
        
        tasks = []
        try:
            cleaned_resp = self.extract_code(response_str)
            raw_tasks = json.loads(cleaned_resp)
            if isinstance(raw_tasks, dict) and "tasks" in raw_tasks:
                raw_tasks = raw_tasks["tasks"]
                
            for t in raw_tasks:
                tasks.append(
                    AgentTask(
                        task_id=t.get("task_id", f"task_{len(tasks)+1}"),
                        agent_name=t.get("agent_name", "worker"),
                        instructions=t.get("instructions", ""),
                        inputs=t.get("inputs", {})
                    )
                )
        except Exception as e:
            sheet_name = workbook_insights[0].sheet_profiles[0].sheet_name if workbook_insights else "Sheet1"
            tasks = [
                AgentTask(
                    task_id="task_1",
                    agent_name="worker",
                    instructions=f"Perform descriptive analysis on user query: '{user_request}' for sheet '{sheet_name}' and save final DataFrame in 'result'.",
                    inputs={"sheet_name": sheet_name}
                )
            ]
            state["errors"] = state.get("errors", []) + [f"Planner parsing error: {e}. Generated fallback task."]
            
        state["agent_queue"] = tasks
        state["workflow_status"] = "running"
        state["active_agent"] = "planner"
        
        self.add_message(state, "assistant", f"Formulated an execution plan with {len(tasks)} analysis task(s).")
        return state

def planner_node(state: ExcelWorkflowState) -> ExcelWorkflowState:
    return PlannerAgent().process(state)
