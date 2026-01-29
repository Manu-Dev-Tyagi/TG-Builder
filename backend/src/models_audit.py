from typing import List, Optional, Literal
from pydantic import BaseModel
from datetime import datetime

Engine = Literal["ENGINE_A", "ENGINE_B", "ORCHESTRATOR", "SCORING", "BUDGET"]

class AuditEntry(BaseModel):
    """A single step in the project audit trail (Review Point 6)"""
    timestamp: str
    engine: Engine
    decision: str
    reason: str

class ProjectAuditTrail(BaseModel):
    """Full chronological project audit log"""
    project_id: str
    entries: List[AuditEntry] = []
    
    def add(self, engine: Engine, decision: str, reason: str):
        self.entries.append(AuditEntry(
            timestamp=datetime.now().isoformat(),
            engine=engine,
            decision=decision,
            reason=reason
        ))
