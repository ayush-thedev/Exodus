from langgraph.graph import StateGraph, END
from backend.agents.state import ExcelWorkflowState
from backend.agents.data_explorer import data_explorer_node
from backend.agents.planner import planner_node
from backend.agents.worker import worker_node
from backend.agents.reviewer import reviewer_node
from backend.agents.follow_up import follow_up_node

def after_exploration(state: ExcelWorkflowState) -> str:
    """Routes the workflow after workbook profiling."""
    req = state.get("user_request", "")
    if req and req.strip():
        return "planner"
    return "reviewer"

def should_continue(state: ExcelWorkflowState) -> str:
    """Checks the task queue to loop or finish."""
    queue = state.get("agent_queue", [])
    if queue and len(queue) > 0:
        return "worker"
    return "reviewer"

def build_workflow() -> StateGraph:
    workflow = StateGraph(ExcelWorkflowState)
    
    # 1. Register Nodes
    workflow.add_node("data_explorer", data_explorer_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("worker", worker_node)
    workflow.add_node("reviewer", reviewer_node)
    
    # 2. Setup Entry Point
    workflow.set_entry_point("data_explorer")
    
    # 3. Add Edges
    workflow.add_conditional_edges(
        "data_explorer",
        after_exploration,
        {
            "planner": "planner",
            "reviewer": "reviewer"
        }
    )
    
    workflow.add_conditional_edges(
        "planner",
        should_continue,
        {
            "worker": "worker",
            "reviewer": "reviewer"
        }
    )
    
    workflow.add_conditional_edges(
        "worker",
        should_continue,
        {
            "worker": "worker",
            "reviewer": "reviewer"
        }
    )
    
    workflow.add_edge("reviewer", END)
    
    return workflow.compile()

# Main workflow application instance
workflow_app = build_workflow()
