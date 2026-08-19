import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict
from enum import Enum, auto


# =============================================================================
# 基础工具与序列化
# =============================================================================
def _json_default(obj):
    if isinstance(obj, Enum):
        return obj.name
    if isinstance(obj, set):
        return list(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


# =============================================================================
# 合同条款分类枚举
# =============================================================================
class ContractClauseType(Enum):
    """合同条款分类，叙事剥离阶段自动识别"""

    PAYMENT = auto()  # 付款条款
    ACCEPTANCE = auto()  # 验收条款
    DELIVERY = auto()  # 交付条款
    BREACH = auto()  # 违约条款
    TERMINATION = auto()  # 终止/解除条款
    LIABILITY = auto()  # 责任/赔偿条款
    CONFIDENTIALITY = auto()  # 保密条款
    INTELLECTUAL_PROPERTY = auto()  # 知识产权条款
    FORCE_MAJEURE = auto()  # 不可抗力条款
    DISPUTE_RESOLUTION = auto()  # 争议解决条款
    WARRANTY = auto()  # 保证/质保条款
    EFFECTIVENESS = auto()  # 生效条款
    OTHER = auto()  # 其他条款


# =============================================================================
# 第二视角因果推理引擎 V2.1（决定论内核，无概率化推测）
# 五步算子：叙事剥离 → 内隐假设透视 → 脆弱性对冲 → 责任闭环锚定 → 因果重构
# 企业版：合同审查专用实现。
# =============================================================================
class SecondPerspectiveCausalEngine:
    """决定论因果推理：仅做因果链的结构性判定，不输出概率估计。"""

    # —— 合同审查专用事实字典 ——
    _CONTRACT_PAYMENT_HINTS = [
        "付款",
        "支付",
        "缴纳",
        "报酬",
        "费用",
        "价款",
        "结算",
        "分期付款",
        "预付款",
        "尾款",
    ]
    _CONTRACT_ACCEPTANCE_HINTS = [
        "验收",
        "检验",
        "测试",
        "确认",
        "合格",
        "达标",
        "质量标准",
        "验收标准",
    ]
    _CONTRACT_DELIVERY_HINTS = ["交付", "移交", "提交", "运送", "提供", "完成交付"]
    _CONTRACT_BREACH_HINTS = [
        "违约",
        "违反",
        "未按",
        "未履行",
        "逾期",
        "迟延",
        "不履行",
        "怠于",
    ]
    _CONTRACT_TERMINATION_HINTS = [
        "终止",
        "解除",
        "撤销",
        "解除合同",
        "终止合同",
        "单方解除",
    ]
    _CONTRACT_LIABILITY_HINTS = [
        "赔偿",
        "承担责任",
        "违约金",
        "损失赔偿",
        "赔偿金",
        "连带责任",
    ]
    _CONTRACT_CONFIDENTIALITY_HINTS = [
        "保密",
        "机密",
        "泄露",
        "信息披露",
        "保密义务",
        "保密期限",
    ]
    _CONTRACT_IP_HINTS = [
        "知识产权",
        "专利",
        "著作权",
        "商标",
        "所有权",
        "使用权",
        "许可",
    ]
    _CONTRACT_FORCE_MAJEURE_HINTS = [
        "不可抗力",
        "地震",
        "战争",
        "疫情",
        "自然灾害",
        "政府行为",
    ]
    _CONTRACT_DISPUTE_HINTS = ["争议", "纠纷", "仲裁", "诉讼", "管辖", "管辖权", "法院"]
    _CONTRACT_NOTICE_HINTS = ["通知", "书面通知", "提前", "通知期限", "告知"]
    _CONTRACT_LIMITATION_HINTS = [
        "时效",
        "诉讼时效",
        "除斥期间",
        "期限届满",
        "时效经过",
    ]

    @classmethod
    def _classify_clause_type(
        cls, text: str, conclusion: str = ""
    ) -> "ContractClauseType":
        """合同条款类型自动识别。
        优先按 conclusion（条款核心行为）判定，再按 full text 兜底。
        优先级：TERMINATION > BREACH > LIABILITY > DISPUTE > FORCE_MAJEURE >
                ACCEPTANCE > DELIVERY > CONFIDENTIALITY > IP > PAYMENT > OTHER
        确保交付/违约/终止等特定类型不被 PAYMENT 的前提词遮蔽。"""
        # 优先检查 conclusion，再检查 full text
        for source_text in (conclusion, text):
            if not source_text:
                continue
            # 按特定性从高到低检查
            for hints, clause_type in [
                (cls._CONTRACT_TERMINATION_HINTS, ContractClauseType.TERMINATION),
                (cls._CONTRACT_BREACH_HINTS, ContractClauseType.BREACH),
                (cls._CONTRACT_LIABILITY_HINTS, ContractClauseType.LIABILITY),
                (cls._CONTRACT_DISPUTE_HINTS, ContractClauseType.DISPUTE_RESOLUTION),
                (cls._CONTRACT_FORCE_MAJEURE_HINTS, ContractClauseType.FORCE_MAJEURE),
                (cls._CONTRACT_ACCEPTANCE_HINTS, ContractClauseType.ACCEPTANCE),
                (cls._CONTRACT_DELIVERY_HINTS, ContractClauseType.DELIVERY),
                (
                    cls._CONTRACT_CONFIDENTIALITY_HINTS,
                    ContractClauseType.CONFIDENTIALITY,
                ),
                (cls._CONTRACT_IP_HINTS, ContractClauseType.INTELLECTUAL_PROPERTY),
                (cls._CONTRACT_PAYMENT_HINTS, ContractClauseType.PAYMENT),
            ]:
                for hint in hints:
                    if hint in source_text:
                        return clause_type
            # conclusion 没命中则检查 full text（第二轮循环）
            if source_text == conclusion:
                continue
            break
        return ContractClauseType.OTHER

    # =====================================================================
    # 合同审查专用方法（V2 假设探测 + V3 崩溃判定 + V4 责任锚定 + V5 重构）
    # =====================================================================

    def contract_clause_stripping(self, clauses):
        """合同条款叙事剥离：识别条款类型、标记前提/结论、检测悬空条款。
        输入 clauses: List[Dict{id, premise, conclusion, party}]。
        输出因果事件链，含 clause_type 标记。"""
        chain = []
        seen_parties = set()
        all_clause_texts = []
        for i, cl in enumerate(clauses):
            cl = dict(cl)
            cl.setdefault("id", f"C{i:03d}")
            cl.setdefault("party", "")
            text = cl.get("premise", "") + cl.get("conclusion", "")
            cl["clause_type"] = self._classify_clause_type(
                text, cl.get("conclusion", "")
            ).name
            party = cl["party"] or self._infer_character(text)
            cl["character"] = party
            if party:
                seen_parties.add(party)
            all_clause_texts.append(text)
            chain.append(cl)
        # 第二轮：检测条款间依赖悬空
        for i, cl in enumerate(chain):
            text = cl.get("premise", "") + cl.get("conclusion", "")
            ct = cl["clause_type"]
            has_payment = any(h in text for h in self._CONTRACT_PAYMENT_HINTS)
            has_acceptance = any(
                h in t
                for t in all_clause_texts
                for h in self._CONTRACT_ACCEPTANCE_HINTS
            )
            has_breach = any(
                h in t for t in all_clause_texts for h in self._CONTRACT_BREACH_HINTS
            )
            has_liability = any(
                h in t for t in all_clause_texts for h in self._CONTRACT_LIABILITY_HINTS
            )
            has_obligation = any(
                h in t
                for t in all_clause_texts
                for h in (
                    self._CONTRACT_PAYMENT_HINTS
                    + self._CONTRACT_DELIVERY_HINTS
                    + self._CONTRACT_CONFIDENTIALITY_HINTS
                )
            )
            has_notice = any(
                h in t for t in all_clause_texts for h in self._CONTRACT_NOTICE_HINTS
            )
            has_dispute = any(
                h in t for t in all_clause_texts for h in self._CONTRACT_DISPUTE_HINTS
            )
            has_force_majeure = any(
                h in t
                for t in all_clause_texts
                for h in self._CONTRACT_FORCE_MAJEURE_HINTS
            )

            dangling_deps = []
            if ct == "PAYMENT" and not has_acceptance:
                dangling_deps.append("PAYMENT_WITHOUT_ACCEPTANCE")
            if ct == "BREACH" and not has_obligation:
                dangling_deps.append("BREACH_WITHOUT_OBLIGATION")
            if ct == "LIABILITY" and not has_breach:
                dangling_deps.append("LIABILITY_WITHOUT_BREACH")
            if ct == "TERMINATION" and not has_notice:
                dangling_deps.append("TERMINATION_WITHOUT_NOTICE")
            cl["dangling_deps"] = dangling_deps
            cl["dangling"] = len(dangling_deps) > 0
            # 全局缺失检测
            cl["missing_globals"] = []
            if not has_dispute:
                cl["missing_globals"].append("DISPUTE_RESOLUTION")
            if not has_force_majeure:
                cl["missing_globals"].append("FORCE_MAJEURE")
        return chain

    def contract_assumption_probe(self, chain):
        """合同假设透视：逆反校验每条条款的内隐前提。
        付款假设验收标准已定义；违约假设义务条款存在；责任假设违约条款存在。"""
        all_texts = [cl.get("premise", "") + cl.get("conclusion", "") for cl in chain]
        all_text_joined = "".join(all_texts)
        for cl in chain:
            text = cl.get("premise", "") + cl.get("conclusion", "")
            assumptions = []
            ct = cl.get("clause_type", "OTHER")

            if ct == "PAYMENT":
                has_acceptance = any(
                    h in all_text_joined for h in self._CONTRACT_ACCEPTANCE_HINTS
                )
                assumptions.append(
                    {
                        "content": "付款义务以验收合格为前提",
                        "reverse_check": "撤除验收条款 -> 付款条件无判定标准，义务触发节点缺失",
                        "collapse": "INEVITABLE" if not has_acceptance else "STABLE",
                    }
                )
                has_delivery = any(
                    h in all_text_joined for h in self._CONTRACT_DELIVERY_HINTS
                )
                assumptions.append(
                    {
                        "content": "付款以交付完成为时序前提",
                        "reverse_check": "撤除交付条款 -> 付款时序无法确定，先付后付无据",
                        "collapse": "CONDITIONAL" if not has_delivery else "STABLE",
                    }
                )

            if ct == "BREACH":
                has_obligation = (
                    any(h in all_text_joined for h in self._CONTRACT_PAYMENT_HINTS)
                    or any(h in all_text_joined for h in self._CONTRACT_DELIVERY_HINTS)
                    or any(
                        h in all_text_joined
                        for h in self._CONTRACT_CONFIDENTIALITY_HINTS
                    )
                )
                assumptions.append(
                    {
                        "content": "违约以有效义务条款存在为前提",
                        "reverse_check": "撤除义务条款 -> 违约判定无基准，责任真空",
                        "collapse": "INEVITABLE" if not has_obligation else "STABLE",
                    }
                )

            if ct == "LIABILITY":
                has_breach = any(
                    h in all_text_joined for h in self._CONTRACT_BREACH_HINTS
                )
                assumptions.append(
                    {
                        "content": "赔偿责任以违约事实成立为前提",
                        "reverse_check": "撤除违约条款 -> 赔偿无触发条件，责任链断裂",
                        "collapse": "INEVITABLE" if not has_breach else "STABLE",
                    }
                )

            if ct == "TERMINATION":
                has_notice = any(
                    h in all_text_joined for h in self._CONTRACT_NOTICE_HINTS
                )
                assumptions.append(
                    {
                        "content": "终止权以通知程序为行使前提",
                        "reverse_check": "撤除通知条款 -> 终止程序缺失，单方终止无程序保障",
                        "collapse": "INEVITABLE" if not has_notice else "STABLE",
                    }
                )

            if ct == "CONFIDENTIALITY":
                has_scope = any(h in text for h in ("范围", "期限", "期间", "地域"))
                assumptions.append(
                    {
                        "content": "保密义务以范围和期限明确为可执行前提",
                        "reverse_check": "撤除范围/期限 -> 保密义务无边无际，无法执行",
                        "collapse": "CONDITIONAL" if not has_scope else "STABLE",
                    }
                )

            if ct == "DISPUTE_RESOLUTION":
                has_jurisdiction = any(
                    h in text for h in ("管辖", "法院", "仲裁机构", "仲裁地")
                )
                assumptions.append(
                    {
                        "content": "争议解决以管辖/仲裁约定明确为前提",
                        "reverse_check": "撤除管辖约定 -> 争议解决无机构，程序悬空",
                        "collapse": "INEVITABLE" if not has_jurisdiction else "STABLE",
                    }
                )

            # 时效检测
            has_limitation = any(
                h in all_text_joined for h in self._CONTRACT_LIMITATION_HINTS
            )
            if ct in ("LIABILITY", "BREACH") and not has_limitation:
                assumptions.append(
                    {
                        "content": "违约/责任条款应约定诉讼时效或适用法定时效",
                        "reverse_check": "撤除时效约定 -> 权利行使期限不明，时效风险",
                        "collapse": "CONDITIONAL",
                    }
                )

            cl["assumptions"] = assumptions
        return chain

    def contract_vulnerability_hedge(self, chain):
        """合同崩溃判定：责任真空=INEVITABLE，条款冲突=CONDITIONAL，时效缺失=CONDITIONAL。
        非概率判定，仅做结构性二元事实校验。"""
        weakest, weakest_score = None, -1.0
        global_missing = set()
        for cl in chain:
            frag = 0
            for dep in cl.get("dangling_deps", []):
                if (
                    dep.endswith("WITHOUT_OBLIGATION")
                    or dep.endswith("WITHOUT_BREACH")
                    or dep.endswith("WITHOUT_NOTICE")
                ):
                    frag += 3  # 责任真空 = 必然崩溃
                else:
                    frag += 1  # 条件缺失 = 条件性崩溃
            for a in cl.get("assumptions", []):
                if a["collapse"] == "INEVITABLE":
                    frag += 3
                elif a["collapse"] == "CONDITIONAL":
                    frag += 1
            for missing in cl.get("missing_globals", []):
                global_missing.add(missing)
                frag += 1
            cl["fragility"] = frag
            if frag > weakest_score:
                weakest_score, weakest = frag, cl

        # 全局缺失扣分
        global_frag = len(global_missing) * 2

        if weakest is None and not global_missing:
            verdict = "STABLE"
        elif weakest_score >= 3 or global_frag >= 4:
            verdict = "INEVITABLE_COLLAPSE"
        elif weakest_score >= 1 or global_frag >= 2:
            verdict = "CONDITIONAL_COLLAPSE"
        else:
            verdict = "STABLE"

        return {
            "weakest_variable": weakest["id"] if weakest else None,
            "weakest_clause": weakest,
            "weakest_clause_type": weakest["clause_type"] if weakest else None,
            "collapse_verdict": verdict,
            "global_missing": list(global_missing),
            "chain_fragility": [
                {
                    "id": cl["id"],
                    "clause_type": cl.get("clause_type"),
                    "fragility": cl.get("fragility", 0),
                    "dangling_deps": cl.get("dangling_deps", []),
                }
                for cl in chain
            ],
        }

    def contract_responsibility_anchor(self, chain):
        """合同责任闭环锚定：每条条款的责任主体、义务指向、最小决策单元。"""
        anchors = []
        for idx, cl in enumerate(chain):
            party = cl.get("party", "") or cl.get("character", "")
            clause_type = cl.get("clause_type", "OTHER")
            conclusion = cl.get("conclusion", "")
            action = self._extract_contract_action(conclusion, clause_type)
            counterparty = cl.get("counterparty", "")
            anchors.append(
                {
                    "clause_id": cl["id"],
                    "position": idx,
                    "clause_type": clause_type,
                    "accountable": party,
                    "counterparty": counterparty,
                    "decision_unit": f"{party}->{action}" if party else action,
                    "premise": cl.get("premise", ""),
                    "conclusion": cl.get("conclusion", ""),
                }
            )
        return anchors

    def contract_causal_reconstruction(
        self, chain, fix_vars, target_state="合同因果自洽"
    ):
        """合同因果重构：注入修正变量（补充条款），校验收敛。"""
        fixed_ids = set()
        for cl in chain:
            for fix in fix_vars or []:
                if cl["id"] == fix.get("target_id") or fix.get("apply_to") == "all":
                    cl["premise"] = (
                        cl.get("premise", "") + "；" + fix.get("adds_premise", "")
                    ).strip("；")
                    cl["dangling"] = False
                    cl["dangling_deps"] = []
                    fixed_ids.add(cl["id"])
        residual = []
        for cl in chain:
            for dep in cl.get("dangling_deps", []):
                if cl["id"] not in fixed_ids:
                    residual.append(
                        f"条款{cl['id']}({cl.get('clause_type', '')})依赖悬空：{dep}"
                    )
            for a in cl.get("assumptions", []):
                if a["collapse"] == "INEVITABLE" and not fix_vars:
                    residual.append(f"条款{cl['id']}关键预设不可逆撤除：{a['content']}")
        if residual:
            return {
                "converged": False,
                "diagnosis": "[中断：合同因果链未收敛] " + "；".join(residual),
                "fixed_ids": list(fixed_ids),
                "suggested_fixes": self._suggest_contract_fixes(chain),
            }
        return {
            "converged": True,
            "target_state": target_state,
            "diagnosis": f"合同因果链收敛至目标稳态：{target_state}",
            "fixed_ids": list(fixed_ids),
        }

    def _extract_contract_action(self, conclusion: str, clause_type: str) -> str:
        """提取合同条款中的核心行为动词。"""
        type_to_hints = {
            "PAYMENT": self._CONTRACT_PAYMENT_HINTS,
            "ACCEPTANCE": self._CONTRACT_ACCEPTANCE_HINTS,
            "DELIVERY": self._CONTRACT_DELIVERY_HINTS,
            "BREACH": self._CONTRACT_BREACH_HINTS,
            "TERMINATION": self._CONTRACT_TERMINATION_HINTS,
            "LIABILITY": self._CONTRACT_LIABILITY_HINTS,
            "CONFIDENTIALITY": self._CONTRACT_CONFIDENTIALITY_HINTS,
            "INTELLECTUAL_PROPERTY": self._CONTRACT_IP_HINTS,
            "FORCE_MAJEURE": self._CONTRACT_FORCE_MAJEURE_HINTS,
            "DISPUTE_RESOLUTION": self._CONTRACT_DISPUTE_HINTS,
        }
        hints = type_to_hints.get(clause_type, [])
        for h in hints:
            if h in conclusion:
                return h
        return conclusion[:15]

    def _suggest_contract_fixes(self, chain) -> List[Dict[str, str]]:
        """根据悬空依赖生成补充条款建议。"""
        suggestions = []
        for cl in chain:
            for dep in cl.get("dangling_deps", []):
                if dep == "PAYMENT_WITHOUT_ACCEPTANCE":
                    suggestions.append(
                        {
                            "target_id": cl["id"],
                            "fix_type": "ADD_ACCEPTANCE_CLAUSE",
                            "adds_premise": "补充验收条款：明确验收标准、验收期限、不合格处理方式",
                        }
                    )
                elif dep == "BREACH_WITHOUT_OBLIGATION":
                    suggestions.append(
                        {
                            "target_id": cl["id"],
                            "fix_type": "ADD_OBLIGATION_CLAUSE",
                            "adds_premise": "补充义务条款：明确付款/交付/保密等具体义务内容及履行标准",
                        }
                    )
                elif dep == "LIABILITY_WITHOUT_BREACH":
                    suggestions.append(
                        {
                            "target_id": cl["id"],
                            "fix_type": "ADD_BREACH_CLAUSE",
                            "adds_premise": "补充违约条款：明确违约情形认定、违约金计算方式",
                        }
                    )
                elif dep == "TERMINATION_WITHOUT_NOTICE":
                    suggestions.append(
                        {
                            "target_id": cl["id"],
                            "fix_type": "ADD_NOTICE_CLAUSE",
                            "adds_premise": "补充通知条款：明确通知方式、提前期限、送达地址",
                        }
                    )
            for missing in cl.get("missing_globals", []):
                if missing == "DISPUTE_RESOLUTION":
                    suggestions.append(
                        {
                            "target_id": "GLOBAL",
                            "fix_type": "ADD_DISPUTE_CLAUSE",
                            "adds_premise": "补充争议解决条款：约定管辖法院或仲裁机构",
                        }
                    )
                elif missing == "FORCE_MAJEURE":
                    suggestions.append(
                        {
                            "target_id": "GLOBAL",
                            "fix_type": "ADD_FORCE_MAJEURE_CLAUSE",
                            "adds_premise": "补充不可抗力条款：定义范围、通知义务、免责范围",
                        }
                    )
        return suggestions

    # —— 内部工具 ——
    def _infer_character(self, text):
        """兜底角色推断：当事件未显式声明 character 时，提取首个 2-3 字中文名候选。"""
        m = re.search(r"([\u4e00-\u9fa5]{2,3})", text)
        return m.group(1) if m else ""


# =============================================================================
# 结构性修复引擎 V5
# 解决条款缺失等结构性问题（非表层词替换）
# =============================================================================
class StructuralRepairEngine:
    """结构性修复：条款缺失补全。"""

    def __init__(self, sp_engine: SecondPerspectiveCausalEngine):
        self.sp_engine = sp_engine
        self.repair_logs: List[Dict[str, Any]] = []

    def _log(self, repair_type: str, target_id: str, detail: str, action: str):
        self.repair_logs.append(
            {
                "repair_type": repair_type,
                "target_id": target_id,
                "detail": detail,
                "action": action,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def repair_contract_gaps(self, chain, hedge_report) -> List[Dict]:
        """合同条款缺失修复：根据崩溃报告生成补充条款建议。"""
        fixes = []
        for item in hedge_report.get("chain_fragility", []):
            for dep in item.get("dangling_deps", []):
                if dep == "PAYMENT_WITHOUT_ACCEPTANCE":
                    fixes.append(
                        {
                            "target_id": item["id"],
                            "fix_type": "ADD_ACCEPTANCE_CLAUSE",
                            "adds_premise": "乙方应于交付后15个工作日内完成验收，验收标准以附件技术规格书为准",
                        }
                    )
                elif dep == "BREACH_WITHOUT_OBLIGATION":
                    fixes.append(
                        {
                            "target_id": item["id"],
                            "fix_type": "ADD_OBLIGATION_CLAUSE",
                            "adds_premise": "甲方义务：按约定时间支付款项；乙方义务：按约定标准交付成果",
                        }
                    )
                elif dep == "LIABILITY_WITHOUT_BREACH":
                    fixes.append(
                        {
                            "target_id": item["id"],
                            "fix_type": "ADD_BREACH_CLAUSE",
                            "adds_premise": "任何一方未按约履行义务即构成违约，违约金按合同总额10%计算",
                        }
                    )
                elif dep == "TERMINATION_WITHOUT_NOTICE":
                    fixes.append(
                        {
                            "target_id": item["id"],
                            "fix_type": "ADD_NOTICE_CLAUSE",
                            "adds_premise": "解除方应提前30日书面通知对方，通知送达后合同方可解除",
                        }
                    )
        for missing in hedge_report.get("global_missing", []):
            if missing == "DISPUTE_RESOLUTION":
                fixes.append(
                    {
                        "target_id": "GLOBAL",
                        "fix_type": "ADD_DISPUTE_CLAUSE",
                        "adds_premise": "因本合同产生的争议，双方应友好协商；协商不成的，提交合同签订地人民法院诉讼解决",
                    }
                )
            elif missing == "FORCE_MAJEURE":
                fixes.append(
                    {
                        "target_id": "GLOBAL",
                        "fix_type": "ADD_FORCE_MAJEURE_CLAUSE",
                        "adds_premise": "因不可抗力导致无法履行的，遭遇方应在15日内书面通知对方并提供证明，可部分或全部免除责任",
                    }
                )
        for fix in fixes:
            self._log(
                "REPAIR_CONTRACT_GAP",
                fix["target_id"],
                f"补充条款建议：{fix['fix_type']}",
                fix["adds_premise"],
            )
        return fixes


# =============================================================================
# 合同审查主管线
# SPL四阶段 + 第二视角五步内核，面向企业合同文书审查场景
# =============================================================================
class ContractReviewEngine:
    """企业合同文书审查引擎：条款因果链构建 -> 假设透视 -> 崩溃判定 -> 责任锚定 -> 重构建议。"""

    def __init__(self, contract_title: str = ""):
        self.contract_title = contract_title
        self.sp_engine = SecondPerspectiveCausalEngine()
        self.repair_engine = StructuralRepairEngine(self.sp_engine)
        self.established_facts: Set[str] = set()
        self.review_history: List[Dict[str, Any]] = []

    def review(
        self,
        clauses: List[Dict[str, str]],
        established_facts: Optional[Set[str]] = None,
    ) -> Dict[str, Any]:
        """
        审查合同条款列表。
        输入 clauses: List[Dict{id, premise, conclusion, party, counterparty}]。
        返回完整审计报告。
        """
        if established_facts:
            self.established_facts = established_facts

        print(
            f"\n===== 合同审查启动 | 《{self.contract_title}》 | 条款数：{len(clauses)} ====="
        )

        # 【SPL 1 叙事剥离：条款类型识别 + 依赖检测】
        print("1/5 执行：条款叙事剥离 & 类型识别")
        chain = self.sp_engine.contract_clause_stripping(clauses)
        type_dist = defaultdict(int)
        for cl in chain:
            type_dist[cl["clause_type"]] += 1
        print(f"   条款类型分布：{dict(type_dist)}")
        dangling_count = sum(1 for cl in chain if cl.get("dangling"))
        print(f"   依赖悬空条款：{dangling_count}个")

        # 【SPL 2 内隐假设透视：逆反校验】
        print("2/5 执行：内隐假设透视 & 逆反校验")
        chain = self.sp_engine.contract_assumption_probe(chain)
        inevitable_count = sum(
            1
            for cl in chain
            for a in cl.get("assumptions", [])
            if a["collapse"] == "INEVITABLE"
        )
        print(f"   不可逆假设：{inevitable_count}个")

        # 【SPL 3 脆弱性对冲：崩溃判定】
        print("3/5 执行：脆弱性对冲 & 崩溃判定")
        hedge_report = self.sp_engine.contract_vulnerability_hedge(chain)
        verdict = hedge_report["collapse_verdict"]
        print(f"   崩溃判定：{verdict}")
        if hedge_report.get("global_missing"):
            print(f"   全局缺失条款：{hedge_report['global_missing']}")

        # 【SPL 4 责任闭环锚定】
        print("4/5 执行：责任闭环锚定")
        anchors = self.sp_engine.contract_responsibility_anchor(chain)
        print(f"   责任锚点：{len(anchors)}个")

        # 【V5 结构性修复：补充条款建议】
        print("5/5 执行：结构性修复 & 补充建议")

        # 保存修复前状态快照（供报告使用，reconstruction 会原地修改 chain）
        pre_fix_dangling = [
            {
                "id": cl["id"],
                "type": cl["clause_type"],
                "deps": list(cl.get("dangling_deps", [])),
            }
            for cl in chain
            if cl.get("dangling")
        ]
        pre_fix_assumptions = [
            {
                "id": cl["id"],
                "type": cl["clause_type"],
                "inevitable": [
                    a
                    for a in cl.get("assumptions", [])
                    if a["collapse"] == "INEVITABLE"
                ],
                "conditional": [
                    a
                    for a in cl.get("assumptions", [])
                    if a["collapse"] == "CONDITIONAL"
                ],
            }
            for cl in chain
            if cl.get("assumptions")
        ]

        suggested_fixes = self.sp_engine._suggest_contract_fixes(chain)
        repair_fixes = self.repair_engine.repair_contract_gaps(chain, hedge_report)
        # 去重：按 (target_id, fix_type) 合并
        seen_fixes = set()
        all_fixes = []
        for fix in suggested_fixes + repair_fixes:
            key = (fix.get("target_id", ""), fix.get("fix_type", ""))
            if key not in seen_fixes:
                seen_fixes.add(key)
                all_fixes.append(fix)
        if all_fixes:
            print(f"   修复建议：{len(all_fixes)}条")

        # 【第二视角五步内核：因果重构收敛校验】
        sp_recon = self.sp_engine.contract_causal_reconstruction(
            chain, fix_vars=all_fixes, target_state="合同因果自洽"
        )
        if not sp_recon["converged"]:
            print(f"   ⚠️ {sp_recon['diagnosis']}")
        else:
            print(f"   ✅ {sp_recon['diagnosis']}")

        # 生成审计报告（使用修复前快照）
        report = {
            "contract_title": self.contract_title,
            "clause_count": len(clauses),
            "clause_type_distribution": dict(type_dist),
            "dangling_clauses": pre_fix_dangling,
            "assumption_issues": pre_fix_assumptions,
            "collapse_verdict": verdict,
            "weakest_clause": hedge_report.get("weakest_clause_type"),
            "global_missing": hedge_report.get("global_missing", []),
            "responsibility_anchors": anchors,
            "repair_suggestions": all_fixes,
            "repair_logs": self.repair_engine.repair_logs,
            "reconstruction": sp_recon,
            "overall_passed": sp_recon["converged"]
            and verdict != "INEVITABLE_COLLAPSE",
        }
        self.review_history.append(report)
        return report

    def save_report(self, report: Dict[str, Any], path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=_json_default)


# =============================================================================
# 合同文书审查演示
# =============================================================================
if __name__ == "__main__":
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print("#" * 60)
    print("# 合同文书审查 · 演示")
    print("#" * 60)

    contract_engine = ContractReviewEngine("软件开发外包合同（审查样例）")

    # 模拟合同条款：故意缺少验收条款和争议解决条款，制造依赖悬空和全局缺失
    contract_clauses = [
        {
            "id": "C001",
            "party": "甲方",
            "counterparty": "乙方",
            "premise": "甲方委托乙方开发软件系统，双方签订本合同",
            "conclusion": "甲方应在合同签订后10日内支付预付款30%",
        },
        {
            "id": "C002",
            "party": "乙方",
            "counterparty": "甲方",
            "premise": "甲方支付预付款后，乙方开始系统开发",
            "conclusion": "乙方应在90个工作日内完成系统交付",
        },
        {
            "id": "C003",
            "party": "甲方",
            "counterparty": "乙方",
            "premise": "乙方完成交付后",
            "conclusion": "甲方应在15日内支付尾款70%",
        },
        {
            "id": "C004",
            "party": "双方",
            "counterparty": "违约方",
            "premise": "任何一方未按约定履行义务",
            "conclusion": "违约方应向守约方支付违约金，并赔偿因此造成的损失",
        },
        {
            "id": "C005",
            "party": "甲方",
            "counterparty": "乙方",
            "premise": "乙方逾期交付超过30日",
            "conclusion": "甲方有权单方解除合同，并要求乙方退还已付款项",
        },
        {
            "id": "C006",
            "party": "双方",
            "counterparty": "泄露方",
            "premise": "双方在合作期间获取的对方商业信息",
            "conclusion": "双方负有保密义务，不得向第三方披露",
        },
    ]

    report = contract_engine.review(contract_clauses)

    print("\n" + "-" * 60)
    print("审查报告摘要：")
    print("-" * 60)
    print(f"  条款总数：{report['clause_count']}")
    print(f"  类型分布：{report['clause_type_distribution']}")
    print(f"  崩溃判定：{report['collapse_verdict']}")
    print(f"  全局缺失：{report['global_missing']}")
    print(f"  悬空条款：{len(report['dangling_clauses'])}个")
    for dc in report["dangling_clauses"]:
        print(f"    - {dc['id']}({dc['type']}): {dc['deps']}")
    print(f"  修复建议：{len(report['repair_suggestions'])}条")
    for rs in report["repair_suggestions"]:
        print(
            f"    - [{rs['fix_type']}] -> {rs['target_id']}: {rs['adds_premise'][:50]}..."
        )
    print(f"  收敛状态：{'通过' if report['overall_passed'] else '未通过'}")
    if not report["overall_passed"]:
        print(f"  诊断：{report['reconstruction']['diagnosis']}")
    print("-" * 60)
