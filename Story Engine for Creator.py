import uuid
import json
import re
from dataclasses import asdict, dataclass, field
from typing import Dict, Any, List, Callable, Optional, Protocol, Tuple
from collections import defaultdict

# ==================== 协议定义 ====================
class LLMProvider(Protocol):
    def generate(self, prompt: str, **kwargs) -> str:
        ...

# ==================== 基础数据结构（与原有保持一致）====================
@dataclass
class ResponsibilityAccount:
    organization: str
    role: str
    stage: str
    nonce: Optional[str] = None
    def __post_init__(self):
        if not self.nonce:
            self.nonce = uuid.uuid4().hex[:8]

class AuditConfigLoader:
    @staticmethod
    def load_from_dict(config: Dict[str, Any]) -> Dict[str, Any]:
        return config
    @staticmethod
    def load_from_json(path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

class AuditPlugin:
    def __init__(self, name: str, analyze_func: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self.name = name
        self.analyze = analyze_func

class CognitiveAuditEngine:
    def __init__(self, account: ResponsibilityAccount, config: Dict[str, Any]):
        self.account = account
        self.config = config
        self.plugins: List[AuditPlugin] = []
        allowed_stages = self.config.get("allowed_stages", [])
        if account.stage not in allowed_stages:
            raise ValueError(f"Unsupported stage: {account.stage}")
    def register_plugin(self, plugin: AuditPlugin) -> None:
        self.plugins.append(plugin)
    def audit(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        report = {
            "disclaimer": self.config.get("disclaimer", "本报告基于情节逻辑分析，不构成创作建议"),
            "responsibility_account": self.account.__dict__,
            "audit_timestamp": uuid.uuid1().hex[:8],
            "overall_passed": True,
            "overall_score": 100.0,
            "analysis": {},
            "custom_fields": self.config.get("custom_fields", {}),
        }
        total_score = 0.0
        for plugin in self.plugins:
            result = plugin.analyze(decision_context)
            report["analysis"][plugin.name] = result
            if not result["passed"]:
                report["overall_passed"] = False
            total_score += result["score"]
        if self.plugins:
            report["overall_score"] = round(total_score / len(self.plugins), 2)
        return report

@dataclass
class EmotionalConstraint:
    name: str
    weight: float
    target: Optional[str] = None
    source: str = "initialization"
    version: int = 1

@dataclass
class ImplicitAssumption:
    content: str
    confidence: float
    risk_level: str

@dataclass
class CausalNode:
    premise: str
    conclusion: str
    context: Dict[str, Any] = field(default_factory=dict)
    node_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    implicit_assumptions: List[ImplicitAssumption] = field(default_factory=list)
    vulnerability_score: float = 100.0
    audit_report: Optional[Dict[str, Any]] = None
    parent_nodes: List[str] = field(default_factory=list)
    child_nodes: List[str] = field(default_factory=list)
    causal_weights: Dict[str, float] = field(default_factory=dict)
    character: str = ""   # 新增：节点所属角色，便于自动注册

@dataclass
class CausalLine:
    line_id: str
    character: str
    nodes: List[CausalNode] = field(default_factory=list)

@dataclass
class Chapter:
    chapter_id: int
    title: str
    causal_lines: List[CausalLine]
    global_state_before: Dict[str, Any]
    global_state_after: Dict[str, Any] = field(default_factory=dict)
    content: str = ""
    audit_report: Optional[Dict[str, Any]] = None

@dataclass
class GlobalState:
    characters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    world_rules: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    emotional_constraints: Dict[str, List[EmotionalConstraint]] = field(default_factory=dict)
    version: int = 0
    last_updated: str = field(default_factory=lambda: uuid.uuid1().hex[:8])

# ==================== 核心组件（已优化）====================
class NarrativeStripper:
    @staticmethod
    def strip(text: str) -> Dict[str, Any]:
        stripped = re.sub(r"[，。！？；：\"\"''()（）【】]", "", text)
        stripped = re.sub(r"[的地得]", "", stripped)
        stripped = re.sub(r"\s+", " ", stripped).strip()
        actions = re.findall(r"([\u4e00-\u9fa5]+)([打跑走看说哭笑哭生气难过拉黑离开留在])", stripped)
        return {"raw_text": text, "stripped_text": stripped, "actions": actions}

class ImplicitAssumptionDetector:
    @staticmethod
    def detect(node: CausalNode, global_state: GlobalState) -> List[ImplicitAssumption]:
        assumptions = []
        if "追上去" in node.conclusion or "留在原地" in node.conclusion:
            assumptions.append(ImplicitAssumption("角色具备物理位移行为能力且共处同一时空", 0.8, "low"))
        if "拉黑" in node.conclusion:
            assumptions.append(ImplicitAssumption("角色之间拥有生效的通讯网络连接手段", 0.9, "low"))
        if "打电话" in node.premise or "发消息" in node.premise:
            assumptions.append(ImplicitAssumption("角色持有可正常使用的通讯设备", 0.95, "low"))
        for char_name, emotions in global_state.emotional_constraints.items():
            if char_name in node.premise or char_name in node.conclusion:
                for emotion in emotions:
                    if emotion.weight >= 0.7:
                        target_desc = f"对{emotion.target}" if emotion.target else ""
                        assumptions.append(ImplicitAssumption(
                            content=f"{char_name}{target_desc}存在强烈的{emotion.name}情感",
                            confidence=emotion.weight,
                            risk_level="medium",
                        ))
        return assumptions

class VulnerabilityAssessor:
    @staticmethod
    def assess(node: CausalNode) -> float:
        score = 100.0
        physical = [a for a in node.implicit_assumptions if "情感" not in a.content]
        score -= len(physical) * 3
        forbidden = ["突然", "莫名", "毫无理由", "不知怎么", "鬼使神差", "突然之间"]
        for word in forbidden:
            if word in node.premise or word in node.conclusion:
                score -= 15
        if len(node.causal_weights) >= 2:
            score += min(10, len(node.causal_weights) * 2)
        return max(0.0, score)

class AutomaticStateExtractor:
    @staticmethod
    def extract(text: str, current_state: GlobalState) -> Dict[str, Any]:
        changes: Dict[str, Any] = {}
        if "拉黑了" in text or "拉黑" in text:
            changes.setdefault("characters", {})
            changes["characters.叶婉清.relationship.陆景川"] = "blocked"
        if "克制住" in text or "留在原地" in text:
            changes.setdefault("events", [])
            changes["events"] = current_state.events + [{"event": "核心成长点", "desc": "行为走向独立"}]
        # 情感关键词自动提取
        emotion_keyword_map = {
            "害怕失去": ("fear_of_loss", 0.8), "习惯了": ("habit", 0.7), "心动": ("attraction", 0.6),
            "难过": ("sadness", 0.6), "愤怒": ("anger", 0.7), "愧疚": ("guilt", 0.75),
            "依赖": ("dependence", 0.8), "占有欲": ("possessiveness", 0.85), "不舍": ("reluctance", 0.65),
        }
        emotional_updates: Dict[str, List[EmotionalConstraint]] = defaultdict(list)
        for keyword, (emotion_name, base_weight) in emotion_keyword_map.items():
            if keyword in text:
                for char_name in current_state.characters.keys():
                    parts = text.split(keyword)
                    context_window = parts[0][-20:] + parts[1][:20] if len(parts) >= 2 else text
                    if char_name in context_window:
                        target = None
                        for other in current_state.characters.keys():
                            if other != char_name and other in context_window:
                                target = other
                                break
                        emotional_updates[char_name].append(EmotionalConstraint(
                            name=emotion_name, weight=base_weight, target=target,
                            source="text_extraction", version=current_state.version + 1
                        ))
        if emotional_updates:
            changes["emotional_constraints"] = dict(emotional_updates)
        return changes

class AutomaticRepairEngine:
    @staticmethod
    def repair(text: str, audit_report: Dict[str, Any], llm_provider: Optional[LLMProvider] = None) -> str:
        # 如果提供了 LLM，尝试让 LLM 重写问题片段（仅对逻辑跳跃词进行修复）
        has_jump = False
        for result in audit_report.get("analysis", {}).values():
            for issue in result.get("issues", []):
                if "逻辑跳跃词" in issue:
                    has_jump = True
                    break
        if has_jump and llm_provider is not None:
            prompt = f"以下文本包含了‘突然’、‘莫名’等不自然的转折词。请重写这段文本，使其逻辑流畅、转折自然，不要改变原意和剧情。\n原文：{text}"
            try:
                repaired = llm_provider.generate(prompt, temperature=0.5, max_tokens=800)
                return repaired.strip()
            except Exception:
                pass  # 降级到词替换
        # 降级方案：简单替换
        repaired = text
        for result in audit_report.get("analysis", {}).values():
            for issue in result.get("issues", []):
                if "逻辑跳跃词" in issue:
                    match = re.search(r"'([^']+)'", issue)
                    if match:
                        word = match.group(1)
                        repaired = repaired.replace(word, "伴随着情绪的沉淀，顺理成章地")
        return repaired

class VisualReportGenerator:
    @staticmethod
    def generate(novel_title: str, chapters: List[Chapter]) -> str:
        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>{novel_title} - 情节逻辑校验报告</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 30px; background: #fdfdfd; color: #333; }}
.chapter {{ margin-bottom: 35px; background: white; border: 1px solid #eee; padding: 25px; border-radius: 12px; }}
.node {{ margin-left: 20px; margin-top: 15px; padding: 18px; background: #f9f9f9; border-radius: 8px; border-left: 4px solid #3498db; }}
.emotion-tag {{ display: inline-block; background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-right: 5px; }}
.passed {{ color: #27ae60; font-weight: bold; }}
.failed {{ color: #e67e22; font-weight: bold; }}
.score {{ float: right; background: #e0f2fe; color: #0369a1; padding: 5px 12px; border-radius: 20px; font-weight: bold; }}
h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
</style>
</head>
<body>
<h1>📊 《{novel_title}》情节逻辑校验报告</h1>
<p style="color:#777;">系统自动梳理多因果链条、检测情感动机并完成逻辑桥接。</p>
"""
        for ch in chapters:
            if not ch.audit_report:
                continue
            status = "passed" if ch.audit_report.get("overall_passed", True) else "failed"
            html += f"""
<div class="chapter">
    <h2>演进段落：{ch.title} <span class="score">稳态评分：{ch.audit_report.get('overall_score', 100)}</span></h2>
    <p>连贯性验证：<span class="{status}">{"✅ 剧情顺畅" if status=="passed" else "⚠️ 部分断层已修复"}</span></p>
"""
            for line in ch.causal_lines:
                html += f"<h3>👤 角色故事线：{line.character}</h3>"
                for node in line.nodes:
                    emotion_tags = ""
                    for a in node.implicit_assumptions:
                        if "情感" in a.content:
                            emotion_tags += f'<span class="emotion-tag">{a.content}</span>'
                    physical = ", ".join([a.content for a in node.implicit_assumptions if "情感" not in a.content]) or "无明显物理断层"
                    html += f"""
<div class="node">
    <strong>🧬 节点 {node.node_id}</strong>
    <p><b>情节起点：</b>{node.premise}</p>
    <p><b>剧情走向：</b>{node.conclusion}</p>
    {f'<p>💡 情感动机：{emotion_tags}</p>' if emotion_tags else ''}
    <p style="color:#666; font-size:13px;">🔍 潜在线索：{physical}</p>
</div>"""
            html += "</div>"
        html += "</body></html>"
        return html

# ==================== 新增：自然语言解析与自动角色注册 ====================
def extract_character_from_text(text: str) -> str:
    """从文本中提取可能的主角名字（简易实现，可替换为更智能的NER）"""
    # 常见中文名字模式（2-3个汉字）
    match = re.search(r"([\u4e00-\u9fa5]{2,3})", text)
    return match.group(1) if match else "主角"

def auto_register_characters(state: GlobalState, nodes: List[CausalNode]):
    """自动注册节点中出现的不在 state.characters 中的角色"""
    for node in nodes:
        # 尝试从 premise 和 conclusion 中提取角色名
        for text in [node.premise, node.conclusion]:
            char = extract_character_from_text(text)
            if char and char not in state.characters:
                state.characters[char] = {"性格": "中性", "简介": "自动注册的角色"}
                # 自动添加默认情感约束（轻度）
                if char not in state.emotional_constraints:
                    state.emotional_constraints[char] = []
                print(f"自动注册角色：{char}")

def parse_outline_to_nodes(outline: str) -> List[CausalNode]:
    """
    将自然语言大纲解析为 CausalNode 列表。
    支持格式：
      "A -> B -> C"
      "A → B; B → C"
      "前提1 → 结论1; 前提2 → 结论2"
    """
    # 统一箭头符号
    outline = outline.replace("→", "->")
    # 分割多个节点
    parts = re.split(r"[;；\n]", outline)
    nodes = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if "->" in part:
            premise, conclusion = part.split("->", 1)
            premise = premise.strip()
            conclusion = conclusion.strip()
        else:
            # 如果没有箭头，整个当作前提，结论为空（占位）
            premise = part
            conclusion = "（待续）"
        node = CausalNode(premise=premise, conclusion=conclusion)
        # 尝试提取角色
        node.character = extract_character_from_text(premise + conclusion)
        nodes.append(node)
    return nodes

# ==================== 主引擎（已优化）====================
class UltimateCausalNovelEngine:
    def __init__(self, novel_title: str, initial_global_state: GlobalState, output_language: str = "zh"):
        self.novel_title = novel_title
        self.global_state = initial_global_state
        self.output_language = output_language
        self.chapters: List[Chapter] = []
        self.causal_graph: Dict[str, CausalNode] = {}
        self.llm_provider: Optional[LLMProvider] = None

        self._init_audit_engines()
        self._register_all_audit_plugins()
        self.stripper = NarrativeStripper()
        self.assumption_detector = ImplicitAssumptionDetector()
        self.vulnerability_assessor = VulnerabilityAssessor()
        self.state_extractor = AutomaticStateExtractor()
        self.repair_engine = AutomaticRepairEngine()
        self.report_generator = VisualReportGenerator()
        self.sp_engine = SecondPerspectiveCausalEngine()
        self.world_builder = WorldBuilder()

    def set_llm_provider(self, provider: LLMProvider) -> None:
        self.llm_provider = provider

    def _init_audit_engines(self):
        self.planning_auditor = CognitiveAuditEngine(
            ResponsibilityAccount("StoryStudio", "ChapterPlanner", "planning"),
            {"allowed_stages": ["planning"]}
        )
        self.node_auditor = CognitiveAuditEngine(
            ResponsibilityAccount("StoryStudio", "NodeGenerator", "generation"),
            {"allowed_stages": ["generation"]}
        )
        self.consistency_auditor = CognitiveAuditEngine(
            ResponsibilityAccount("StoryStudio", "ConsistencyChecker", "consistency"),
            {"allowed_stages": ["consistency"]}
        )
        self.vulnerability_auditor = CognitiveAuditEngine(
            ResponsibilityAccount("StoryStudio", "VulnerabilityAssessor", "vulnerability"),
            {"allowed_stages": ["vulnerability"]}
        )

    def _register_all_audit_plugins(self):
        self.planning_auditor.register_plugin(AuditPlugin("story_chain_integrity", self._audit_story_chain_integrity))
        self.planning_auditor.register_plugin(AuditPlugin("implicit_assumption_detection", self._audit_implicit_assumptions))
        self.node_auditor.register_plugin(AuditPlugin("logical_jump_detection", self._audit_logical_jump))
        self.node_auditor.register_plugin(AuditPlugin("premise_conclusion_match", self._audit_premise_conclusion_match))
        self.consistency_auditor.register_plugin(AuditPlugin("character_consistency", self._audit_character_consistency))
        self.consistency_auditor.register_plugin(AuditPlugin("world_rule_consistency", lambda ctx: self.world_builder.check_consistency(ctx, self.global_state)))
        self.vulnerability_auditor.register_plugin(AuditPlugin("vulnerability_assessment", self._audit_vulnerability))

    def _audit_implicit_assumptions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        events = self._context_to_events(context)
        chain = self.sp_engine.narrative_stripping(events)
        self.sp_engine.implicit_assumption_probe(chain)
        critical = 0
        for line in context.get("causal_lines", []):
            for node in line.nodes:
                node.implicit_assumptions = self.assumption_detector.detect(node, self.global_state)
        for ev in chain:
            for a in ev.get("assumptions", []):
                if a["collapse"] == "INEVITABLE":
                    critical += 1
        return {"passed": critical == 0, "score": max(0.0, 100.0 - critical * 20), "critical_assumptions": critical}

    def _audit_logical_jump(self, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("text", "")
        forbidden = ["突然", "莫名", "毫无理由", "不知怎么", "鬼使神差", "突然之间"]
        issues = [f"发现逻辑跳跃词：'{w}'" for w in forbidden if w in text]
        score = max(0.0, 100.0 - len(issues) * 15)
        return {"passed": len(issues) == 0, "issues": issues, "score": score}

    def _audit_vulnerability(self, context: Dict[str, Any]) -> Dict[str, Any]:
        node = context["node"]
        score = self.vulnerability_assessor.assess(node)
        node.vulnerability_score = score
        return {"passed": score >= 50, "score": score}

    def _context_to_events(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        lines = context.get("causal_lines") or []
        for line in lines:
            nodes = getattr(line, "nodes", line.get("nodes", []) if isinstance(line, dict) else [])
            for n in nodes:
                events.append({
                    "id": getattr(n, "node_id", ""),
                    "premise": getattr(n, "premise", ""),
                    "conclusion": getattr(n, "conclusion", ""),
                    "character": getattr(n, "character", ""),
                })
        if not events and context.get("node"):
            n = context["node"]
            events.append({"id": getattr(n, "node_id", ""), "premise": getattr(n, "premise", ""),
                           "conclusion": getattr(n, "conclusion", ""), "character": getattr(n, "character", "")})
        return events

    def _audit_story_chain_integrity(self, context: Dict[str, Any]) -> Dict[str, Any]:
        chain = self.sp_engine.narrative_stripping(self._context_to_events(context))
        dangling = [e["id"] for e in chain if e.get("dangling")]
        return {"passed": not dangling, "score": max(0.0, 100.0 - len(dangling) * 15), "dangling_events": dangling}

    def _audit_premise_conclusion_match(self, context: Dict[str, Any]) -> Dict[str, Any]:
        mismatches = []
        for ev in self._context_to_events(context):
            char = ev.get("character") or ""
            if char and char not in (ev.get("premise", "") + ev.get("conclusion", "")):
                mismatches.append(ev["id"])
        return {"passed": not mismatches, "score": max(0.0, 100.0 - len(mismatches) * 15), "mismatch_events": mismatches}

    def _audit_character_consistency(self, context: Dict[str, Any]) -> Dict[str, Any]:
        violations = []
        for ev in self._context_to_events(context):
            char = ev.get("character")
            profile = self.global_state.characters.get(char, {})
            if profile:
                restraint = profile.get("restraint", profile.get("克制", 0.5))
                if isinstance(restraint, (int, float)) and restraint > 0.7:
                    if any(w in ev.get("conclusion", "") for w in ["大喊", "追赶", "崩溃", "痛哭"]):
                        violations.append(ev["id"])
        return {"passed": not violations, "score": max(0.0, 100.0 - len(violations) * 20), "violations": violations}

    def plan_chapter(self, chapter_id: int, title: str, causal_lines: List[CausalLine]) -> Optional[Chapter]:
        # 自动注册角色
        all_nodes = []
        for line in causal_lines:
            all_nodes.extend(line.nodes)
        auto_register_characters(self.global_state, all_nodes)

        report = self.planning_auditor.audit({"chapter_id": chapter_id, "title": title, "causal_lines": causal_lines})
        for line in causal_lines:
            for node in line.nodes:
                self.causal_graph[node.node_id] = node
        chapter = Chapter(
            chapter_id=chapter_id,
            title=title,
            causal_lines=causal_lines,
            global_state_before=json.loads(json.dumps(asdict(self.global_state))),
            audit_report=report,
        )
        self.chapters.append(chapter)
        return chapter

    def render_chapter(self, chapter: Chapter, max_retries: int = 3) -> Optional[str]:
        full_content = ""
        for line in chapter.causal_lines:
            for i, node in enumerate(line.nodes):
                for attempt in range(max_retries):
                    if i > 0:
                        text = self._call_llm_to_bridge_gap(line.nodes[i-1], node, chapter)
                    else:
                        text = self._call_llm_for_node(node, chapter)
                    node_audit = self.node_auditor.audit(
                        {"node": node, "text": text, "global_state": asdict(self.global_state)}
                    )
                    vuln_audit = self.vulnerability_auditor.audit({"node": node, "text": text})
                    if node_audit["overall_passed"] and vuln_audit["overall_passed"]:
                        node.audit_report = {**node_audit, "vulnerability": vuln_audit}
                        full_content += text + "\n\n"
                        break
                    # 尝试用 LLM 修复（如果提供了 provider）
                    text = self.repair_engine.repair(text, node_audit, self.llm_provider)
                else:
                    text = self.repair_engine.repair(
                        text,
                        {"analysis": {"logical_jump_detection": {"issues": ["发现逻辑跳跃词"]}}},
                        self.llm_provider
                    )
                    full_content += text + "\n\n"
        consistency_audit = self.consistency_auditor.audit(
            {"chapter": asdict(chapter), "text": full_content, "global_state": asdict(self.global_state)}
        )
        chapter.content = full_content.strip()
        # 第二视角五步内核诊断（嵌入一致性审计结果）
        sp_chain = self.sp_engine.narrative_stripping(
            [{"id": n.node_id, "premise": n.premise, "conclusion": n.conclusion, "character": n.character}
             for line in chapter.causal_lines for n in line.nodes]
        )
        self.sp_engine.implicit_assumption_probe(sp_chain)
        sp_hedge = self.sp_engine.vulnerability_hedge(sp_chain)
        sp_anchor = self.sp_engine.responsibility_anchor(sp_chain)
        sp_recon = self.sp_engine.causal_reconstruction(sp_chain, fix_vars=[], target_state="叙事逻辑自洽")
        chapter.audit_report = {**consistency_audit, "second_perspective": {
            "collapse_verdict": sp_hedge["collapse_verdict"],
            "anchors": sp_anchor,
            "reconstruction": sp_recon,
        }}
        changes = self.state_extractor.extract(full_content, self.global_state)
        for key, val in changes.items():
            self._apply_state_change(key, val)
        self.global_state.version += 1
        chapter.global_state_after = json.loads(json.dumps(asdict(self.global_state)))
        return full_content

    def _call_llm_for_node(self, node: CausalNode, chapter: Chapter) -> str:
        lang = (self.output_language or "zh").lower().strip()
        if self.llm_provider is not None:
            emotions = []
            for char, cons in self.global_state.emotional_constraints.items():
                if char in node.premise or char in node.conclusion:
                    for e in cons:
                        emotions.append(f"{e.name}(权重{e.weight})")
            emotion_hint = f"当前角色情感状态：{', '.join(emotions)}。请据此合理推导行为动机。" if emotions else ""
            if lang in ("en", "english"):
                prompt = f"""You are a top-tier web fiction writer.
Characters: {self.global_state.characters}
{emotion_hint}
Evolve the plot naturally from the premise [{node.premise}] to the conclusion [{node.conclusion}].
Constraints: vivid prose, character-consistent; motivations clear; avoid abrupt words like "suddenly", "out of nowhere".
Output: 120-200 English words."""
            elif lang in ("bilingual", "zh-en", "zh_en", "cn-en", "cn_en", "mix"):
                prompt = f"""你是一名优秀的网络小说作家，同时也是专业英译者。
角色设定：{self.global_state.characters}
{emotion_hint}
请将情节起点【{node.premise}】自然演进至故事走向【{node.conclusion}】。
要求：文字细腻流畅，符合人物性格，行为必须有合理动机，严禁使用“突然”“莫名其妙”等生硬转折词。
输出格式必须严格如下：
【中文】
（150-250字中文小说文本）

【English】
(120-200 English words, faithful translation, natural English)"""
            else:
                prompt = f"""你是一名优秀的网络小说作家。
角色设定：{self.global_state.characters}
{emotion_hint}
请将情节起点【{node.premise}】自然演进至故事走向【{node.conclusion}】。
要求：文字细腻流畅，符合人物性格，行为必须有合理动机，严禁使用“突然”“莫名其妙”等生硬转折词。
输出150-250字的小说文本。"""
            return self.llm_provider.generate(prompt, temperature=0.7, max_tokens=8000)
        # 演示模式
        if lang in ("en", "english"):
            return f"[Demo] From “{node.premise}” to “{node.conclusion}”, the character’s inner world shifts, plot moves forward."
        if lang in ("bilingual", "zh-en", "zh_en", "cn-en", "cn_en", "mix"):
            return f"【中文】\n【演示】从「{node.premise}」到「{node.conclusion}」，角色的内心经历了转变，情节自然推进。\n\n【English】\n[Demo] From “{node.premise}” to “{node.conclusion}”, the character’s inner world shifts, plot moves forward."
        return f"【演示】从「{node.premise}」到「{node.conclusion}」，角色的内心经历了转变，情节自然推进。"

    def _call_llm_to_bridge_gap(self, prev_node: CausalNode, curr_node: CausalNode, chapter: Chapter) -> str:
        lang = (self.output_language or "zh").lower().strip()
        if self.llm_provider is not None:
            emotions = []
            for char, cons in self.global_state.emotional_constraints.items():
                if char in prev_node.conclusion or char in curr_node.premise:
                    for e in cons:
                        if e.weight >= 0.6:
                            emotions.append(f"{char}的{e.name}")
            emotion_hint = f"重点体现{', '.join(emotions)}的变化过程。" if emotions else ""
            if lang in ("en", "english"):
                prompt = f"""You are a master of narrative continuity.
There is a natural gap: previous ending [{prev_node.conclusion}], next opening [{curr_node.premise}].
Write a seamless transition (~160-240 English words) using inner thoughts, emotional shifts, or environmental details.
{emotion_hint}
Avoid abrupt words like "suddenly", "out of nowhere". Do NOT repeat previous content."""
            elif lang in ("bilingual", "zh-en", "zh_en", "cn-en", "cn_en", "mix"):
                prompt = f"""你是顶级小说情节逻辑架构师，同时也是专业英译者。
作者大纲存在自然断层：上一段结尾【{prev_node.conclusion}】，下一段开头【{curr_node.premise}】。
请写一段过渡剧情，通过心理活动、情绪变化或环境细节将两个场景无缝连接。
{emotion_hint}
严禁使用生硬转折词，不要重复前文内容，让过渡自然流畅。
输出格式必须严格如下：
【中文】
（180-260字中文过渡剧情）

【English】
(160-240 English words, faithful translation, natural English)"""
            else:
                prompt = f"""你是顶级小说情节逻辑架构师。
作者大纲存在自然断层：上一段结尾【{prev_node.conclusion}】，下一段开头【{curr_node.premise}】。
请写一段200字左右的过渡剧情，通过心理活动、情绪变化或环境细节将两个场景无缝连接。
{emotion_hint}
严禁使用生硬转折词，不要重复前文内容，让过渡自然流畅。"""
            return self.llm_provider.generate(prompt, temperature=0.7, max_tokens=8000)
        return self._call_llm_for_node(curr_node, chapter)

    def _apply_state_change(self, key: str, value: Any) -> None:
        parts = key.split(".")
        obj: Any = self.global_state
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            elif isinstance(obj, dict):
                obj = obj.setdefault(part, {})
            elif isinstance(obj, list) and part.lstrip("-").isdigit():
                idx = int(part)
                if idx >= len(obj):
                    obj.extend([{}] * (idx - len(obj) + 1))
                obj = obj[idx]
            else:
                raise KeyError(f"无法解析路径: {key}")
        last = parts[-1]
        if isinstance(obj, dict):
            obj[last] = value
        elif hasattr(obj, last):
            setattr(obj, last, value)
        else:
            raise KeyError(f"无法设置属性 {last} 在 {type(obj)}")

    def generate_novel(self, chapter_plans: List[Chapter]) -> str:
        full = f"# {self.novel_title}\n\n"
        for ch in chapter_plans:
            content = self.render_chapter(ch)
            if content:
                full += f"## 第{ch.chapter_id}章 {ch.title}\n\n{content}\n\n"
        with open("audit_report.html", "w", encoding="utf-8") as f:
            f.write(self.report_generator.generate(self.novel_title, self.chapters))
        return full

    # 新增辅助方法：从自然语言大纲直接创建章节
    def create_chapter_from_outline(self, chapter_id: int, title: str, outline: str) -> Optional[Chapter]:
        nodes = parse_outline_to_nodes(outline)
        if not nodes:
            return None
        # 自动设置角色（如果节点中没有character，尝试提取）
        for node in nodes:
            if not node.character:
                node.character = extract_character_from_text(node.premise + node.conclusion)
        # 将所有节点放入一个 CausalLine（角色可以混合，但建议按角色分组，这里简化）
        line = CausalLine(line_id=f"ch{chapter_id}", character=nodes[0].character if nodes else "主角", nodes=nodes)
        return self.plan_chapter(chapter_id, title, [line])

    def conceive_world(self, outline: str) -> Dict[str, Any]:
        """构思世界观：从自然语言提纲生成势力/地理/法则/时间线骨架，并写入全局 world_rules。"""
        self.world_builder.generate_skeleton(outline)
        self.global_state.world_rules.update(self.world_builder.world_rules)
        return self.world_builder.world_rules

# =============================================================================
# 第二视角因果推理引擎 V2.1（决定论内核，无概率化推测）
# 五步算子：叙事剥离 → 内隐假设透视 → 脆弱性对冲 → 责任闭环锚定 → 因果重构
# 与 business 引擎内联同一份内核，确保两引擎逻辑口径一致。
# =============================================================================
class SecondPerspectiveCausalEngine:
    """决定论因果推理：仅做因果链的结构性判定，不输出概率估计。"""

    _COLOCATION_HINTS = ["车站", "站台", "电车", "街道", "房间", "同处", "见面", "相遇", "战场", "广场"]
    _MOTION_HINTS = ["追", "跑", "走", "离开", "去", "赶到", "赶来", "冲", "奔"]
    _COMMS_HINTS = ["发消息", "打电话", "拉黑", "联系", "回复", "微信", "短信", "传讯"]
    _JUMP_HINTS = ["突然", "莫名", "毫无理由", "不知怎么", "鬼使神差", "突然之间"]

    def narrative_stripping(self, events):
        chain = []
        seen_chars = set()
        for i, ev in enumerate(events):
            ev = dict(ev)
            ev.setdefault("id", f"E{i:03d}")
            ev.setdefault("character", "")
            premise, conclusion = ev.get("premise", ""), ev.get("conclusion", "")
            char = ev["character"] or self._infer_character(premise + conclusion)
            ev["character"] = char
            dangling = bool(char) and (i > 0) and (char not in premise) and (char not in seen_chars)
            if char:
                seen_chars.add(char)
            ev["dangling"] = dangling
            chain.append(ev)
        return chain

    def implicit_assumption_probe(self, chain):
        for ev in chain:
            text = ev.get("premise", "") + ev.get("conclusion", "")
            assumptions = []
            if any(h in text for h in self._COLOCATION_HINTS):
                assumptions.append({
                    "content": "角色共处同一物理时空，场景自洽",
                    "reverse_check": "撤除：角色不在同一时空 → 位移类行为失去前提",
                    "collapse": "INEVITABLE" if any(m in ev.get("conclusion", "") for m in self._MOTION_HINTS) else "STABLE",
                })
            if any(h in text for h in self._COMMS_HINTS):
                assumptions.append({
                    "content": "角色间存在生效的通讯连接手段",
                    "reverse_check": "撤除：无通讯手段 → 通讯类行为不成立",
                    "collapse": "INEVITABLE" if any(h in ev.get("conclusion", "") for h in self._COMMS_HINTS) else "STABLE",
                })
            ev["assumptions"] = assumptions
        return chain

    def vulnerability_hedge(self, chain):
        weakest, weakest_score = None, -1.0
        for ev in chain:
            frag = sum(1 for a in ev.get("assumptions", []) if a["collapse"] == "INEVITABLE")
            if ev.get("dangling"):
                frag += 2
            ev["fragility"] = frag
            if frag > weakest_score:
                weakest_score, weakest = frag, ev
        if weakest is None:
            verdict = "STABLE"
        elif weakest_score >= 2:
            verdict = "INEVITABLE_COLLAPSE"
        elif weakest_score == 1:
            verdict = "CONDITIONAL_COLLAPSE"
        else:
            verdict = "STABLE"
        return {
            "weakest_variable": weakest["id"] if weakest else None,
            "weakest_event": weakest,
            "collapse_verdict": verdict,
            "chain_fragility": [{"id": e["id"], "fragility": e.get("fragility", 0)} for e in chain],
        }

    def responsibility_anchor(self, chain):
        anchors = []
        for idx, ev in enumerate(chain):
            char = ev.get("character", "")
            action = self._extract_action(ev.get("conclusion", ""))
            anchors.append({
                "event_id": ev["id"],
                "position": idx,
                "accountable": char,
                "decision_unit": f"{char}→{action}" if char else action,
                "premise": ev.get("premise", ""),
                "conclusion": ev.get("conclusion", ""),
            })
        return anchors

    def causal_reconstruction(self, chain, fix_vars, target_state):
        fixed_ids = set()
        for ev in chain:
            for fix in (fix_vars or []):
                if ev["id"] == fix.get("target_id") or fix.get("apply_to") == "all":
                    ev["premise"] = (ev["premise"] + "；" + fix.get("adds_premise", "")).strip("；")
                    ev["dangling"] = False
                    fixed_ids.add(ev["id"])
        residual = []
        for ev in chain:
            if ev.get("dangling") and ev["id"] not in fixed_ids:
                residual.append(f"事件{ev['id']}结论缺前提支撑")
            for a in ev.get("assumptions", []):
                if a["collapse"] == "INEVITABLE" and not fix_vars:
                    residual.append(f"事件{ev['id']}关键预设不可逆撤除")
        if residual:
            return {"converged": False, "diagnosis": "[中断：因果链未收敛] " + "；".join(residual), "fixed_ids": list(fixed_ids)}
        return {"converged": True, "target_state": target_state,
                "diagnosis": f"因果链收敛至目标稳态：{target_state}", "fixed_ids": list(fixed_ids)}

    def _infer_character(self, text):
        return ""
    def _extract_action(self, conclusion):
        for w in self._MOTION_HINTS + self._COMMS_HINTS:
            if w in conclusion:
                return w
        return conclusion[:12]


# =============================================================================
# WorldBuilder：世界观构思（势力 / 地理 / 法则 / 时间线骨架 + 一致性校验）
# =============================================================================
class WorldBuilder:
    """从自然语言提纲构思世界观骨架，并维护 world_rules，供 world_rule_consistency 真实校验。"""

    def __init__(self):
        self.factions: List[str] = []
        self.geography: List[str] = []
        self.laws: List[str] = []
        self.timeline: List[str] = []
        self.world_rules: Dict[str, Any] = {}

    def generate_skeleton(self, outline: str) -> Dict[str, Any]:
        import re as _re
        text = outline or ""
        fac = _re.findall(r"([一-龥]{1,6}?(?:族|国|门|宗|组织|帝国|联邦|公会|势力))", text)
        self.factions = list(dict.fromkeys(fac))
        geo = _re.findall(r"([一-龥]{1,6}?(?:界|域|大陆|城|山|海|渊|境|洲|星球))", text)
        self.geography = list(dict.fromkeys(geo))
        law = _re.findall(r"([一-龥]{1,8}?(?:之道|法则|铁则|律令|天条))", text)
        self.laws = list(dict.fromkeys(law))
        self.world_rules = {
            "factions": self.factions,
            "geography": self.geography,
            "laws": self.laws,
            "timeline": self.timeline,
        }
        return self.world_rules

    def add_timeline_event(self, event: str) -> None:
        self.timeline.append(event)

    def check_consistency(self, context: Dict[str, Any], global_state=None) -> Dict[str, Any]:
        text = ""
        if isinstance(context, dict):
            text = context.get("text", "") or ""
            ch = context.get("chapter")
            if isinstance(ch, dict):
                text = text or str(ch.get("content", ""))
        if not self.factions and not self.geography and not self.laws:
            return {"passed": True, "score": 100, "note": "世界观骨架未构建，跳过硬性校验"}
        violations = []
        for fac in self.factions:
            if fac in text and ("灭亡" in text or "覆灭" in text) and (fac + "仍" in text):
                violations.append(f"势力一致性冲突：{fac} 既被宣称覆灭又仍存续")
        score = max(0.0, 100.0 - len(violations) * 20)
        return {"passed": len(violations) == 0, "score": score,
                "violations": violations, "world_rules": self.world_rules}


# ==================== 演示示例 ====================
if __name__ == "__main__":
    # 极简演示：使用 MockLLM（无API）
    class MockLLM(LLMProvider):
        def generate(self, prompt: str, **kwargs) -> str:
            return "（模拟的桥接文本）她深吸一口气，将所有情绪压回心底，转身走向站台边缘。电车进站的气流吹起发梢，她的目光追随着那个熟悉的身影，却终究没有迈出那一步。"
    state = GlobalState()
    engine = UltimateCausalNovelEngine("自动补全测试", state)
    engine.set_llm_provider(MockLLM())
    # 使用自然语言大纲
    outline = "叶婉清拿到诊断报告，得知纵容权重2.7 → 她决定不再纵容 → 在电车站遇到陆景川，克制住没有追上去"
    chapter = engine.create_chapter_from_outline(1, "决裂", outline)
    if chapter:
        engine.render_chapter(chapter)
        print(engine.compile_all())
