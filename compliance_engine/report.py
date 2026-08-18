"""报告生成：HTML（可视化）/ JSON（结构化）/ Markdown（简洁）。

HTML 报告内嵌样式，单文件可分享；JSON 供系统集成；Markdown 供文档归档。
"""

import json
from typing import Any, Dict

from .models import AuditReport, RiskLevel

_SEV_COLOR = {
    RiskLevel.FATAL: "#dc2626",
    RiskLevel.CRITICAL: "#ea580c",
    RiskLevel.WARNING: "#d97706",
    RiskLevel.SAFE: "#16a34a",
}
_SEV_LABEL = {
    RiskLevel.FATAL: "致命",
    RiskLevel.CRITICAL: "严重",
    RiskLevel.WARNING: "警告",
    RiskLevel.SAFE: "安全",
}


def to_dict(report: AuditReport) -> Dict[str, Any]:
    return {
        "doc_type": report.doc_type.value,
        "title": report.title,
        "overall_score": report.overall_score,
        "passed": report.passed,
        "generated_at": report.generated_at,
        "summary": report.summary,
        "responsibility": {
            "organization": report.responsibility.organization,
            "role": report.responsibility.role,
            "stage": report.responsibility.stage,
            "trace_chain": report.responsibility.trace_chain,
        },
        "findings": [
            {
                "rule_id": f.rule_id,
                "category": f.category,
                "severity": f.severity.name,
                "message": f.message,
                "suggestion": f.suggestion,
                "location": f.location,
                "snippet": f.snippet,
            }
            for f in report.findings
        ],
        "trace": [
            {
                "timestamp": t.timestamp,
                "operation": t.operation,
                "stage": t.stage,
                "node_id": t.node_id,
                "remark": t.remark,
            }
            for t in report.trace
        ],
    }


def to_json(report: AuditReport) -> str:
    return json.dumps(to_dict(report), ensure_ascii=False, indent=2)


def to_markdown(report: AuditReport) -> str:
    lines = [
        f"# 文书合规审计报告：{report.title}",
        "",
        f"- 文书类型：{report.doc_type.value}",
        f"- 综合评分：{report.overall_score:.0f} / 100",
        f"- 判定：{'通过' if report.passed else '不通过'}",
        f"- 审计时间：{report.generated_at}",
        f"- 责任节点：{report.responsibility.organization} / {report.responsibility.role}",
        "",
        "## 汇总",
        "",
        f"- 发现总数：{report.summary.get('total_findings', 0)}",
        f"- 按严重度：{_fmt_dict(report.summary.get('by_severity', {}))}",
        f"- 按维度：{_fmt_dict(report.summary.get('by_category', {}))}",
        "",
        "## 问题清单",
        "",
    ]
    if not report.findings:
        lines.append("未发现合规问题。")
    for f in sorted(report.findings, key=lambda x: x.severity.value):
        lines.append(
            f"- **[{_SEV_LABEL[f.severity]}] {f.category}** {f.message}"
            f"\n  - 位置：{f.location} | 命中：`{f.snippet or '—'}`"
            f"\n  - 建议：{f.suggestion}"
        )
    lines += ["", "## 审计追溯链", ""]
    for t in report.trace:
        lines.append(f"- `{t.timestamp}` {t.operation} | {t.remark}")
    return "\n".join(lines)


def to_html(report: AuditReport) -> str:
    sev_counts = report.summary.get("by_severity", {})
    cards = "".join(
        f'<span class="sev sev-{s.name.lower()}" style="background:{_SEV_COLOR[s]}">{_SEV_LABEL[s]} {sev_counts.get(s.name, 0)}</span>'
        for s in (RiskLevel.FATAL, RiskLevel.CRITICAL, RiskLevel.WARNING)
    )
    findings_html = ""
    for f in sorted(report.findings, key=lambda x: x.severity.value):
        findings_html += f"""
<div class="finding sev-{f.severity.name.lower()}">
  <div class="f-head">
    <span class="badge" style="background:{_SEV_COLOR[f.severity]}">{_SEV_LABEL[f.severity]}</span>
    <strong>{f.category}</strong>
    <span class="rule">{f.rule_id}</span>
  </div>
  <p class="f-msg">{f.message}</p>
  <p class="f-snip">命中：<code>{f.snippet or '—'}</code></p>
  <p class="f-loc">位置：{f.location}</p>
  <p class="f-sug">建议：{f.suggestion}</p>
</div>"""
    if not report.findings:
        findings_html = '<div class="finding sev-safe"><p class="f-msg">未发现合规问题。</p></div>'
    trace_html = "".join(
        f"<li><code>{t.timestamp}</code> {t.operation} — {t.remark}</li>"
        for t in report.trace
    )
    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>文书合规审计报告 · {report.title}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif; margin: 0; background: #f4f5f7; color: #1f2937; }}
.wrap {{ max-width: 900px; margin: 0 auto; padding: 32px 20px; }}
h1 {{ font-size: 24px; border-bottom: 3px solid #2563eb; padding-bottom: 12px; }}
.meta {{ display: flex; gap: 24px; flex-wrap: wrap; margin: 16px 0; color: #4b5563; font-size: 14px; }}
.score-box {{ background: #fff; border-radius: 12px; padding: 20px; margin: 16px 0; box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
.score {{ font-size: 42px; font-weight: 700; color: #2563eb; }}
.verdict {{ font-size: 16px; font-weight: 600; }}
.verdict.pass {{ color: #16a34a; }} .verdict.fail {{ color: #dc2626; }}
.sev {{ color: #fff; padding: 3px 10px; border-radius: 12px; font-size: 13px; margin-right: 8px; }}
h2 {{ font-size: 18px; margin-top: 28px; }}
.finding {{ background: #fff; border-radius: 10px; padding: 14px 16px; margin: 10px 0; box-shadow: 0 1px 3px rgba(0,0,0,.06); border-left: 5px solid #9ca3af; }}
.finding.sev-fatal {{ border-left-color: #dc2626; }} .finding.sev-critical {{ border-left-color: #ea580c; }}
.finding.sev-warning {{ border-left-color: #d97706; }} .finding.sev-safe {{ border-left-color: #16a34a; }}
.f-head {{ display: flex; align-items: center; gap: 10px; }}
.badge {{ color: #fff; padding: 2px 8px; border-radius: 10px; font-size: 12px; }}
.rule {{ color: #9ca3af; font-size: 12px; }}
.f-msg {{ margin: 8px 0 4px; font-weight: 600; }}
.f-snip, .f-loc, .f-sug {{ margin: 3px 0; font-size: 13px; color: #4b5563; }}
code {{ background: #f3f4f6; padding: 1px 6px; border-radius: 4px; }}
ul.trace {{ background: #fff; border-radius: 10px; padding: 16px 16px 16px 36px; box-shadow: 0 1px 3px rgba(0,0,0,.06); font-size: 13px; color: #4b5563; }}
</style>
</head>
<body>
<div class="wrap">
<h1>文书合规审计报告 · {report.title}</h1>
<div class="meta">
  <span>类型：{report.doc_type.value}</span>
  <span>责任节点：{report.responsibility.organization} / {report.responsibility.role}</span>
  <span>时间：{report.generated_at}</span>
</div>
<div class="score-box">
  <div class="score">{report.overall_score:.0f}<span style="font-size:16px;color:#9ca3af"> / 100</span></div>
  <div class="verdict {'pass' if report.passed else 'fail'}">判定：{'通过' if report.passed else '不通过'}</div>
  <div style="margin-top:10px">{cards}</div>
</div>
<h2>问题清单（{report.summary.get('total_findings', 0)}）</h2>
{findings_html}
<h2>审计追溯链</h2>
<ul class="trace">{trace_html}</ul>
</div>
</body>
</html>"""


def _fmt_dict(d: Dict[str, Any]) -> str:
    return "、".join(f"{k}={v}" for k, v in d.items()) if d else "无"
