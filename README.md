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

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">STORY-ENGINE consists of two clearly-positioned products:</p>

<ul style="font-size:15px;line-height:1.8;color:#2C2C2C">
  <li><strong>Story Engine (for creators and the general public)</strong> — a long-form novel consistency engine that automatically audits character settings, causal timelines, and memory lines, keeping million-word works consistent in characters, plot, and worldview; it also provides the SPL four-stage narrative editing pipeline. It transforms an editor's intuitive verification into a reusable structured process.</li>
  <li><strong>Document Review Engine (for enterprises)</strong> — a zero-dependency, offline-capable enterprise-grade document compliance review engine that performs clause-level rule scanning and document-level auditing (element completeness / consistency / rights-obligation parity / formatting) on contracts, regulations, official documents, and general text, and outputs traceable review reports.</li>
</ul>

<p align="center">
  <img src="assets/overview.png" alt="STORY-ENGINE overview" style="width:100%">
</p>

</div>

<p align="center">— ✦ —</p>

## ✦ Design Direction

<div style="max-width:880px;margin:0 auto;padding:0 16px">

STORY-ENGINE consists of two independent products, each targeting a different user group:

| Product | Target Users | Module | Typical Input |
|------|----------|------|----------|
| **Story Engine** | Creators / general public | `Story Engine for Creator.py` + `engine for business.py` | Characters / causal timeline / worldview / narrative elements |
| **Document Review Engine** | Enterprises | `compliance_engine/` | Contracts / regulations / official documents / general text |

Both products share the same **deterministic audit design language** — responsibility-loop anchoring (`ResponsibilityAccount`), risk grading, and full-chain traceable logs. The Document Review Engine is a relatively independent offline rule module that **does not depend on LLMs** — pure rule base, zero third-party dependencies, runs offline, dedicated to enterprise document compliance scenarios.

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

STORY-ENGINE consists of two products, each serving a different user group:

### Story Engine (for creators and the general public)

A long-form novel consistency engine that transforms an editor's intuitive verification into a reusable structured process. It has two layers:

- **Creator Engine** (`Story Engine for Creator.py`) — the narrative-facing cognitive audit layer:
  - `ResponsibilityAccount` — every check is anchored to a named responsibility node (who / role / stage).
  - `CognitiveAuditEngine` + pluggable `AuditPlugin` + `EmotionalConstraint` — composable audit dimensions.
  - `CausalNode` carries `implicit_assumptions` and `vulnerability_score` — tracks *because → therefore* logic and quantifies fragility.
  - `NarrativeStripper` / `ImplicitAssumptionDetector` / `VulnerabilityAssessor` — the second-perspective operator pipeline.
  - `AutomaticRepairEngine` (full jump-word repair) / `UltimateCausalNovelEngine` / `SecondPerspectiveCausalEngine` / `WorldBuilder` (token-level worldview extraction) — the repair, whole-book audit, and worldview construction layer.
- **Business Engine** (`engine for business.py`) — the SPL four-stage native reasoning pipeline:
  1. `STRIP_NARRATIVE` — identify narrative elements (foreshadowing / twist / climax / setup).
  2. `SCAN_ASSUMPTION` — `ImplicitAssumptionScanner` verifies motivation and plot logic.
  3. `HEDGE_RISK` — `VulnerabilityHedge` flags OOC, logic holes, and pacing issues; `CausalIntersectionBroker` merges worldlines.
  4. `LOCK_RESPONSIBILITY` — output a quality score with traceable optimizations.
  - Risk levels: `SAFE` / `WARNING` / `CRITICAL` / `FATAL`; node states: `RAW` / `STRIPPED` / `AUDITED` / `PRUNED` / `ACTIVE`.
  - `SPLStoryGenerationEngine` + `StylisticScribe` drive generation; `DeepSeekProvider` / `MockLLM` are replaceable LLM backends.

### Document Review Engine (for enterprises)

An enterprise-grade document compliance review engine (`compliance_engine/`), zero-dependency and runs offline:

- Supports clause-level rule scanning + document-level auditing (element completeness / consistency / rights-obligation parity / formatting) for four document types: contracts / regulations / official documents / general text.
- `ComplianceEngine` orchestration: sectioning → rule scanning → document-level audit → responsibility loop → scoring → report.
- `ResponsibilityAccount` responsibility-loop anchoring + `TraceLog` full-chain traceability; judgments are deterministic (hit = verdict), no probability output.
- `RuleEngine` loads a pure JSON rule base (externally extensible via `--rules-dir`); four `Auditor` classes complement clause-level hits.
- Reports support three formats: HTML (visualization) / JSON (structured) / Markdown (archiving); full CLI: `audit` / `list-rules` / `demo`.

Both products share the same deterministic audit design language (responsibility-loop anchoring, risk grading, full-chain traceability), but target creative narrative and enterprise document scenarios respectively.

**Robustness hardening (2026-08 fixes)**:
- **Character-name plausibility filter** — `_extract_plausible_name` excludes pronouns / verb phrases / weather-scene words, preferring absence over noise: `"坚持己见" → ""`, `"他说：我们走吧" → ""`, `"林夏在评审会上坚持自研方案" → "林夏"`.
- **Token-level worldbuilding extraction** — `WorldBuilder` pre-tokenizes on connectives / punctuation, then matches whole words with longest-suffix priority: `"青云宗与魔道势力在苍云大陆" → factions ["青云宗","魔道势力"], geography ["苍云大陆"]`, connectives are no longer swallowed.
- **Full-text revision replacement** — `AutomaticRepairEngine` replaces all stiff transition words at once (`突然 / 莫名 / 鬼使神差 …`) and merges adjacent duplicate transition phrases.
- **Engine isolation detection** — both engines embed `_ENGINE_FINGERPRINT` and `check_engine_isolation()`: mixing both in one process warns immediately, preventing data corruption and crashes caused by homonymous but heterogeneous data classes (`CausalNode` / `ResponsibilityAccount`, etc.) overwriting each other.

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
for conflict in biz.check_engine_isolation():
    print(f"⚠️ {conflict}")
```

Or run the built-in engines directly:

```bash
python "Story Engine for Creator.py"
python "engine for business.py"
python -m compliance_engine audit --type contract --input contract.txt --output report.html
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
| **Story-Engine** | [nohn3043-arch/story-engine](https://github.com/nohn3043-arch/story-engine) | Story Engine (creators/public) + Document Review Engine (enterprise) |
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
