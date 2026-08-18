"""文档级审计器：要素完整性 / 一致性 / 权利义务对等 / 公文格式。

与规则引擎（条款级命中）互补：这些审计需要整篇文书的跨段信息。
"""

import re
from typing import Dict, List

from .models import AuditFinding, DocType, RiskLevel

# 各文书类型的必备要素（关键词组，全部缺失任一即告警）
_COMPLETENESS: Dict[DocType, List[Dict[str, object]]] = {
    DocType.CONTRACT: [
        {"name": "当事人", "keywords": ["甲方", "乙方", "当事人"]},
        {"name": "标的", "keywords": ["标的", "项目", "服务", "货物", "产品"]},
        {"name": "价款", "keywords": ["价款", "金额", "费用", "价格", "报酬"]},
        {"name": "履行期限", "keywords": ["期限", "日期", "时间", "交付", "完成"]},
        {"name": "违约责任", "keywords": ["违约"]},
        {"name": "争议解决", "keywords": ["争议", "仲裁", "诉讼", "法院", "管辖"]},
    ],
    DocType.REGULATION: [
        {"name": "目的", "keywords": ["目的", "为规范", "为加强", "为进一步"]},
        {"name": "适用范围", "keywords": ["适用范围", "适用于", "本办法", "本制度"]},
        {"name": "职责", "keywords": ["职责", "负责", "承担"]},
        {"name": "流程", "keywords": ["流程", "程序", "步骤", "办理"]},
        {"name": "罚则", "keywords": ["罚则", "处罚", "奖惩", "责任追究", "考核"]},
        {"name": "生效条款", "keywords": ["生效", "施行", "发布之日起", "自发布"]},
    ],
    DocType.OFFICIAL_DOC: [
        {"name": "标题", "keywords": ["关于"]},
        {"name": "主送机关", "keywords": ["各", "单位", "部门", "处室"]},
        {"name": "成文日期", "keywords": ["年", "月", "日"]},
        {"name": "文号", "keywords": ["〔", "["]},
    ],
    DocType.GENERIC: [],
}

_ASSIGN_RE = re.compile(
    r"([\u4e00-\u9fa5]{2,8})(?:为|是|：)([0-9]{2,}[年月日元%]|[一二三四五六七八九十百千]+[年月日元%])"
)

_PARTY_RIGHT_RE = re.compile(r"(甲方|乙方)(?:有权|可|可以|应)")
_PARTY_DUTY_RE = re.compile(r"(甲方|乙方)(?:应|须|应当|有义务)")


class CompletenessAuditor:
    """要素完整性：必备要素缺失即告警（决定论：缺失=命中）。"""

    def audit(self, text: str, doc_type: DocType) -> List[AuditFinding]:
        findings: List[AuditFinding] = []
        for item in _COMPLETENESS.get(doc_type, []):
            name = item["name"]
            keywords = item["keywords"]
            if not any(k in text for k in keywords):
                findings.append(
                    AuditFinding(
                        rule_id=f"COMPLETE-{doc_type.value}",
                        category="要素完整性",
                        severity=RiskLevel.CRITICAL,
                        message=f"缺少必备要素：{name}",
                        suggestion=f"补充「{name}」相关内容（如：{' / '.join(keywords[:3])}）",
                        location="全文",
                        snippet="",
                    )
                )
        return findings


class ConsistencyAuditor:
    """一致性：同一赋值短语出现多次但取值不同 → 前后矛盾。"""

    def audit(self, text: str, doc_type: DocType) -> List[AuditFinding]:
        groups: Dict[str, List[str]] = {}
        for m in _ASSIGN_RE.finditer(text):
            key, val = m.group(1), m.group(2)
            groups.setdefault(key, []).append(val)
        findings: List[AuditFinding] = []
        for key, vals in groups.items():
            unique = list(dict.fromkeys(vals))
            if len(unique) > 1:
                findings.append(
                    AuditFinding(
                        rule_id=f"CONSIST-{doc_type.value}",
                        category="一致性",
                        severity=RiskLevel.CRITICAL,
                        message=f"「{key}」前后取值矛盾：{' / '.join(unique)}",
                        suggestion="核对并统一为单一取值",
                        location="全文",
                        snippet=f"{key}为{' / '.join(unique)}",
                    )
                )
        return findings


class BalanceAuditor:
    """权利义务对等（合同）：甲方权利词显著多于乙方 → 失衡。"""

    def audit(self, text: str, doc_type: DocType) -> List[AuditFinding]:
        if doc_type != DocType.CONTRACT:
            return []
        rights = {"甲方": 0, "乙方": 0}
        for m in _PARTY_RIGHT_RE.finditer(text):
            rights[m.group(1)] += 1
        duties = {"甲方": 0, "乙方": 0}
        for m in _PARTY_DUTY_RE.finditer(text):
            duties[m.group(1)] += 1
        imbalance = rights["甲方"] - rights["乙方"]
        findings: List[AuditFinding] = []
        if imbalance >= 2:
            findings.append(
                AuditFinding(
                    rule_id="BALANCE-CONTRACT",
                    category="权利义务对等",
                    severity=RiskLevel.WARNING,
                    message=(
                        f"权利义务失衡：甲方权利表述 {rights['甲方']} 处，"
                        f"乙方 {rights['乙方']} 处（差 {imbalance}）"
                    ),
                    suggestion="检查是否存在单方优势条款，补充乙方对等权利",
                    location="全文",
                    snippet=f"甲方有权×{rights['甲方']} / 乙方有权×{rights['乙方']}",
                )
            )
        return findings


class FormatAuditor:
    """公文格式：文号缺失、落款缺失。"""

    def audit(self, text: str, doc_type: DocType) -> List[AuditFinding]:
        if doc_type != DocType.OFFICIAL_DOC:
            return []
        findings: List[AuditFinding] = []
        if "〔" not in text and "[" not in text:
            findings.append(
                AuditFinding(
                    rule_id="FORMAT-OFFICIAL",
                    category="格式规范",
                    severity=RiskLevel.CRITICAL,
                    message="缺少公文文号（如：×发〔2026〕×号）",
                    suggestion="补充规范文号",
                    location="标题下方",
                    snippet="",
                )
            )
        if not re.search(r"\d{4}年\d{1,2}月\d{1,2}日", text):
            findings.append(
                AuditFinding(
                    rule_id="FORMAT-OFFICIAL",
                    category="格式规范",
                    severity=RiskLevel.WARNING,
                    message="缺少成文日期（YYYY年MM月DD日）",
                    suggestion="在落款处补充成文日期",
                    location="落款",
                    snippet="",
                )
            )
        return findings
