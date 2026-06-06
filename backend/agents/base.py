import re
from typing import Dict, Any, List, Optional
from backend.core.llm import llm_client

class BaseAgent:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.llm = llm_client
        
    def invoke(self, user_message: str, response_format: Optional[dict] = None) -> str:
        """Invoke the configured LLM with the agent's system prompt and user message."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]
        return self.llm.generate(messages, response_format=response_format)
        
    def add_message(self, state: Dict[str, Any], role: str, content: str) -> None:
        """Helper to append a message to the state's chat history."""
        messages = state.get("messages", [])
        if messages is None:
            messages = []
        messages.append({"role": role, "content": content})
        state["messages"] = messages
        
    def extract_code(self, response: str) -> str:
        """Extracts code block from markdown representation."""
        code_match = re.search(r'```python\n?(.*?)```', response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        code_match = re.search(r'```\n?(.*?)```', response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        return response.strip()
        
    def get_dataframe_info_str(self, df_info: Dict[str, Any]) -> str:
        """Format DataFrame metadata to inject into agent prompt contexts."""
        preview = df_info.get("preview", [])
        if not preview and "preview_rows" in df_info:
            preview = df_info["preview_rows"]
            
        preview_lines = [f"Row {i+1}: {row}" for i, row in enumerate(preview[:5])]
        return f"""
- Columns: {df_info.get('columns', [])}
- Types: {df_info.get('dtypes', df_info.get('headers', {}))}
- Shape: {df_info.get('shape', (0, 0))}
- Numeric columns: {df_info.get('numeric_columns', [])}
- Categorical columns: {df_info.get('categorical_columns', [])}
- Preview:
{chr(10).join(preview_lines)}
"""
