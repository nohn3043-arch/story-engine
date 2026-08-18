"""企业级文书合规审计引擎 · 核心数据模型。

沿用原业务引擎的精华：责任闭环锚定、风险分级、节点状态机、可追溯日志。
全部判定为决定论式（命中即判定），不输出概率估计。
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class RiskLevel(Enum):
    SAFE = auto()
    WARNING = auto()
    CRITICAL = auto()
    FATAL = auto()


class NodeStatus(Enum):
    RAW = auto()
    SCANNED = auto()
    AUDITED = auto()
    PRUNED = auto()
    ACTIVE = auto()


class DocType(Enum):
    CONTRACT = "contract"
    REGULATION = "regulation"
    OFFICIAL_DOC = "official_doc"
    GENERIC = "generic"

    @classmethod
    def from_str(cls, s: str) -> "DocType":
        try:
            return cls(s.strip().lower())
        except ValueError:
            return cls.GENERIC


@dataclass
class TraceLog:
    timestamp: str
    operation: str
    stage: str
    node_id: Optional[str]
    remark: str
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    @staticmethod
    def now(operation: str, stage: str, node_id: Optional[str], remark: str) -> "TraceLog":
        return TraceLog(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            operation=operation,
            stage=stage,
            node_id=node_id,
            remark=remark,
        )


@dataclass
class ResponsibilityAccount:
    """责任闭环锚定：每项审计动作绑定到具名责任节点（组织/角色/阶段）。"""

    organization: str
    role: str
    stage: str
    nonce: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    trace_chain: List[str] = field(default_factory=list)

    def bind_stage(self, stage: str) -> bool:
        self.trace_chain.append(f"{stage}|{uuid.uuid4().hex[:6]}")
        return True


@dataclass
class AuditFinding:
    rule_id: str
    category: str
    severity: RiskLevel
    message: str
    suggestion: str
    location: str
    snippet: str
    confidence: float = 1.0


@dataclass
class AuditNode:
    """文书中的审计单元：一条条款 / 一个段落 / 一个制度条目。"""

    node_id: str
    content: str
    section: str = ""
    findings: List[AuditFinding] = field(default_factory=list)
    status: NodeStatus = NodeStatus.RAW
    score: float = 100.0


@dataclass
class AuditReport:
    doc_type: DocType
    title: str
    overall_score: float
    passed: bool
    findings: List[AuditFinding]
    nodes: List[AuditNode]
    trace: List[TraceLog]
    responsibility: ResponsibilityAccount
    summary: Dict[str, Any]
    generated_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )
