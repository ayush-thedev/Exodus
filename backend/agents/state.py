from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, TypedDict, List, Dict, Optional

@dataclass
class FileArtifact:
    artifact_id: str
    name: str
    path: Path
    mime_type: str = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    source: str = "upload"
    sheet_names: List[str] = field(default_factory=list)
    row_count: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentTask:
    task_id: str
    agent_name: str
    instructions: str
    inputs: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentResult:
    agent_name: str
    summary: str
    status: Literal["pending", "running", "completed", "failed"] = "completed"
    outputs: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[FileArtifact] = field(default_factory=list)

@dataclass
class SheetProfile:
    sheet_name: str
    row_count: int
    column_count: int
    headers: List[str] = field(default_factory=list)
    preview_rows: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class WorkbookInsight:
    artifact_id: str
    file_name: str
    file_path: Path
    sheet_count: int
    total_rows: int
    total_columns: int
    sheet_profiles: List[SheetProfile] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

@dataclass
class FollowUpResult:
    request: str
    workbook_name: str
    sheet_name: str
    generated_code: str
    result_kind: Literal["number", "text", "table", "none", "error"]
    result_value: Any = None
    summary: str = ""
    analysis_log: List[str] = field(default_factory=list)
    error: Optional[str] = None
    fig_base64: Optional[str] = None

class ExcelWorkflowState(TypedDict, total=False):
    session_id: str
    report_path: str
    user_request: str
    workflow_status: Literal["idle", "planning", "running", "reviewing", "completed", "failed"]
    input_files: List[FileArtifact]
    output_files: List[FileArtifact]
    agent_queue: List[AgentTask]
    agent_results: Dict[str, AgentResult]
    shared_data: Dict[str, Any]
    workbook_insights: List[WorkbookInsight]
    follow_up_request: str
    follow_up_result: Optional[FollowUpResult]
    analysis_log: List[str]
    notes: List[str]
    errors: List[str]
    active_agent: str
    final_summary: str
    messages: List[Dict[str, str]]  # Chat history: [{"role": "user/assistant", "content": "..."}]
