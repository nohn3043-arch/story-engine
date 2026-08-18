"""企业级文书合规审计引擎。

纯规则库、零第三方依赖、可离线运行。核心能力：
- 通用多类型文书审计（合同 / 制度 / 公文 / 通用）
- 条款级规则扫描 + 文档级审计（要素完整性 / 一致性 / 权利义务对等 / 格式）
- 责任闭环锚定与全链路可追溯
- HTML / JSON / Markdown 三格式报告
"""

from .engine import ComplianceEngine
from .models import AuditReport, DocType, RiskLevel
from .report import to_html, to_json, to_markdown

__all__ = [
    "ComplianceEngine",
    "AuditReport",
    "DocType",
    "RiskLevel",
    "to_html",
    "to_json",
    "to_markdown",
]

__version__ = "1.0.0"
