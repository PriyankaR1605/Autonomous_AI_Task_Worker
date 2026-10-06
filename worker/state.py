from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class StepStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class TaskStatus(str, Enum):
    INIT = "INIT"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Milestone(BaseModel):
    id: int
    title: str
    description: str
    status: StepStatus = StepStatus.PENDING
    result_summary: Optional[str] = None

class ActionStep(BaseModel):
    step_number: int
    thought: str = Field(description="Agent's reasoning behind choosing this action")
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    timestamp: str

class ApprovalRequest(BaseModel):
    required: bool = False
    reason: str
    proposed_action: str
    details: Dict[str, Any]
    user_approved: Optional[bool] = None
    user_feedback: Optional[str] = None

class VerificationResult(BaseModel):
    verified: bool = False
    source_values: Dict[str, Any] = Field(default_factory=dict, description="Values extracted from source invoice")
    target_values: Dict[str, Any] = Field(default_factory=dict, description="Values confirmed in the internal ERP")
    discrepancies: List[str] = Field(default_factory=list)
    verification_message: str = ""

class AgentState(BaseModel):
    task_id: str
    user_prompt: str
    status: TaskStatus = TaskStatus.INIT
    
    # Planning
    milestones: List[Milestone] = Field(default_factory=list)
    current_milestone_index: int = 0
    
    # Cognitive scratchpad & extracted entities
    working_memory: Dict[str, Any] = Field(default_factory=dict)
    
    # Audit log & execution trajectory
    steps_history: List[ActionStep] = Field(default_factory=list)
    
    # Failure & self-healing tracking
    consecutive_failures: int = 0
    retry_budget: int = 3
    
    # Human-in-the-loop gate
    pending_approval: Optional[ApprovalRequest] = None
    
    # Independent outcome verification
    verification: Optional[VerificationResult] = None
    
    # Final output
    final_summary: Optional[str] = None
    evidence_report_path: Optional[str] = None
