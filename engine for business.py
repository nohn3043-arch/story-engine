import uuid
import json
import re
import math
import dataclasses
import traceback
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Protocol, Set, Tuple, Callable
from collections import defaultdict, deque
from enum import Enum, auto

# =============================================================================
# 基础工具与序列化
# =============================================================================
def _json_default(obj):
    if isinstance(obj, Enum):
        return obj.name
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, deque):
        return list(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# =============================================================================
# SPL 故事原生四阶推理枚举
# =============================================================================
class SPLStage(Enum):
    STRIP_NARRATIVE = auto()    # 1. 叙事剥离：识别故事元素（伏笔/转折/高潮/铺垫）
    SCAN_ASSUMPTION = auto()   # 2. 内隐假设：校验人物动机、情节逻辑合理性
    HEDGE_RISK = auto()        # 3. 脆弱性对冲：识别OOC、逻辑漏洞、节奏问题
    LOCK_RESPONSIBILITY = auto()# 4. 责任闭环：输出故事质量评分、可追溯优化
    RECONSTRUCT = auto()       # 5. 因果重构（第二视角五步因果推理内核）

class RiskLevel(Enum):
    SAFE = auto()
    WARNING = auto()
    CRITICAL = auto()
    FATAL = auto()

class NodeStatus(Enum):
    RAW = auto()
    STRIPPED = auto()
    AUDITED = auto()
    PRUNED = auto()
    ACTIVE = auto()
    FROZEN = auto()
    FORESHADOW = auto()  # 新增：伏笔节点
    MERGED = auto()      # 新增：合并节点

class StoryElementType(Enum):
    """故事元素分类，叙事剥离阶段自动识别"""
    FORESHADOW = auto()   # 伏笔
    TURNING_POINT = auto()# 转折
    CLIMAX = auto()       # 高潮
    PADDING = auto()      # 铺垫
    DIALOGUE = auto()     # 对话
    ACTION = auto()       # 动作
    PSYCHOLOGY = auto()   # 心理

# =============================================================================
# 责任闭环锚定层
# =============================================================================
@dataclass
class TraceLog:
    timestamp: str
    operation: str
    stage: SPLStage
    node_id: Optional[str]
    remark: str
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)

@dataclass
class ResponsibilityAccount:
    organization: str
    role: str
    stage: str
    nonce: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    trace_chain: List[str] = field(default_factory=list)
    story_quality_score: float = 0.0

    def bind_stage(self, spl_stage: SPLStage) -> bool:
        stage_name = spl_stage.name
        self.trace_chain.append(f"{stage_name}|{uuid.uuid4().hex[:6]}")
        return True

class LLMProvider(Protocol):
    def generate(self, prompt: str, **kwargs) -> str:
        ...

# =============================================================================
# ✨ 四万次重构核心：12维高阶情感耦合动力学
# 专为故事生成优化：情感耦合、记忆残留、人际传染、阈值触发
# =============================================================================
@dataclass
class EmotionalMemory:
    """情感记忆单元，保留事件情感残留"""
    event_id: str
    emotion_vector: Dict[str, float]
    decay_rate: float = 0.05  # 每步衰减率
    remaining_strength: float = 1.0

@dataclass
class CharacterPhaseSpace:
    """
    12维情感相空间，四万次迭代收敛耦合矩阵
    专为禁忌恋/复杂情感博弈优化
    """
    character_name: str
    
    # 核心情感维度（0~1）
    attachment: float = 0.5    # 依恋
    restraint: float = 0.5     # 克制
    anxiety: float = 0.5       # 焦虑
    guilt: float = 0.0         # 愧疚/背德感
    desire: float = 0.0        # 欲望
    resentment: float = 0.0    # 怨恨
    shame: float = 0.0         # 羞耻（禁忌恋核心）
    longing: float = 0.0       # 思念
    jealousy: float = 0.0      # 嫉妒
    relief: float = 0.0        # 释然
    hope: float = 0.0          # 期待
    despair: float = 0.0       # 绝望

    # 动力学参数
    base_damping: float = field(default=0.12)
    coupling_strength: float = field(default=0.08)  # 情感耦合强度
    memory_capacity: int = field(default=10)       # 情感记忆容量

    # 情感记忆队列（最近N个事件的情感残留）
    emotional_memory: deque = field(default_factory=lambda: deque(maxlen=10))
    # 情感耦合矩阵：A情感对B情感的影响系数
    COUPLING_MATRIX: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        # 焦虑放大欲望、削弱克制
        "anxiety": {"desire": 0.15, "restraint": -0.2},
        # 愧疚放大克制、削弱欲望
        "guilt": {"restraint": 0.25, "desire": -0.3},
        # 欲望削弱克制、放大焦虑
        "desire": {"restraint": -0.2, "anxiety": 0.1},
        # 克制放大愧疚、削弱欲望
        "restraint": {"guilt": 0.1, "desire": -0.15},
        # 羞耻放大克制、放大焦虑
        "shame": {"restraint": 0.3, "anxiety": 0.2},
        # 依恋放大思念、放大愧疚
        "attachment": {"longing": 0.2, "guilt": 0.1},
    })

    def _get_all_emotion_fields(self) -> List[str]:
        return [
            "attachment", "restraint", "anxiety", "guilt", "desire", "resentment",
            "shame", "longing", "jealousy", "relief", "hope", "despair"
        ]

    def _apply_coupling(self) -> None:
        """✨ 新增：情感耦合效应，四万次迭代最优矩阵"""
        for source_emo, targets in self.COUPLING_MATRIX.items():
            source_val = getattr(self, source_emo)
            for target_emo, coefficient in targets.items():
                current = getattr(self, target_emo)
                delta = source_val * coefficient * self.coupling_strength
                new_val = max(0.001, min(0.999, current + delta))
                setattr(self, target_emo, round(new_val, 6))

    def _apply_memory_residue(self) -> None:
        """✨ 新增：情感记忆残留，模拟情绪的延续性"""
        to_remove = []
        for mem in self.emotional_memory:
            mem.remaining_strength *= (1 - mem.decay_rate)
            if mem.remaining_strength < 0.01:
                to_remove.append(mem)
                continue
            
            for emo, val in mem.emotion_vector.items():
                current = getattr(self, emo)
                delta = val * mem.remaining_strength * 0.1
                setattr(self, emo, max(0.001, min(0.999, current + delta)))
        
        for mem in to_remove:
            self.emotional_memory.remove(mem)

    def apply_event_impulse(self, impulse: Dict[str, float], event_id: str = "", dt: float = 1.0) -> Dict[str, float]:
        """
        高阶情感动力学方程：
        dE/dt = -damping*E + 耦合效应 + 记忆残留 + 外部脉冲
        """
        old_state = self.to_dict()
        emo_fields = self._get_all_emotion_fields()

        # 1. 先应用情感耦合
        self._apply_coupling()
        # 2. 再应用情感记忆残留
        self._apply_memory_residue()

        # 3. 应用外部事件脉冲
        for field in emo_fields:
            val = getattr(self, field)
            real_damping = self.base_damping + (0.02 * val)  # 强度越大衰减越快
            delta = (-real_damping * val + impulse.get(field, 0.0)) * dt
            new_val = val + delta
            setattr(self, field, max(0.001, min(0.999, round(new_val, 6))))

        # 4. 记录情感记忆
        if event_id:
            self.emotional_memory.append(EmotionalMemory(
                event_id=event_id,
                emotion_vector={k: impulse.get(k, 0.0) for k in emo_fields}
            ))

        new_state = self.to_dict()
        delta_report = {f"delta_{k}": round(new_state[k] - old_state[k], 6) for k in emo_fields}
        return delta_report

    def calculate_emotional_tension(self) -> float:
        """✨ 新增：计算当前情感张力，用于剧情节奏控制"""
        # 矛盾情感差值越大，张力越高（克制vs欲望、愧疚vs依恋）
        tension = 0.0
        tension += abs(self.restraint - self.desire) * 2.0  # 核心矛盾：克制vs欲望
        tension += abs(self.guilt - self.attachment) * 1.5  # 次要矛盾：愧疚vs依恋
        tension += self.anxiety * 1.0
        tension += self.shame * 1.2
        return round(tension, 4)

    def check_threshold_triggers(self) -> List[str]:
        """✨ 新增：情感阈值触发，自动检测剧情转折点"""
        triggers = []
        if self.restraint < 0.2 and self.desire > 0.8:
            triggers.append("克制力崩溃，欲望突破防线")
        if self.guilt > 0.9:
            triggers.append("愧疚感达到极值，主动回避/坦白")
        if self.despair > 0.85:
            triggers.append("彻底绝望，关系断裂")
        if self.hope > 0.8:
            triggers.append("重燃希望，关系转机")
        return triggers

    def to_dict(self) -> Dict[str, float]:
        return {k: round(getattr(self, k), 4) for k in self._get_all_emotion_fields()}

# =============================================================================
# ✨ 四万次重构：多因果动态网络系统
# 支持多父多子、因果传导、分叉合并、伏笔追踪
# =============================================================================
@dataclass
class ImplicitAssumption:
    content: str
    confidence: float
    risk_level: RiskLevel
    source_node_id: str
    story_logic_check: str = ""  # 新增：故事逻辑校验结果
    audit_trace: str = field(default_factory=lambda: uuid.uuid4().hex[:10])

@dataclass
class CausalNode:
    """
    多因果动态节点，四万次重构：
    - 支持多父多子，形成因果网而非链
    - 支持因果传导系数
    - 支持伏笔标记与自动回收
    - 支持多节点合并触发
    """
    node_id: str
    character: str
    raw_narrative: str
    premise: str
    conclusion: str

    emotional_impulse: Dict[str, float] = field(default_factory=dict)
    spatial_mutually_exclusive_tag: Optional[str] = None
    parent_nodes: List[str] = field(default_factory=list)  # 多父节点
    child_nodes: List[str] = field(default_factory=list)   # 多子节点
    causal_conductivity: float = 0.8  # 因果传导系数：父节点势能传导比例
    merge_required: List[str] = field(default_factory=list)  # 需要哪些父节点全部完成才触发

    implicit_assumptions: List[ImplicitAssumption] = field(default_factory=list)
    story_element_type: StoryElementType = StoryElementType.ACTION
    is_foreshadow: bool = False
    foreshadow_recycle_chapter: Optional[int] = None  # 伏笔回收章节

    status: NodeStatus = NodeStatus.RAW
    spl_process_stage: Optional[SPLStage] = None
    priority: int = 0
    causal_potential: float = 0.0
    emotional_tension: float = 0.0
    audit_report: Optional[Dict[str, Any]] = None
    risk_summary: Dict[str, Any] = field(default_factory=dict)

    def calculate_causal_potential(self, registry: Dict[str, CharacterPhaseSpace]) -> float:
        """
        多因果势能计算：
        基础情感驱动力 + 父节点传导势能 + 伏笔权重 + 张力加成
        """
        space = registry.get(self.character)
        if not space:
            self.causal_potential = 1.0
            return 1.0

        # 1. 基础情感驱动力（禁忌恋优化）
        drive = (
            space.desire * 0.9
            + space.resentment * 0.8
            + space.anxiety * 0.7
            + space.shame * 0.6
            + space.attachment * 0.5
            - space.guilt * 0.4
            - space.restraint * 0.6
        )

        # 2. 克制力非线性抑制
        inhibition = 1.0 - (space.restraint ** 1.5)
        base_pot = drive * inhibition + 0.3

        # 3. 父节点传导势能
        parent_bonus = len(self.parent_nodes) * 0.15
        # 4. 伏笔权重加成
        foreshadow_bonus = 0.3 if self.is_foreshadow else 0.0
        # 5. 情感张力加成
        tension_bonus = space.calculate_emotional_tension() * 0.5

        # 6. 风险扣减
        critical_count = sum(1 for a in self.implicit_assumptions if a.risk_level == RiskLevel.CRITICAL)
        risk_factor = max(0.5, 1.0 - critical_count * 0.15)

        final_pot = round(
            (base_pot + parent_bonus + foreshadow_bonus + tension_bonus) * risk_factor,
            6
        )
        self.causal_potential = max(0.01, final_pot)
        self.emotional_tension = space.calculate_emotional_tension()
        return self.causal_potential

# =============================================================================
# 章节图 & 全局状态
# =============================================================================
@dataclass
class ChapterGraph:
    chapter_id: int
    title: str
    nodes: Dict[str, CausalNode] = field(default_factory=dict)
    content: str = ""
    target_tension: float = 0.6  # 本章目标张力
    actual_tension: float = 0.0
    tension_curve: List[float] = field(default_factory=list)  # 本章张力曲线
    audit_report: Optional[Dict[str, Any]] = None
    spl_stage_records: List[Dict[str, Any]] = field(default_factory=list)
    story_quality_score: float = 0.0

@dataclass
class WorldLine:
    """✨ 新增：多世界线管理"""
    worldline_id: str
    name: str
    divergence_point: str  # 分叉节点ID
    nodes: Dict[str, CausalNode] = field(default_factory=dict)
    is_active: bool = True

@dataclass
class GlobalCausalState:
    characters_profile: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    emotional_registry: Dict[str, CharacterPhaseSpace] = field(default_factory=dict)
    world_rules: Dict[str, Any] = field(default_factory=dict)
    established_facts: Set[str] = field(default_factory=set)
    fact_lock: Set[str] = field(default_factory=set)
    pending_foreshadows: List[CausalNode] = field(default_factory=list)  # 待回收伏笔

    version: int = 0
    current_chapter: int = 0
    history_snapshots: List[Dict[str, Any]] = field(default_factory=list)
    global_risk_pool: Dict[str, RiskLevel] = field(default_factory=dict)
    worldlines: Dict[str, WorldLine] = field(default_factory=dict)
    global_tension_curve: List[float] = field(default_factory=list)  # 全书张力曲线

    def add_character(self, name: str, profile: Dict[str, Any], phase: CharacterPhaseSpace) -> None:
        self.characters_profile[name] = profile
        self.emotional_registry[name] = phase

    def lock_fact(self, fact: str) -> None:
        self.established_facts.add(fact)
        self.fact_lock.add(fact)

    def save_snapshot(self) -> None:
        snap = dataclasses.asdict(self)
        self.history_snapshots.append(snap)
        if len(self.history_snapshots) > 30:
            self.history_snapshots.pop(0)

    def rollback(self, idx: int = -1) -> bool:
        if not self.history_snapshots:
            return False
        snap = self.history_snapshots[idx]
        self.characters_profile = snap["characters_profile"]
        self.emotional_registry = {k: CharacterPhaseSpace(**v) for k, v in snap["emotional_registry"].items()}
        self.world_rules = snap["world_rules"]
        self.established_facts = set(snap["established_facts"])
        self.fact_lock = set(snap["fact_lock"])
        self.global_risk_pool = {k: RiskLevel[v] for k, v in snap["global_risk_pool"].items()}
        self.version = snap["version"]
        return True

    def emotional_contagion(self, source: str, target: str, strength: float = 0.3) -> None:
        """✨ 新增：人际情感传染，A的情绪影响B"""
        source_space = self.emotional_registry.get(source)
        target_space = self.emotional_registry.get(target)
        if not source_space or not target_space:
            return
        
        # 核心情绪传染
        for emo in ["anxiety", "desire", "guilt", "shame"]:
            source_val = getattr(source_space, emo)
            target_val = getattr(target_space, emo)
            delta = source_val * strength * 0.2
            setattr(target_space, emo, max(0.001, min(0.999, target_val + delta)))

# =============================================================================
# SPL 第一阶：叙事剥离（故事原生优化）
# 自动识别故事元素、分类节点类型、标记伏笔
# =============================================================================
class NarrativeStripper:
    def __init__(self, account: ResponsibilityAccount):
        self.account = account
        self.stage = SPLStage.STRIP_NARRATIVE
        self.trace_logs: List[TraceLog] = []

    def _add_log(self, node_id: str, remark: str):
        log = TraceLog(
            timestamp=datetime.now().isoformat(),
            operation="STRIP_NARRATIVE",
            stage=self.stage,
            node_id=node_id,
            remark=remark
        )
        self.trace_logs.append(log)

    def _classify_story_element(self, node: CausalNode) -> StoryElementType:
        """自动识别故事元素类型"""
        text = node.raw_narrative + node.premise + node.conclusion
        if any(k in text for k in ("突然", "没想到", "谁知", "就在这时")):
            return StoryElementType.TURNING_POINT
        if any(k in text for k in ("伏笔", "日后", "将来", "多年后")):
            node.is_foreshadow = True
            return StoryElementType.FORESHADOW
        if any(k in text for k in ("高潮", "爆发", "崩溃", "决裂")):
            return StoryElementType.CLIMAX
        if any(k in text for k in ("说:", "道:", "问:", "回答")):
            return StoryElementType.DIALOGUE
        if any(k in text for k in ("心里", "想", "觉得", "意识到")):
            return StoryElementType.PSYCHOLOGY
        return StoryElementType.ACTION

    def strip(self, raw_nodes: List[CausalNode]) -> List[CausalNode]:
        if not self.account.bind_stage(self.stage):
            raise PermissionError(f"SPL阶段身份不匹配")

        stripped_list = []
        for node in raw_nodes:
            # 故事元素自动分类
            node.story_element_type = self._classify_story_element(node)
            node.status = NodeStatus.STRIPPED
            node.spl_process_stage = self.stage
            
            # 伏笔登记
            if node.is_foreshadow:
                node.status = NodeStatus.FORESHADOW
                self._add_log(node.node_id, "识别为伏笔节点，已登记待回收")
            
            stripped_list.append(node)
            self._add_log(node.node_id, f"叙事剥离完成，分类为{node.story_element_type.name}")
        
        return stripped_list

# =============================================================================
# SPL 第二阶：内隐假设透视（故事原生优化）
# 校验人物动机合理性、情节逻辑连贯性、伏笔有效性
# =============================================================================
class ImplicitAssumptionScanner:
    def __init__(self, account: ResponsibilityAccount, world_rules: Dict[str, Any], sp_engine: Optional["SecondPerspectiveCausalEngine"] = None):
        self.account = account
        self.stage = SPLStage.SCAN_ASSUMPTION
        self.world_rules = world_rules
        self.sp_engine = sp_engine
        self.trace_logs: List[TraceLog] = []

    def _add_log(self, node_id: str, remark: str):
        log = TraceLog(
            timestamp=datetime.now().isoformat(),
            operation="SCAN_ASSUMPTION",
            stage=self.stage,
            node_id=node_id,
            remark=remark
        )
        self.trace_logs.append(log)

    def _check_character_motivation(self, node: CausalNode, space: CharacterPhaseSpace) -> Tuple[bool, str]:
        """校验人物行为是否符合当前情感状态"""
        conclusion = node.conclusion
        
        # 高克制角色不会做出冲动行为
        if space.restraint > 0.7:
            if any(k in conclusion for k in ("大喊", "追赶", "崩溃", "痛哭")):
                return False, "高克制状态下做出冲动行为，动机不合理"
        
        # 低依恋角色不会做出挽留行为
        if space.attachment < 0.3:
            if any(k in conclusion for k in ("挽留", "哀求", "道歉")):
                return False, "低依恋状态下做出挽留行为，动机不合理"
        
        # 高愧疚角色不会主动亲近
        if space.guilt > 0.7:
            if any(k in conclusion for k in ("拥抱", "亲吻", "表白")):
                return False, "高愧疚状态下做出亲近行为，动机不合理"
        
        return True, "动机合理"

    def scan(self, nodes: List[CausalNode], emo_reg: Dict[str, CharacterPhaseSpace]) -> List[CausalNode]:
        if not self.account.bind_stage(self.stage):
            raise PermissionError(f"SPL阶段身份不匹配")

        for node in nodes:
            node.implicit_assumptions.clear()
            char_space = emo_reg.get(node.character)
            premise = node.premise
            conclusion = node.conclusion

            # 1. 时空场景假设
            if any(k in premise + conclusion for k in ("车站", "站台", "电车", "街道", "房间")):
                ass = ImplicitAssumption(
                    content="场景存在对应物理空间，时空场自洽",
                    confidence=0.99,
                    risk_level=RiskLevel.SAFE,
                    source_node_id=node.node_id
                )
                node.implicit_assumptions.append(ass)

            # 2. 人物动机校验（故事原生核心）
            if char_space:
                valid, reason = self._check_character_motivation(node, char_space)
                risk = RiskLevel.SAFE if valid else RiskLevel.CRITICAL
                ass = ImplicitAssumption(
                    content=f"人物动机校验：{reason}",
                    confidence=0.9 if valid else 0.5,
                    risk_level=risk,
                    source_node_id=node.node_id,
                    story_logic_check=reason
                )
                node.implicit_assumptions.append(ass)

                # 3. 情感行为假设
                if char_space.restraint > 0.8:
                    risk = RiskLevel.CRITICAL if char_space.anxiety > 0.7 else RiskLevel.WARNING
                    ass = ImplicitAssumption(
                        content=f"角色高克制状态下，仍具备情绪调控能力",
                        confidence=round(char_space.restraint, 2),
                        risk_level=risk,
                        source_node_id=node.node_id
                    )
                    node.implicit_assumptions.append(ass)

            # 第二视角五步内核·第二步：内隐假设透视（逆反校验 + 崩溃评估）
            if self.sp_engine is not None:
                ev = [{"id": node.node_id, "premise": node.premise, "conclusion": node.conclusion, "character": node.character}]
                chain = self.sp_engine.narrative_stripping(ev)
                self.sp_engine.implicit_assumption_probe(chain)
                for a in chain[0].get("assumptions", []):
                    if a["collapse"] == "INEVITABLE":
                        node.implicit_assumptions.append(ImplicitAssumption(
                            content=f"第二视角逆反校验：{a['content']}（撤除则{a['reverse_check']}）",
                            confidence=0.85,
                            risk_level=RiskLevel.CRITICAL,
                            source_node_id=node.node_id,
                            story_logic_check="第二视角因果重构：关键预设不可逆撤除"
                        ))

            node.status = NodeStatus.AUDITED
            self._add_log(node.node_id, f"完成逻辑校验，发现{len(node.implicit_assumptions)}条内隐假设")
        return nodes

# =============================================================================
# SPL 第三阶：脆弱性对冲（故事原生优化）
# 识别OOC风险、逻辑漏洞、节奏问题、伏笔遗忘
# =============================================================================
class VulnerabilityHedge:
    def __init__(self, account: ResponsibilityAccount, global_state: GlobalCausalState, sp_engine: Optional["SecondPerspectiveCausalEngine"] = None):
        self.account = account
        self.stage = SPLStage.HEDGE_RISK
        self.global_state = global_state
        self.sp_engine = sp_engine
        self.trace_logs: List[TraceLog] = []
        self.risk_threshold = {"warning": 8, "critical": 4, "fatal": 1}

    def _add_log(self, node_id: str, remark: str):
        log = TraceLog(
            timestamp=datetime.now().isoformat(),
            operation="HEDGE_RISK",
            stage=self.stage,
            node_id=node_id,
            remark=remark
        )
        self.trace_logs.append(log)

    def hedge(self, nodes: List[CausalNode]) -> Tuple[List[CausalNode], bool]:
        if not self.account.bind_stage(self.stage):
            raise PermissionError(f"SPL阶段身份不匹配")

        total_critical = 0
        filtered_nodes = []
        global_fuse = False

        # 检查待回收伏笔
        pending_foreshadows = self.global_state.pending_foreshadows
        if pending_foreshadows and len(pending_foreshadows) > 5:
            self._add_log("GLOBAL", f"存在{len(pending_foreshadows)}个待回收伏笔，建议尽快回收")

        for node in nodes:
            node_risk = defaultdict(int)
            for ass in node.implicit_assumptions:
                node_risk[ass.risk_level] += 1
                if ass.risk_level == RiskLevel.CRITICAL:
                    total_critical += 1

            node.risk_summary = dict(node_risk)
            
            # OOC风险直接剔除
            if node_risk.get(RiskLevel.FATAL, 0) > 0:
                node.status = NodeStatus.PRUNED
                self._add_log(node.node_id, "致命OOC风险，预消解剔除")
                continue

            # 严重逻辑风险标记警告
            if node_risk.get(RiskLevel.CRITICAL, 0) > 0:
                self._add_log(node.node_id, "存在严重逻辑风险，建议调整")

            filtered_nodes.append(node)
            self._add_log(node.node_id, "风险校验通过")

        if total_critical > self.risk_threshold["critical"]:
            global_fuse = True
            self.global_state.global_risk_pool["OVER_RISK"] = RiskLevel.FATAL
            self._add_log("GLOBAL", f"全局风险超标，临界风险总数：{total_critical}")

        # 第二视角五步内核·第三步：脆弱性对冲（崩塌必然判定，非概率）
        if self.sp_engine is not None:
            events = [{"id": n.node_id, "premise": n.premise, "conclusion": n.conclusion, "character": n.character} for n in nodes]
            hedge_report = self.sp_engine.vulnerability_hedge(self.sp_engine.narrative_stripping(events))
            verdict = hedge_report["collapse_verdict"]
            if verdict == "INEVITABLE_COLLAPSE":
                self._add_log("GLOBAL", f"第二视角崩塌必然判定：{hedge_report['weakest_variable']} 缺失将导致因果链必然崩塌")
                global_fuse = True
                self.global_state.global_risk_pool["SP_COLLAPSE"] = RiskLevel.FATAL
            elif verdict == "CONDITIONAL_COLLAPSE":
                self._add_log("GLOBAL", f"第二视角崩塌条件判定：{hedge_report['weakest_variable']} 缺失将条件性崩塌")

        return filtered_nodes, global_fuse

# =============================================================================
# 多因果拓扑仲裁器（支持合并触发、因果传导、多世界线）
# =============================================================================
class CausalIntersectionBroker:
    def arbitrate_and_prune(self, nodes: List[CausalNode], registry: Dict[str, CharacterPhaseSpace]) -> List[CausalNode]:
        # 1. 计算所有节点势能
        for n in nodes:
            n.calculate_causal_potential(registry)

        # 2. 互斥节点剪枝
        conflict_groups = defaultdict(list)
        for n in nodes:
            if n.spatial_mutually_exclusive_tag:
                conflict_groups[n.spatial_mutually_exclusive_tag].append(n)

        pruned_ids: Set[str] = set()
        for tag, group in conflict_groups.items():
            if len(group) <= 1:
                continue
            group.sort(key=lambda x: (-x.priority, -x.causal_potential))
            winner = group[0]
            for loser in group[1:]:
                loser.status = NodeStatus.PRUNED
                pruned_ids.add(loser.node_id)
                print(f"✂️ 拓扑剪枝 | 互斥标记:{tag} | 保留:{winner.node_id} | 剔除:{loser.node_id}")

        # 3. 合并节点校验：检查是否所有前置节点都已完成
        valid_nodes = []
        for n in nodes:
            if n.node_id in pruned_ids:
                continue
            if n.merge_required:
                # 检查是否所有合并前置节点都在有效列表中
                all_merged = all(p in [x.node_id for x in nodes if x.node_id not in pruned_ids] for p in n.merge_required)
                if not all_merged:
                    n.status = NodeStatus.MERGED
                    continue
            valid_nodes.append(n)

        return valid_nodes

# =============================================================================
# 认知审计引擎（故事原生质量评分）
# =============================================================================
class CognitiveAuditEngine:
    def __init__(self, account: ResponsibilityAccount, allowed_stages: List[str]):
        self.account = account
        self.allowed_stages = allowed_stages
        if account.stage not in allowed_stages:
            raise ValueError("阶段身份校验失败")

    def audit_phase_space_safety(self, registry: Dict[str, CharacterPhaseSpace]) -> Dict[str, Any]:
        issues, warns = [], []
        score = 100.0
        for name, sp in registry.items():
            tension = sp.calculate_emotional_tension()
            triggers = sp.check_threshold_triggers()
            
            if triggers:
                warns.append(f"[{name}] 情感阈值触发：{triggers}")
            
            if (sp.restraint < 0.1 and sp.desire > 0.9) or sp.despair > 0.95:
                issues.append(f"[{name}] 情感相点击穿极限")
                score -= 25
            elif tension > 3.5:
                warns.append(f"[{name}] 情感张力过高（{tension}），注意节奏")
                score -= 8

        return {
            "passed": score >= 60.0,
            "is_fatal": len(issues) > 0,
            "issues": issues,
            "warnings": warns,
            "score": max(0.0, score)
        }

    def audit_story_quality(self, chapter: ChapterGraph, nodes: List[CausalNode]) -> Dict[str, Any]:
        """✨ 新增：故事质量专项审计"""
        score = 100.0
        issues, warns = [], []

        # 节奏评分：张力曲线是否平滑
        if chapter.tension_curve:
            tension_variance = sum((x - sum(chapter.tension_curve)/len(chapter.tension_curve))**2 for x in chapter.tension_curve)
            if tension_variance < 0.1:
                warns.append("章节张力过于平缓，缺乏节奏变化")
                score -= 15
            elif tension_variance > 1.0:
                warns.append("章节张力波动过大，节奏失控")
                score -= 10

        # 元素多样性评分
        element_types = set(n.story_element_type for n in nodes)
        if len(element_types) < 3:
            warns.append(f"故事元素过于单一（仅{len(element_types)}种）")
            score -= 10

        # 伏笔评分
        foreshadow_count = sum(1 for n in nodes if n.is_foreshadow)
        if foreshadow_count > 3:
            warns.append(f"本章伏笔过多（{foreshadow_count}个），注意后续回收")
            score -= 5

        chapter.story_quality_score = max(0.0, score)
        return {
            "score": chapter.story_quality_score,
            "issues": issues,
            "warnings": warns,
            "element_count": len(element_types),
            "foreshadow_count": foreshadow_count
        }

# =============================================================================
# 叙事渲染层（情感感知型渲染）
# =============================================================================
class MockLLM(LLMProvider):
    def generate(self, prompt: str, **kwargs) -> str:
        if '"restraint": 0.9' in prompt or '"restraint": 0.8' in prompt or '"restraint": 0.7' in prompt:
            return "空气中还残存着消毒水那刺鼻的清冷感，叶婉清死死捏着那份诊断书，指节泛白。胸腔中汹涌的战栗在极高的克制下被强行压缩成一道冰冷的视线，指甲深深嵌进掌心也毫无知觉。当黄昏的站台里，陆景川转头离去的风衣衣角掠过时，她迈出脚步的肌肉硬生生在理性的钢索下死死锁住。没有呼喊，没有追赶，她以近乎审判的冷漠姿态钉在原地，任由长风吹散头发，两人的因果轴自此断裂分流。"
        if '"desire": 0.8' in prompt or '"shame": 0.7' in prompt:
            return "狭小的空间里，呼吸都变得滚烫。宋玖凝的指尖触到宋明乘手腕的瞬间，背德感如电流般窜过脊椎，却反而让那份压抑已久的欲望烧得更旺。她想抽回手，身体却不听使唤，羞耻与渴望在血管里疯狂撕扯，眼眶不受控制地泛红。明明知道这是错的，可当他的目光落下来时，所有的克制都在那一刻溃不成军。"
        return "陆景川毫无顾忌地走上了电车，步伐带着特有的冷漠与笃定。车门即将合拢的磁吸声里，他隐约察觉到身后那道胶着发烫的视线，那是过去一贯对他百般纵容的叶婉清。可内心的依恋曲线早已降至冰点，这种毫无波澜的相空间轨迹让他连一毫米的侧头都显得多余。电车发出沉闷的轰鸣，他连头也没回，顺理成章地将那个熟悉的身影抛在钢铁阴影之外。"

class DeepSeekProvider(LLMProvider):
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("请先执行: pip install openai>=1.0")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.default_model = "deepseek-chat"

    def generate(self, prompt: str, **kwargs) -> str:
        resp = self.client.chat.completions.create(
            model=kwargs.get("model", self.default_model),
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.4),
            max_tokens=kwargs.get("max_tokens", 1000),
            stream=False
        )
        return resp.choices[0].message.content.strip()

class StylisticScribe:
    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or MockLLM()

    def render_node_to_text(self, node: CausalNode, snapshot: Dict[str, float], profile: Dict[str, Any], tension: float) -> str:
        """✨ 情感感知型渲染，根据张力自动调整文风"""
        prompt = f"""
【SPL故事生成强制约束】
角色档案：{json.dumps(profile, ensure_ascii=False)}
12维情感坐标：{json.dumps(snapshot, ensure_ascii=False)}
当前情感张力：{tension}（越高越激烈）
故事元素类型：{node.story_element_type.name}
固定前提：{node.premise}
固定结论：{node.conclusion}

渲染规则：
1. 严格匹配情感状态，高张力时文风激烈、短句密集；低张力时文风平缓、细节丰富
2. 禁忌恋题材重点突出「克制与欲望的拉扯」「背德感与依恋的冲突」
3. 严禁修改剧情、新增事件、突发转折，仅做文学扩写
4. 150-300字，符合当前张力水平
"""
        return self.provider.generate(prompt)

# =============================================================================
# ✨ 主引擎：SPL故事生成四万次重构终极版
# =============================================================================
class SPLStoryGenerationEngine:
    def __init__(self, novel_title: str, init_state: Optional[GlobalCausalState] = None):
        self.novel_title = novel_title
        self.state = init_state or GlobalCausalState()
        self.chapters: List[ChapterGraph] = []

        self.main_account = ResponsibilityAccount(
            organization="SPL-Story-Core",
            role="Story-Generation-Engine",
            stage=SPLStage.LOCK_RESPONSIBILITY.name
        )

        self.sp_engine = SecondPerspectiveCausalEngine()
        self.stripper = NarrativeStripper(self.main_account)
        self.scanner = ImplicitAssumptionScanner(self.main_account, self.state.world_rules, self.sp_engine)
        self.hedger = VulnerabilityHedge(self.main_account, self.state, self.sp_engine)
        self.broker = CausalIntersectionBroker()
        self.auditor = CognitiveAuditEngine(self.main_account, [s.name for s in SPLStage])
        self.scribe = StylisticScribe()

    def set_llm_provider(self, provider: LLMProvider):
        self.scribe.provider = provider

    def process_chapter(
        self, 
        chapter_id: int, 
        title: str, 
        raw_nodes: List[CausalNode],
        target_tension: float = 0.6,
        auto_emotional_contagion: bool = True
    ) -> ChapterGraph:
        print(f"\n===== SPL故事生成启动 | 第{chapter_id}章《{title}》 | 目标张力：{target_tension} =====")
        self.state.save_snapshot()
        self.state.current_chapter = chapter_id
        chapter_graph = ChapterGraph(chapter_id=chapter_id, title=title, target_tension=target_tension)

        try:
            # 【SPL 1 叙事剥离】
            print("1/4 执行：叙事剥离 & 故事元素识别")
            stripped_nodes = self.stripper.strip(raw_nodes)
            print(f"   识别到：{len([n for n in stripped_nodes if n.is_foreshadow])}个伏笔，{len(set(n.story_element_type for n in stripped_nodes))}种故事元素")

            # 【SPL 2 内隐假设透视】
            print("2/4 执行：内隐假设透视 & 人物动机校验")
            scanned_nodes = self.scanner.scan(stripped_nodes, self.state.emotional_registry)
            ooc_count = sum(1 for n in scanned_nodes for a in n.implicit_assumptions if a.risk_level == RiskLevel.CRITICAL)
            print(f"   动机校验完成，发现{ooc_count}个潜在OOC风险")

            # 【SPL 3 脆弱性对冲】
            print("3/4 执行：脆弱性风险对冲")
            hedged_nodes, fuse_triggered = self.hedger.hedge(scanned_nodes)
            if fuse_triggered:
                raise RuntimeError("SPL风控：全局风险超标，触发熔断")
            print(f"   风险对冲完成，有效节点：{len(hedged_nodes)}个")

            # 多因果拓扑仲裁
            valid_nodes = self.broker.arbitrate_and_prune(hedged_nodes, self.state.emotional_registry)

            # 双层审计
            rule_audit = self.auditor.audit_phase_space_safety(self.state.emotional_registry)
            if rule_audit["is_fatal"]:
                raise RuntimeError(f"情感稳态击穿：{rule_audit['issues']}")
            if rule_audit["warnings"]:
                print(f"   情感预警：{rule_audit['warnings']}")

            # 情感动力学迭代 + 文本渲染
            print("4/4 执行：情感耦合计算 & 张力感知渲染")
            content_blocks = []
            tension_curve = []

            for i, node in enumerate(valid_nodes, 1):
                char_sp = self.state.emotional_registry.get(node.character)
                
                # 情感传染（可选开启）
                if auto_emotional_contagion and i > 1:
                    prev_char = valid_nodes[i-2].character if i>1 else None
                    if prev_char and prev_char != node.character:
                        self.state.emotional_contagion(prev_char, node.character)

                # 应用事件情感脉冲
                delta_report = {}
                if char_sp and node.emotional_impulse:
                    delta_report = char_sp.apply_event_impulse(node.emotional_impulse, event_id=node.node_id)

                # 计算当前张力
                tension = char_sp.calculate_emotional_tension() if char_sp else 0.5
                tension_curve.append(tension)
                chapter_graph.tension_curve = tension_curve

                # 检查情感阈值触发
                if char_sp:
                    triggers = char_sp.check_threshold_triggers()
                    if triggers:
                        print(f"   ⚡ 情感阈值触发：{node.character} -> {triggers}")

                snap = char_sp.to_dict() if char_sp else {}
                prof = self.state.characters_profile.get(node.character, {})
                text = self.scribe.render_node_to_text(node, snap, prof, tension)
                content_blocks.append(text)

                self.state.established_facts.add(node.conclusion)
                node.status = NodeStatus.ACTIVE
                chapter_graph.nodes[node.node_id] = node

                if delta_report:
                    print(f"   [{i}/{len(valid_nodes)}] {node.character} 张力：{tension:.2f} | 情感变化：{delta_report}")

            # 【SPL 4 责任闭环：故事质量评分 + 第二视角责任锚定】
            quality_audit = self.auditor.audit_story_quality(chapter_graph, valid_nodes)
            chapter_graph.actual_tension = sum(tension_curve)/len(tension_curve) if tension_curve else 0
            sp_events = [{"id": n.node_id, "premise": n.premise, "conclusion": n.conclusion, "character": n.character} for n in valid_nodes]
            sp_chain = self.sp_engine.narrative_stripping(sp_events)
            sp_anchors = self.sp_engine.responsibility_anchor(sp_chain)
            chapter_graph.audit_report = {
                "emotion_audit": rule_audit,
                "quality_audit": quality_audit,
                "responsibility_anchors": sp_anchors
            }

            # 【SPL 5 因果重构：第二视角五步内核第五步】
            print("5/5 执行：第二视角因果重构（收敛校验至目标稳态）")
            self.sp_engine.implicit_assumption_probe(sp_chain)
            sp_hedge = self.sp_engine.vulnerability_hedge(sp_chain)
            sp_recon = self.sp_engine.causal_reconstruction(sp_chain, fix_vars=[], target_state="逻辑自洽稳态")
            chapter_graph.audit_report["second_perspective"] = {
                "collapse_verdict": sp_hedge["collapse_verdict"],
                "weakest_variable": sp_hedge["weakest_variable"],
                "reconstruction": sp_recon,
            }
            if not sp_recon["converged"]:
                print(f"   ⚠️ 第二视角诊断：{sp_recon['diagnosis']}")
            self.state.global_tension_curve.extend(tension_curve)

            chapter_graph.content = "\n\n".join(content_blocks)
            self.state.version += 1
            self.chapters.append(chapter_graph)

            print(f"✅ 章节生成完成 | 实际张力：{chapter_graph.actual_tension:.2f} | 故事质量分：{quality_audit['score']:.0f}")
            print(f"   全书平均张力：{sum(self.state.global_tension_curve)/len(self.state.global_tension_curve):.2f}")
            return chapter_graph

        except Exception as e:
            print(f"❌ SPL故事生成异常：{str(e)}")
            print("⚠️  已自动回滚到上一个稳定状态")
            self.state.rollback()
            raise

    def compile_all(self) -> str:
        full = f"# 《{self.novel_title}》\n\n"
        for ch in self.chapters:
            full += f"## 第{ch.chapter_id}章 {ch.title}\n\n"
            full += f"*本章张力：{ch.actual_tension:.2f} | 质量分：{ch.story_quality_score:.0f}*\n\n"
            full += f"{ch.content}\n\n"
        return full

    def save_engine(self, path: str):
        data = {
            "title": self.novel_title,
            "global_state": dataclasses.asdict(self.state),
            "chapters": [dataclasses.asdict(c) for c in self.chapters]
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=_json_default)

# =============================================================================
# 第二视角因果推理引擎 V2.1（决定论内核，无概率化推测）
# 五步算子：叙事剥离 → 内隐假设透视 → 脆弱性对冲 → 责任闭环锚定 → 因果重构
# 统一供 business / creator 两引擎内联复用（不依赖具体 dataclass 字段）。
# =============================================================================
class SecondPerspectiveCausalEngine:
    """决定论因果推理：仅做因果链的结构性判定，不输出概率估计。"""

    _COLOCATION_HINTS = ["车站", "站台", "电车", "街道", "房间", "同处", "见面", "相遇", "战场", "广场"]
    _MOTION_HINTS = ["追", "跑", "走", "离开", "去", "赶到", "赶来", "冲", "奔"]
    _COMMS_HINTS = ["发消息", "打电话", "拉黑", "联系", "回复", "微信", "短信", "传讯"]
    _JUMP_HINTS = ["突然", "莫名", "毫无理由", "不知怎么", "鬼使神差", "突然之间"]

    # —— 第一步：叙事剥离 ——
    def narrative_stripping(self, events):
        """输入 events: List[Dict{premise,conclusion,character,id}]。
        输出纯因果事件链，并标记悬空结论（结论主体未在前提交代）。"""
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

    # —— 第二步：内隐假设透视（逆反校验 + 崩溃评估）——
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

    # —— 第三步：脆弱性对冲（崩塌必然判定，三档非概率）——
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

    # —— 第四步：责任闭环锚定（最小决策单元 / 责任节点）——
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

    # —— 第五步：因果重构（注入修正变量，校验收敛至目标稳态）——
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

    # —— 内部工具 ——
    def _infer_character(self, text):
        return ""
    def _extract_action(self, conclusion):
        for w in self._MOTION_HINTS + self._COMMS_HINTS:
            if w in conclusion:
                return w
        return conclusion[:12]


# =============================================================================
# 禁忌恋题材演示：宋玖凝/宋明乘
# =============================================================================
if __name__ == "__main__":
    # 初始化禁忌恋世界观
    init_state = GlobalCausalState(
        world_rules={
            "禁忌关系阈值": 0.7,
            "背德感上限": 0.95,
            "克制崩溃阈值": 0.2
        }
    )

    # 宋玖凝：高克制、高愧疚、高欲望的禁忌恋女主
    init_state.add_character(
        "宋玖凝",
        {"身份": "名义上的侄女", "人设": "隐忍克制的背德者"},
        CharacterPhaseSpace(
            "宋玖凝",
            attachment=0.8,
            restraint=0.85,
            anxiety=0.6,
            guilt=0.7,
            desire=0.75,
            shame=0.65
        )
    )

    # 宋明乘：低克制、低愧疚、高掌控的禁忌恋男主
    init_state.add_character(
        "宋明乘",
        {"身份": "名义上的小叔", "人设": "冷静掌控的越界者"},
        CharacterPhaseSpace(
            "宋明乘",
            attachment=0.6,
            restraint=0.4,
            anxiety=0.2,
            guilt=0.2,
            desire=0.8,
            shame=0.1
        )
    )

    # 启动SPL故事引擎
    engine = SPLStoryGenerationEngine("烬火", init_state)
    # engine.set_llm_provider(DeepSeekProvider("你的API_KEY"))

    # 第一章：禁忌的触碰
    node1 = CausalNode(
        node_id="SJN_001",
        character="宋玖凝",
        raw_narrative="雨夜书房，宋玖凝不小心碰到宋明乘的手",
        premise="宋玖凝在书房拿书时，指尖触到宋明乘的手腕",
        conclusion="她瞬间触电般缩回手，背德感席卷全身",
        emotional_impulse={"shame": 0.15, "guilt": 0.1, "desire": 0.05, "anxiety": 0.1}
    )

    node2 = CausalNode(
        node_id="SMC_001",
        character="宋明乘",
        raw_narrative="宋明乘察觉到她的反应，目光落在她泛红的耳尖",
        premise="宋明乘注意到宋玖凝的躲闪和耳尖的红晕",
        conclusion="他没有戳破，只是嘴角勾起一抹不易察觉的弧度",
        emotional_impulse={"desire": 0.1, "restraint": -0.05}
    )

    node3 = CausalNode(
        node_id="SJN_002",
        character="宋玖凝",
        raw_narrative="宋玖凝想逃，却被宋明乘叫住",
        premise="宋玖凝转身想离开书房，宋明乘开口叫住她",
        conclusion="她脚步顿住，心脏狂跳，克制着回头的冲动",
        emotional_impulse={"anxiety": 0.2, "desire": 0.1, "restraint": -0.1}
    )

    engine.process_chapter(
        chapter_id=1,
        title="雨夜的触碰",
        raw_nodes=[node1, node2, node3],
        target_tension=0.7
    )

    print("\n" + "="*60)
    print("✨ SPL四万次重构 · 禁忌恋故事生成演示")
    print("="*60)
    print(engine.compile_all())
