<p align="center">
  <img src="assets/banner.png" alt="STORY-ENGINE 横幅" style="width:100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/nlp-D4AF37?style=flat-square" alt="nlp">
  <img src="https://img.shields.io/badge/consistency-D4AF37?style=flat-square" alt="consistency">
  <img src="https://img.shields.io/badge/long--form-D4AF37?style=flat-square" alt="long-form">
  <img src="https://img.shields.io/badge/second--perspective-D4AF37?style=flat-square" alt="second-perspective">
</p>

<p align="center">
[English](README.md) | 简体中文
</p>

<blockquote align="center">
  <em>长篇叙事一致性引擎</em>
</blockquote>

<div style="max-width:880px;margin:0 auto;padding:0 16px">

## ✦ 关于

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">STORY-ENGINE 包含两个定位清晰的产品：</p>

<ul style="font-size:15px;line-height:1.8;color:#2C2C2C">
  <li><strong>Story Engine（面向创作者与大众）</strong> —— 长篇小说一致性引擎，自动审计角色设定、因果时间线与记忆线，让百万字作品在人物、剧情、世界观上保持一致；同时提供 SPL 四阶段叙事编辑流水线。它将编辑的直觉式验证转化为可复用的结构化流程。</li>
  <li><strong>Document Review Engine（面向企业）</strong> —— 零依赖、可离线运行的企业级文档合规审查引擎，对合同、规章、公文与通用文本进行条款级规则扫描与文档级审计（要素完整性 / 一致性 / 权责对等 / 格式），输出可追溯的审查报告。</li>
</ul>

<p align="center">
  <img src="assets/overview.png" alt="STORY-ENGINE 总览" style="width:100%">
</p>

</div>

<p align="center">— ✦ —</p>

## ✦ 设计方向

<div style="max-width:880px;margin:0 auto;padding:0 16px">

STORY-ENGINE 由两个独立产品组成，各自面向不同用户群体：

| 产品 | 目标用户 | 模块 | 典型输入 |
|------|----------|------|----------|
| **Story Engine** | 创作者 / 大众 | `Story Engine for Creator.py` + `engine for business.py` | 角色 / 因果时间线 / 世界观 / 叙事元素 |
| **Document Review Engine** | 企业 | `compliance_engine/` | 合同 / 规章 / 公文 / 通用文本 |

两个产品共享同一套 **确定性审计设计语言** —— 责任闭环锚定（`ResponsibilityAccount`）、风险分级与全链路可追溯日志。Document Review Engine 是相对独立的离线规则模块，**不依赖 LLM** —— 纯规则库、零第三方依赖、可离线运行，专用于企业文档合规场景。

</div>

<p align="center">— ✦ —</p>

## ✦ 快速开始

```bash
# 主仓库：GitHub
git clone https://github.com/nohn3043-arch/story-engine.git
# 镜像：Gitee
# git clone https://gitee.com/sjiun/Story-engine.git
cd Story-engine
# 纯 Python >=3.8。引擎文件有意使用带空格的文件名。
python "Story Engine for Creator.py"      # 面向创作者的第二视角认知审计引擎
# 或：python "engine for business.py"      # SPL 四阶段编辑流水线
```

<p align="center">— ✦ —</p>

## ✦ 功能特性

<div style="max-width:880px;margin:0 auto;padding:0 16px">

### Story Engine（面向创作者与大众）

一个长篇小说一致性引擎，将编辑的直觉式验证转化为可复用的结构化流程。分两层：

- **创作者引擎**（`Story Engine for Creator.py`）—— 面向叙事的认知审计层：
  - `ResponsibilityAccount` —— 每一项检查都锚定到命名责任节点（谁 / 角色 / 阶段）。
  - `CognitiveAuditEngine` + 可插拔 `AuditPlugin` + `EmotionalConstraint` —— 可组合的审计维度。
  - `CausalNode` 携带 `implicit_assumptions` 与 `vulnerability_score` —— 追踪「因为 → 所以」逻辑并量化脆弱性。
  - `NarrativeStripper` / `ImplicitAssumptionDetector` / `VulnerabilityAssessor` —— 第二视角算子流水线。
  - `AutomaticRepairEngine`（全量跳词修复）/ `UltimateCausalNovelEngine` / `SecondPerspectiveCausalEngine` / `WorldBuilder`（token 级世界观抽取）—— 修复、全书审计与世界观构建层。
- **商业引擎**（`engine for business.py`）—— SPL 四阶段原生推理流水线：
  1. `STRIP_NARRATIVE` —— 识别叙事元素（伏笔 / 转折 / 高潮 / 铺垫）。
  2. `SCAN_ASSUMPTION` —— `ImplicitAssumptionScanner` 验证动机与剧情逻辑。
  3. `HEDGE_RISK` —— `VulnerabilityHedge` 标记 OOC、逻辑漏洞与节奏问题；`CausalIntersectionBroker` 合并世界线。
  4. `LOCK_RESPONSIBILITY` —— 输出带可追溯优化项的质量分数。
  - 风险等级：`SAFE` / `WARNING` / `CRITICAL` / `FATAL`；节点状态：`RAW` / `STRIPPED` / `AUDITED` / `PRUNED` / `ACTIVE`。
  - `SPLStoryGenerationEngine` + `StylisticScribe` 驱动生成；`DeepSeekProvider` / `MockLLM` 为可替换 LLM 后端。

### Document Review Engine（面向企业）

企业级文档合规审查引擎（`compliance_engine/`），零依赖、可离线运行：

- 支持四种文档类型（合同 / 规章 / 公文 / 通用文本）的条款级规则扫描 + 文档级审计（要素完整性 / 一致性 / 权责对等 / 格式）。
- `ComplianceEngine` 编排：分节 → 规则扫描 → 文档级审计 → 责任闭环 → 评分 → 报告。
- `ResponsibilityAccount` 责任闭环锚定 + `TraceLog` 全链路可追溯；判定为确定性（命中 = 裁决），不输出概率。
- `RuleEngine` 加载纯 JSON 规则库（可通过 `--rules-dir` 外部扩展）；四个 `Auditor` 类补充条款级命中。
- 报告支持三种格式：HTML（可视化）/ JSON（结构化）/ Markdown（归档）；完整 CLI：`audit` / `list-rules` / `demo`。

两个产品共享同一套确定性审计设计语言（责任闭环锚定、风险分级、全链路可追溯），但分别面向创作文本与企业文档场景。

**鲁棒性加固（2026-08 修复）**：
- **角色名合理性过滤** —— `_extract_plausible_name` 排除代词 / 动词短语 / 天气景物词，宁缺毋滥：`"坚持己见" → ""`、`"他说：我们走吧" → ""`、`"林夏在评审会上坚持自研方案" → "林夏"`。
- **Token 级世界观抽取** —— `WorldBuilder` 先按连接词 / 标点预分词，再以最长后缀优先匹配整词：`"青云宗与魔道势力在苍云大陆" → factions ["青云宗","魔道势力"], geography ["苍云大陆"]`，连接词不再被吞掉。
- **全文修订替换** —— `AutomaticRepairEngine` 一次性替换所有生硬过渡词（`突然 / 莫名 / 鬼使神差 …`），并合并相邻重复过渡短语。
- **引擎隔离检测** —— 两个引擎均嵌入 `_ENGINE_FINGERPRINT` 与 `check_engine_isolation()`：同一进程混用立即告警，防止同名但异构的数据类（`CausalNode` / `ResponsibilityAccount` 等）互相覆盖导致数据损坏与崩溃。

</div>

<p align="center">— ✦ —</p>

## ✦ 使用方法

<div style="max-width:880px;margin:0 auto;padding:0 16px">

```python
import importlib.util

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

biz = load("biz", "engine for business.py")
print([s.name for s in biz.SPLStage])   # STRIP_NARRATIVE … LOCK_RESPONSIBILITY

# 引擎隔离检测：混用两个引擎时清晰告警
#（两个引擎都在 sys.modules 中注册指纹；无论哪种加载路径都能检测到）
for conflict in biz.check_engine_isolation():
    print(f"⚠️ {conflict}")
```

或直接运行内置引擎：

```bash
python "Story Engine for Creator.py"
python "engine for business.py"
python -m compliance_engine audit --type contract --input contract.txt --output report.html
python -m compliance_engine list-rules --type regulation
python -m compliance_engine demo
```

</div>

<p align="center">— ✦ —</p>

## ✦ 项目结构

```
STORY-ENGINE/
├── Story Engine for Creator.py    # 面向创作者的叙事认知审计引擎
├── engine for business.py         # SPL 四阶段编辑 + 合同审查流水线
├── compliance_engine/             # 企业文档合规审查引擎（离线，零依赖）
│   ├── engine.py / models.py / auditors.py / rules.py / report.py
│   ├── cli.py                     # audit / list-rules / demo
│   ├── rules/                     # contract.json / regulation.json / official_doc.json / common.json
│   └── demo.py
├── assets/                        # banner.svg/png, overview.svg/png
└── LICENSE
```

<p align="center">— ✦ —</p>

## ✦ 生态

STORY-ENGINE 是 NOHN AI 生态的一员 —— 围绕第二视角因果审计与确定性执行构建的项目家族：

| 项目 | 仓库 | 定位 |
|---|---|---|
| **Second-Perspective (GCAE)** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective) | 全球认知审计引擎 —— 五算子因果审计核心（IMDA 95/100） |
| **NOMOS** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective)（`Intelligent-Decision-Hub--Nomos` 分支） | 可审计确定性决策中心（IMDA 95/100） |
| **SPL-G1** | [nohn3043-arch/SPL-G1](https://github.com/nohn3043-arch/SPL-G1) | 硬件因果审计可信计算单元（TCU） |
| **SPL-Virtual-World-Base** | [nohn3043-arch/Second-Reality](https://github.com/nohn3043-arch/Second-Reality) | 虚拟世界与元宇宙基础设施（宪法 / 法律 / 桥梁） |
| **Story-Engine** | [nohn3043-arch/story-engine](https://github.com/nohn3043-arch/story-engine) | Story Engine（创作者/大众） + Document Review Engine（企业） |
| **Antares** | [nohn3043-arch/Antares](https://github.com/nohn3043-arch/Antares) | GFSIP v1.0 —— 带因果审计的联邦稳定互操作协议 |
| **Anthropomorphic-Agent-Engine** | [nohn3043-arch/Anthropomorphic-Agent-Engine](https://github.com/nohn3043-arch/Anthropomorphic-Agent-Engine) | 确定性拟人心理学引擎（SPL Pure Core V8.0） |
| **PAGES** | [nohn3043-arch/pages](https://github.com/nohn3043-arch/pages) | NOHN AI 生态官方落地页 |

<p align="center">— ✦ —</p>

## ✦ 许可与授权

本仓库 **不是开源软件**，采用双轨模式：个人非商业研究免费；政府 / 企业使用需事先取得付费商业许可。参见 [LICENSE](./LICENSE)。

| 用户 | 用途 | 许可要求 |
|---|---|---|
| 个人（自然人） | 非商业学术研究 / 学习 / 个人实验 | **免费**，依据 [LICENSE](./LICENSE) 中「个人免费研究许可」 |
| 政府机构 / 事业单位 / 企业 | 任何用途（含内部部署、产品开发、服务提供） | **必须事先取得付费商业许可** |

- **个人研究者** 可免费用于非商业研究，但不得用于任何商业目的，也不得向任何企业或政府机构提供服务。
- **政府 / 企业用户** 在签署商业许可协议并支付约定费用前，不得复制、部署、运行、集成或分发本作品。
- **许可申请**：国际 / 全球 — [ai@nohnlins.com](mailto:ai@nohnlins.com) · 中国 — [lin@secondai.top](mailto:lin@secondai.top)

许可方、适用法律与争议解决依用户所在地按 [LICENSE](./LICENSE) 执行：中国境内用户 → 上海林明钧华科技有限公司（适用中国法律）；中国境外用户 → NOHN AI TECHNOLOGY PTE. LTD.（适用新加坡法律，SIAC 仲裁）。

<p align="center">
  <a href="https://github.com/nohn3043-arch">GitHub</a>
  &nbsp;·&nbsp;
  <a href="https://www.nohnlins.com/">nohnlins.com</a>
  &nbsp;·&nbsp;
  <a href="mailto:ai@nohnlins.com">ai@nohnlins.com</a>
</p>
<p align="center"><sub>NOHN AI · STORY-ENGINE</sub></p>
