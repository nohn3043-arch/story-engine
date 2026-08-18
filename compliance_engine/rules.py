"""规则引擎：加载规则库（JSON）并按文书类型匹配。

规则库为纯 JSON 配置，可外部替换/扩展（--rules-dir）。
匹配为决定论式：命中即产出 finding，不输出概率。
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import AuditFinding, DocType, RiskLevel

_DEFAULT_RULES_DIR = Path(__file__).parent / "rules"


class RuleEngine:
    def __init__(self, rules_dir: Optional[Path] = None):
        self.rules_dir = Path(rules_dir) if rules_dir else _DEFAULT_RULES_DIR
        self.rules: List[Dict[str, Any]] = []
        self._load_all()

    def _load_all(self) -> None:
        if not self.rules_dir.is_dir():
            raise FileNotFoundError(f"规则目录不存在: {self.rules_dir}")
        for f in sorted(self.rules_dir.glob("*.json")):
            self._load_file(f)

    def _load_file(self, path: Path) -> None:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        file_scope = data.get("doc_type")
        for rule in data.get("rules", []):
            rule = dict(rule)
            scope = rule.get("scope") or file_scope or "generic"
            rule["scope"] = scope
            self.rules.append(rule)

    def rules_for(self, doc_type: DocType) -> List[Dict[str, Any]]:
        return [r for r in self.rules if r.get("scope") in (doc_type.value, "generic")]

    def list_rules(self, doc_type: Optional[DocType] = None) -> List[Dict[str, Any]]:
        if doc_type is None:
            return list(self.rules)
        return self.rules_for(doc_type)

    def scan(self, text: str, doc_type: DocType) -> List[AuditFinding]:
        """对整篇文书做条款级扫描，返回全部命中 finding。"""
        findings: List[AuditFinding] = []
        for rule in self.rules_for(doc_type):
            findings.extend(self._apply(rule, text))
        return findings

    def _apply(self, rule: Dict[str, Any], text: str) -> List[AuditFinding]:
        kind = rule.get("kind", "risk_keywords")
        severity = _parse_severity(rule.get("severity", "WARNING"))
        if kind == "risk_keywords":
            return self._match_keywords(rule, text, severity)
        if kind == "forbidden_keywords":
            return self._match_keywords(rule, text, severity)
        if kind == "regex":
            return self._match_regex(rule, text, severity)
        return []

    def _match_keywords(
        self, rule: Dict[str, Any], text: str, severity: RiskLevel
    ) -> List[AuditFinding]:
        findings: List[AuditFinding] = []
        for kw in rule.get("patterns", []):
            if kw and kw in text:
                findings.append(
                    AuditFinding(
                        rule_id=rule["id"],
                        category=rule.get("category", "风险条款"),
                        severity=severity,
                        message=rule.get("message", f"命中风险词「{kw}」"),
                        suggestion=rule.get("suggestion", ""),
                        location="全文",
                        snippet=_snippet_around(text, kw),
                    )
                )
        return findings

    def _match_regex(
        self, rule: Dict[str, Any], text: str, severity: RiskLevel
    ) -> List[AuditFinding]:
        findings: List[AuditFinding] = []
        try:
            pat = re.compile(rule["pattern"])
        except re.error:
            return []
        for m in pat.finditer(text):
            findings.append(
                AuditFinding(
                    rule_id=rule["id"],
                    category=rule.get("category", "格式规范"),
                    severity=severity,
                    message=rule.get("message", f"命中模式「{m.group(0)}」"),
                    suggestion=rule.get("suggestion", ""),
                    location="全文",
                    snippet=m.group(0),
                )
            )
        return findings


def _parse_severity(s: str) -> RiskLevel:
    try:
        return RiskLevel[s.strip().upper()]
    except KeyError:
        return RiskLevel.WARNING


def _snippet_around(text: str, kw: str, radius: int = 18) -> str:
    idx = text.find(kw)
    if idx < 0:
        return kw
    start = max(0, idx - radius)
    end = min(len(text), idx + len(kw) + radius)
    return text[start:end]
