"""内置演示：三份含合规问题的示例文书（合同 / 制度 / 公文），跑全流程并输出三格式报告。"""

from pathlib import Path
from typing import Dict, Optional, Tuple

from .engine import ComplianceEngine
from .models import DocType
from .report import to_html, to_json, to_markdown

SAMPLES: Dict[DocType, Tuple[str, str]] = {
    DocType.CONTRACT: (
        "示例采购合同",
        """采购合同

甲方：星辰科技有限公司
乙方：云帆供应链有限公司

第一条 合同标的
甲方向乙方采购办公设备一批，标的为办公设备及配套服务。

第二条 价款与支付
合同总价款为人民币200000元。甲方应于验收合格后30日内支付。
乙方应于收到款项后5日内开具发票。

第三条 履行期限
乙方应于2026年9月30日前完成交付。

第四条 违约责任
违约金为50000元。
若乙方逾期交付，违约金为80000元。
乙方加班无补偿，需自行安排进度。

第五条 争议解决
因本合同产生的争议，双方协商解决；协商不成的，提交甲方所在地人民法院诉讼。

第六条 其他
本合同最终解释权归甲方所有。
甲方有权调整交付计划，甲方有权变更验收标准，甲方有权单方解除合同。
乙方应尽快完成交付。""",
    ),
    DocType.REGULATION: (
        "示例差旅费用管理制度",
        """差旅费用管理制度

第一章 总则
第一条 目的
为规范公司差旅费用管理，加强费用控制，特制定本制度。

第二条 适用范围
本制度适用于公司全体员工。

第二章 职责与流程
第三条 职责
财务部负责差旅费用的审核与报销，行政部负责差旅审批。

第四条 报销流程
员工出差前须提交出差申请，经审批后出差；出差结束后提交报销单据，财务部在5个工作日内完成审核。

第五条 权限
相关部门可自行决定差旅标准，财务部有权调整报销比例。

第三章 罚则
第六条 责任追究
对虚报差旅费用的员工，视情况给予警告或处罚。

第七条 生效
本制度自发布之日起施行。""",
    ),
    DocType.OFFICIAL_DOC: (
        "关于申请采购办公设备的请示",
        """关于申请采购办公设备的请示

星辰科技〔2026〕12号

各部门：

为满足公司业务发展需要，拟采购办公设备一批，预算约人民币50万元，交付时间大约在2026.8.18前后，特此请示。

妥否，请批示。

星辰科技有限公司
2026年8月18日""",
    ),
}


def run_demo(out_dir: Path, doc_type: Optional[DocType] = None) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    engine = ComplianceEngine()

    for dt, (title, text) in SAMPLES.items():
        if doc_type is not None and dt != doc_type:
            continue
        report = engine.audit(text, dt, title)
        base = out_dir / f"demo_{dt.value}"
        (out_dir / f"{base.name}.html").write_text(to_html(report), encoding="utf-8")
        (out_dir / f"{base.name}.json").write_text(to_json(report), encoding="utf-8")
        (out_dir / f"{base.name}.md").write_text(to_markdown(report), encoding="utf-8")

        print(f"\n===== {title} [{dt.value}] =====")
        print(f"评分：{report.overall_score:.0f}/100 | 判定：{'通过' if report.passed else '不通过'}")
        print(f"发现：{report.summary['total_findings']} 条 | 严重度分布：{report.summary['by_severity']}")
        for f in report.findings:
            print(f"  [{f.severity.name}] {f.category} | {f.message}")
        print(f"报告：{base.name}.html / .json / .md")

    print("\n演示完成。")
