import ast
import io
import sys
import contextlib
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Tuple

class SafetyVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors = []
        
    def visit_Import(self, node):
        self.errors.append("Imports (import ...) are not allowed in the sandbox.")
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        self.errors.append("Imports (from ... import ...) are not allowed in the sandbox.")
        self.generic_visit(node)
        
    def visit_ClassDef(self, node):
        self.errors.append("Class definitions are not allowed in the sandbox.")
        self.generic_visit(node)
        
    def visit_Try(self, node):
        self.errors.append("Try/except blocks are not allowed in the sandbox.")
        self.generic_visit(node)
        
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            name = node.func.id
            blacklisted = {
                "eval", "exec", "open", "__import__", "globals", "locals", 
                "getattr", "setattr", "delattr", "compile", "dir", "vars", 
                "exit", "quit", "breakpoint"
            }
            if name in blacklisted:
                self.errors.append(f"Function call '{name}' is forbidden in the sandbox.")
        elif isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            if attr.startswith('__'):
                self.errors.append(f"Dunder attribute access '{attr}' is forbidden in the sandbox.")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        attr = node.attr
        if attr.startswith('__'):
            self.errors.append(f"Dunder attribute access '{attr}' is forbidden in the sandbox.")
        self.generic_visit(node)

def validate_ast(code: str) -> Tuple[bool, str]:
    """
    Validates that a Python code string contains only safe constructs.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"Syntax Error: {e}"
        
    visitor = SafetyVisitor()
    visitor.visit(tree)
    if visitor.errors:
        return False, "\n".join(visitor.errors)
    return True, ""

def execute_code_sandbox(code: str, df_dict: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Executes Python code in a restricted namespace.
    Injects pandas (as pd), numpy (as np), plotly.express (as px), and plotly.graph_objects (as go).
    Also injects the DataFrames in df_dict.
    """
    # 1. AST Validation
    is_safe, error_msg = validate_ast(code)
    if not is_safe:
        return {"success": False, "error": f"AST Validation Failed:\n{error_msg}"}
        
    # 2. Setup environment
    allowed_builtins = {
        "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
        "enumerate": enumerate, "float": float, "int": int, "len": len,
        "list": list, "map": map, "max": max, "min": min, "range": range,
        "round": round, "set": set, "sorted": sorted, "str": str, "sum": sum,
        "tuple": tuple, "zip": zip, "print": print
    }
    
    local_ns = {
        "pd": pd,
        "np": np,
        "px": px,
        "go": go,
        "df_dict": df_dict
    }
    
    # Bind each sheet dataframe to its variable name if it's a valid identifier,
    # and bind the first one to 'df'
    first_df = None
    for sheet_name, df in df_dict.items():
        if first_df is None:
            first_df = df
        
        # Sanitize key name to make it a valid variable name if possible
        var_name = "".join(c if c.isalnum() else "_" for c in sheet_name)
        if var_name.isidentifier():
            local_ns[var_name] = df

    if first_df is not None:
        local_ns["df"] = first_df
        
    # Inject an empty result object
    local_ns["result"] = None
    local_ns["fig"] = None
    
    # 3. Capture stdout & Execute
    stdout_io = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout_io):
            compiled_code = compile(code, "<sandbox>", "exec")
            exec(compiled_code, {"__builtins__": allowed_builtins}, local_ns)
            
        captured_output = stdout_io.getvalue()
        
        result_val = local_ns.get("result")
        fig_val = local_ns.get("fig")
        
        return {
            "success": True,
            "result": result_val,
            "fig": fig_val,
            "stdout": captured_output,
            "variables": {k: v for k, v in local_ns.items() if k not in ["pd", "np", "px", "go", "__builtins__"]}
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Runtime Execution Error: {type(e).__name__}: {str(e)}",
            "stdout": stdout_io.getvalue()
        }
