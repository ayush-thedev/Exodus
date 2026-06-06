import json
import pandas as pd
from pathlib import Path
from backend.agents.base import BaseAgent
from backend.agents.state import ExcelWorkflowState, FollowUpResult
from backend.agents.prompts import FOLLOW_UP_PROMPT
from backend.core.sandbox import execute_code_sandbox

class FollowUpAgent(BaseAgent):
    def __init__(self):
        super().__init__("follow_up", FOLLOW_UP_PROMPT)
        
    def process(self, state: ExcelWorkflowState) -> ExcelWorkflowState:
        workbook_insights = state.get("workbook_insights", [])
        follow_up_request = state.get("follow_up_request", "")
        chat_history = state.get("messages", [])
        
        if not follow_up_request.strip():
            return state
            
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
                    state["errors"] = state.get("errors", []) + [f"Follow-Up failed to load sheets: {e}"]
                    
        # Active sheet (default to the first sheet)
        sheet_name = list(df_dict.keys())[0] if df_dict else "Sheet1"
        workbook_name = input_files[0].name if input_files else "Workbook"
        
        # Format profile for LLM context
        profile_str = ""
        for insight in workbook_insights:
            profile_str += f"File: {insight.file_name}\n"
            for sheet in insight.sheet_profiles:
                profile_str += f"- Sheet: {sheet.sheet_name} ({sheet.row_count} rows, {sheet.column_count} cols)\n"
                profile_str += f"  Headers: {sheet.headers}\n"
                
        # Format chat history
        history_str = ""
        for msg in chat_history[-10:]:
            history_str += f"{msg['role'].capitalize()}: {msg['content']}\n"
            
        prompt = self.system_prompt.format(
            workbook_profile=profile_str,
            user_message=follow_up_request,
            conversation_history=history_str
        )
        
        # Invoke LLM
        response_str = self.invoke(prompt, response_format={"type": "json_object"})
        
        thought = ""
        requires_code = False
        generated_code = ""
        direct_response = ""
        
        try:
            cleaned_resp = self.extract_code(response_str)
            payload = json.loads(cleaned_resp)
            thought = payload.get("thought", "")
            requires_code = payload.get("requires_code", False)
            generated_code = payload.get("generated_code", "")
            direct_response = payload.get("direct_response", "")
        except Exception as e:
            requires_code = False
            direct_response = f"I failed to parse the agent's routing decision. Error: {e}"
            
        # Execute sandbox code if required
        if requires_code and generated_code:
            cleaned_code = self.extract_code(generated_code)
            exec_res = execute_code_sandbox(cleaned_code, df_dict)
            
            if exec_res.get("success"):
                result_val = exec_res.get("result")
                fig_val = exec_res.get("fig")
                
                # Determine result kind
                result_kind = "none"
                if isinstance(result_val, (pd.DataFrame, pd.Series)):
                    result_kind = "table"
                    preview_val = result_val.head(10).to_dict(orient="records") if isinstance(result_val, pd.DataFrame) else result_val.head(10).to_dict()
                elif isinstance(result_val, (int, float, complex)):
                    result_kind = "number"
                    preview_val = result_val
                elif isinstance(result_val, str):
                    result_kind = "text"
                    preview_val = result_val
                else:
                    result_kind = "text"
                    preview_val = str(result_val)
                    
                fig_status = "A visualization was successfully generated and displayed to the user." if fig_val is not None else "No visualization was generated."
                
                # Format final summary conversationally using the LLM
                summary_prompt = f"""
The user asked: "{follow_up_request}"
We ran this pandas code:
```python
{cleaned_code}
```
And got this stdout:
{exec_res.get('stdout')}

And this result value:
{preview_val}

Figure Status:
{fig_status}

Provide a polite and direct answer to the user explaining these findings. If a visualization was generated, do NOT apologize for missing visualizations or tell them to use .show(). Just summarize the data insights.
"""
                final_answer = self.llm.generate([
                    {"role": "system", "content": "You are a helpful data analyst explaining code execution outcomes to a user."},
                    {"role": "user", "content": summary_prompt}
                ])
                
                # Store chart if figure generated
                fig_base64_str = None
                if fig_val is not None:
                    if "shared_data" not in state or state["shared_data"] is None:
                        state["shared_data"] = {}
                    charts = state["shared_data"].get("charts", [])
                    charts.append(fig_val)
                    state["shared_data"]["charts"] = charts
                    
                    try:
                        import base64
                        img_bytes = fig_val.to_image(format="png", width=700, height=450)
                        fig_base64_str = base64.b64encode(img_bytes).decode('utf-8')
                    except Exception as e:
                        print(f"Failed to encode fig to base64: {e}")
                
                result_obj = FollowUpResult(
                    request=follow_up_request,
                    workbook_name=workbook_name,
                    sheet_name=sheet_name,
                    generated_code=cleaned_code,
                    result_kind=result_kind,
                    result_value=preview_val,
                    summary=final_answer,
                    analysis_log=[exec_res.get("stdout", "")],
                    fig_base64=fig_base64_str
                )
                
                # Append to report if report_path is in state
                report_path = state.get("report_path")
                if report_path:
                    from backend.core.utils import append_insight_to_report
                    append_insight_to_report(report_path, result_val, fig_val)
                
                state["follow_up_result"] = result_obj
                self.add_message(state, "assistant", final_answer)
            else:
                error_msg = exec_res.get("error", "Execution failed")
                result_obj = FollowUpResult(
                    request=follow_up_request,
                    workbook_name=workbook_name,
                    sheet_name=sheet_name,
                    generated_code=cleaned_code,
                    result_kind="error",
                    error=error_msg,
                    summary=f"I tried executing analysis code but hit an error:\n{error_msg}"
                )
                state["follow_up_result"] = result_obj
                self.add_message(state, "assistant", f"I tried executing code but encountered an error: {error_msg}")
        else:
            # Direct text answer
            result_obj = FollowUpResult(
                request=follow_up_request,
                workbook_name=workbook_name,
                sheet_name=sheet_name,
                generated_code="",
                result_kind="text",
                result_value=direct_response,
                summary=direct_response
            )
            state["follow_up_result"] = result_obj
            self.add_message(state, "assistant", direct_response)
            
        state["active_agent"] = "follow_up"
        return state

def follow_up_node(state: ExcelWorkflowState) -> ExcelWorkflowState:
    return FollowUpAgent().process(state)
