<p align="center">
  <img src="assets/banner.png" alt="STORY-ENGINE banner" style="width:100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/nlp-D4AF37?style=flat-square" alt="nlp">
  <img src="https://img.shields.io/badge/consistency-D4AF37?style=flat-square" alt="consistency">
  <img src="https://img.shields.io/badge/long--form-D4AF37?style=flat-square" alt="long-form">
  <img src="https://img.shields.io/badge/second--perspective-D4AF37?style=flat-square" alt="second-perspective">
</p>

<blockquote align="center">
  <em>Long-Form Narrative Consistency Engine</em>
</blockquote>

<div style="max-width:880px;margin:0 auto;padding:0 16px">

## ✦ About

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">STORY-ENGINE 由两款定位清晰的产品组成：</p>

<ul style="font-size:15px;line-height:1.8;color:#2C2C2C">
  <li><strong>故事引擎（面向创作者与大众）</strong> — 长篇小说一致性引擎，对角色设定、因果时间线、记忆线做自动化审计，让百万字作品在人物、情节、世界观上保持一致；并提供 SPL 四阶段叙事编辑流水线。将编辑的直觉校验转化为可复用的结构化流程。</li>
  <li><strong>文书审查引擎（面向企业）</strong> — 零依赖、可离线的企业级文书合规审查引擎，对合同、制度、公文、通用文本做条款级规则扫描与文档级审计（要素完整性 / 一致性 / 权利义务对等 / 格式），并输出可追溯的审查报告。</li>
</ul>

<p align="center">
  <img src="assets/overview.png" alt="STORY-ENGINE overview" style="width:100%">
</p>

</div>

<p align="center">— ✦ —</p>

## ✦ Design Direction

<div style="max-width:880px;margin:0 auto;padding:0 16px">

STORY-ENGINE 由两款独立产品组成，分别面向不同用户群体：

| 产品 | 面向用户 | 模块 | 典型输入 |
|------|----------|------|----------|
| **故事引擎** | 创作者 / 大众 | `Story Engine for Creator.py` + `engine for business.py` | 角色 / 因果时间线 / 世界观 / 叙事元素 |
| **文书审查引擎** | 企业 | `compliance_engine/` | 合同 / 制度 / 公文 / 通用文档 |

两款产品共享同一套**决定论式审计设计语言**——责任闭环锚定（`ResponsibilityAccount`）、风险分级与全链路可追溯日志。文书审查引擎为相对独立的离线规则模块，**不依赖 LLM**，纯规则库、零第三方依赖、可离线运行，专门服务企业文档合规场景。

</div>

<p align="center">— ✦ —</p>

## ✦ Quick Start

```bash
# Primary: GitHub
git clone https://github.com/nohn3043-arch/story-engine.git
# Mirror: Gitee
# git clone https://gitee.com/sjiun/Story-engine.git
cd Story-engine
# Pure Python >=3.8. Engine files intentionally use space-separated names.
python "Story Engine for Creator.py"      # creator-facing second-perspective cognitive audit engine
# or: python "engine for business.py"     # SPL four-stage editorial pipeline
```

<p align="center">— ✦ —</p>

## ✦ Features

<div style="max-width:880px;margin:0 auto;padding:0 16px">

STORY-ENGINE 由两款产品组成，分别服务不同用户群体：

### 故事引擎（面向创作者与大众）

长篇小说一致性引擎，将编辑的直觉校验转化为可复用的结构化流程。包含两层：

- **Creator Engine**（`Story Engine for Creator.py`）——面向叙事的认知审计层：
  - `ResponsibilityAccount`——每项检查锚定到具名责任节点（谁 / 角色 / 阶段）。
  - `CognitiveAuditEngine` + 可插拔 `AuditPlugin` + `EmotionalConstraint`——可组合审计维度。
  - `CausalNode` 携带 `implicit_assumptions` 与 `vulnerability_score`——追踪 *因为 → 所以* 逻辑并量化脆弱性。
  - `NarrativeStripper` / `ImplicitAssumptionDetector` / `VulnerabilityAssessor`——第二视角算子流水线。
  - `AutomaticRepairEngine`（全量跳跃词修复）/ `UltimateCausalNovelEngine` / `SecondPerspectiveCausalEngine` / `WorldBuilder`（分词级世界观提取）——修复、全书审计与世界观构建层。
- **Business Engine**（`engine for business.py`）——SPL 四阶段原生推理流水线：
  1. `STRIP_NARRATIVE`——识别叙事元素（伏笔 / 转折 / 高潮 / 铺垫）。
  2. `SCAN_ASSUMPTION`——`ImplicitAssumptionScanner` 校验动机与剧情逻辑。
  3. `HEDGE_RISK`——`VulnerabilityHedge` 标记 OOC、逻辑漏洞、节奏问题；`CausalIntersectionBroker` 合并世界线。
  4. `LOCK_RESPONSIBILITY`——输出带可追溯优化的质量评分。
  - 风险级别：`SAFE` / `WARNING` / `CRITICAL` / `FATAL`；节点状态：`RAW` / `STRIPPED` / `AUDITED` / `PRUNED` / `ACTIVE`。
  - `SPLStoryGenerationEngine` + `StylisticScribe` 驱动生成；`DeepSeekProvider` / `MockLLM` 为可替换 LLM 后端。

### 文书审查引擎（面向企业）

企业级文书合规审查引擎（`compliance_engine/`），零依赖、可离线运行：

- 支持合同 / 制度 / 公文 / 通用四类文书的条款级规则扫描 + 文档级审计（要素完整性 / 一致性 / 权利义务对等 / 格式）。
- `ComplianceEngine` 编排：分节 → 规则扫描 → 文档级审计 → 责任闭环 → 评分 → 报告。
- `ResponsibilityAccount` 责任闭环锚定 + `TraceLog` 全链路可追溯；判定为决定论式（命中即判定），不输出概率。
- `RuleEngine` 加载纯 JSON 规则库（可 `--rules-dir` 外部扩展）；四类 `Auditor` 与条款级命中互补。
- 报告支持 HTML（可视化）/ JSON（结构化）/ Markdown（归档）三格式；完整 CLI：`audit` / `list-rules` / `demo`。

两款产品共享同一套决定论式审计设计语言（责任闭环锚定、风险分级、全链路可追溯），但分别面向创意叙事与企业文档两类场景。

**Robustness hardening (2026-08 fixes)**:
- **Character-name plausibility filter** — `_extract_plausible_name` excludes pronouns / verb phrases / weather-scene words, preferring absence over noise: `"坚持己见" → ""`, `"他说：我们走吧" → ""`, `"林夏在评审会上坚持自研方案" → "林夏"`.
- **Token-level worldbuilding extraction** — `WorldBuilder` pre-tokenizes on connectives / punctuation, then matches whole words with longest-suffix priority: `"青云宗与魔道势力在苍云大陆" → factions ["青云宗","魔道势力"], geography ["苍云大陆"]`, connectives are no longer swallowed.
- **Full-text revision replacement** — `AutomaticRepairEngine` replaces all stiff transition words at once (`突然 / 莫名 / 鬼使神差 …`) and merges adjacent duplicate transition phrases.
- **Engine isolation detection** — both engines embed `_ENGINE_FINGERPRINT` and `check_engine_isolation()`: mixing both in one process warns immediately, preventing data corruption and crashes caused by homonymous but heterogeneous data classes (`CausalNode` / `ResponsibilityAccount`, etc.) overwriting each other.

**鲁棒性加固（2026-08 修复）**：
- **角色名可信度过滤**——`_extract_plausible_name` 排除代词 / 动词短语 / 天气场景词，宁缺毋滥：`"坚持己见" → ""`、`"他说：我们走吧" → ""`、`"林夏在评审会上坚持自研方案" → "林夏"`。
- **分词级世界观提取**——`WorldBuilder` 按连接词 / 标点预分词后整词匹配、长后缀优先：`"青云宗与魔道势力在苍云大陆" → 势力 ["青云宗","魔道势力"]、地理 ["苍云大陆"]`，连接词不再被吞入。
- **修文全量替换**——`AutomaticRepairEngine` 一次性替换全部生硬转折词（`突然 / 莫名 / 鬼使神差 …`），并合并相邻重复的过渡短语。
- **引擎隔离检测**——两引擎均内置 `_ENGINE_FINGERPRINT` 与 `check_engine_isolation()`：同一进程混用时立即警告，杜绝同名异构数据类（`CausalNode` / `ResponsibilityAccount` 等）互相覆盖导致的数据错乱与崩溃。

</div>

<p align="center">— ✦ —</p>

## ✦ Usage

<div style="max-width:880px;margin:0 auto;padding:0 16px">

```python
import importlib.util

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

biz = load("biz", "engine for business.py")
print([s.name for s in biz.SPLStage])   # STRIP_NARRATIVE … LOCK_RESPONSIBILITY

# Engine isolation detection: clear warning when both engines are mixed
# (both engines register a fingerprint in sys.modules; any load path is detectable)
# 引擎隔离检测：混用两引擎时给出明确警告
# （两引擎均已向 sys.modules 注册指纹，任何加载方式都能被检测到）
for conflict in biz.check_engine_isolation():
    print(f"⚠️ {conflict}")
```

Or run the built-in engines directly:

```bash
python "Story Engine for Creator.py"
python "engine for business.py"
python -m compliance_engine audit --type contract --input 合同.txt --output 报告.html
python -m compliance_engine list-rules --type regulation
python -m compliance_engine demo
```

</div>

<p align="center">— ✦ —</p>

## ✦ Project Structure

```
STORY-ENGINE/
├── Story Engine for Creator.py    # creator-facing narrative cognitive audit engine
├── engine for business.py         # SPL four-stage editorial + contract-review pipeline
├── compliance_engine/             # enterprise document compliance audit engine (offline, zero-dep)
│   ├── engine.py / models.py / auditors.py / rules.py / report.py
│   ├── cli.py                     # audit / list-rules / demo
│   ├── rules/                     # contract.json / regulation.json / official_doc.json / common.json
│   └── demo.py
├── assets/                        # banner.svg/png, overview.svg/png
└── LICENSE
```

<p align="center">— ✦ —</p>

## ✦ Ecosystem

STORY-ENGINE is a member of the NOHN AI ecosystem — a family of projects built around second-perspective causal auditing and deterministic execution:

| Project | Repo | Positioning |
|---|---|---|
| **Second-Perspective (GCAE)** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective) | Global cognitive audit engine — five-operator causal audit core (IMDA 95/100) |
| **NOMOS** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective) (`Intelligent-Decision-Hub--Nomos` branch) | Auditable deterministic decision hub (IMDA 95/100) |
| **SPL-G1** | [nohn3043-arch/SPL-G1](https://github.com/nohn3043-arch/SPL-G1) | Hardware causal-audit trusted computing unit (TCU) |
| **SPL-Virtual-World-Base** | [nohn3043-arch/Second-Reality](https://github.com/nohn3043-arch/Second-Reality) | Virtual-world & metaverse infrastructure (constitution / law / bridge) |
| **Story-Engine** | [nohn3043-arch/story-engine](https://github.com/nohn3043-arch/story-engine) | 故事引擎（创作者/大众）+ 文书审查引擎（企业） |
| **Antares** | [nohn3043-arch/Antares](https://github.com/nohn3043-arch/Antares) | GFSIP v1.0 — causally-audited federated stable interoperability protocol |
| **Anthropomorphic-Agent-Engine** | [nohn3043-arch/Anthropomorphic-Agent-Engine](https://github.com/nohn3043-arch/Anthropomorphic-Agent-Engine) | Deterministic anthropomorphic psychology engine (SPL Pure Core V8.0) |
| **PAGES** | [nohn3043-arch/pages](https://github.com/nohn3043-arch/pages) | NOHN AI ecosystem official landing page |

<p align="center">— ✦ —</p>

## ✦ License & Authorization

This repository is **not open source** and adopts a dual-track model: free for personal non-commercial research; government / enterprises require a paid commercial license. See [LICENSE](./LICENSE).

| User | Purpose | License requirement |
|---|---|---|
| Individual (natural person) | Non-commercial academic research / study / personal experiments | **Free** under [LICENSE](./LICENSE) "Personal Free Research License" |
| Government agency / public institution / enterprise | Any purpose (incl. internal deployment, product development, service provision) | **Paid commercial license required in advance** |

- **Individual researchers** may use it free for non-commercial research, but not for any commercial purpose, nor may they provide services to any enterprise or government agency.
- **Government / enterprise users** may not copy, deploy, run, integrate, or distribute this work before signing a commercial license agreement and paying the agreed fee.
- **Apply for license**: International / Global — [ai@nohnlins.com](mailto:ai@nohnlins.com) · China — [lin@secondai.top](mailto:lin@secondai.top)

The licensor, applicable law, and dispute resolution follow [LICENSE](./LICENSE) based on the user's location: users within China → Shanghai Linming Junhua Technology Co., Ltd. (PRC law); users outside China → NOHN AI TECHNOLOGY PTE. LTD. (Singapore law, SIAC arbitration).

<p align="center">
  <a href="https://github.com/nohn3043-arch">GitHub</a>
  &nbsp;·&nbsp;
  <a href="https://www.nohnlins.com/">nohnlins.com</a>
  &nbsp;·&nbsp;
  <a href="mailto:ai@nohnlins.com">ai@nohnlins.com</a>
</p>
<p align="center"><sub>NOHN AI · STORY-ENGINE</sub></p>
