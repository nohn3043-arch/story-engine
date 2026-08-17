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

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">STORY-ENGINE is a narrative consistency checking engine for long-form fiction, performing automated audits on character settings, causal timelines, and memory threads to ensure million-word works remain coherent across characters, plots, and worldbuilding. It transforms an editor's intuitive checks into a reusable, structured pipeline.</p>

<p align="center">
  <img src="assets/overview.png" alt="STORY-ENGINE overview" style="width:100%">
</p>

</div>

<p align="center">— ✦ —</p>

## ✦ Quick Start

```bash
# Primary: GitHub
git clone https://github.com/nohn3043-arch/story-engine.git
# Mirror: Gitee
# git clone https://gitee.com/sjiun/Story-engine.git
cd Story-engine
# Pure Python ≥3.8. Engine files use spaces in their names by design.
python "Story Engine for Creator.py"      # creator-facing cognitive audit engine
# or: python "engine for business.py"     # SPL four-stage editorial pipeline
```

<p align="center">— ✦ —</p>

## ✦ What It Does

<div style="max-width:880px;margin:0 auto;padding:0 16px">

STORY-ENGINE audits long-form fiction for narrative consistency, turning an editor's intuition into a reusable, structured pipeline. It works in two layers:

- **Creator engine** (`Story Engine for Creator.py`) — a cognitive-audit layer for storytelling:
  - `ResponsibilityAccount` — every check is anchored to a named accountable node (who / role / stage).
  - `CognitiveAuditEngine` + pluggable `AuditPlugin`s + `EmotionalConstraint` — composable audit dimensions.
  - `CausalNode` with `implicit_assumptions` and a `vulnerability_score` — traces *because → so* logic and grades fragility.
  - `NarrativeStripper` / `ImplicitAssumptionDetector` / `VulnerabilityAssessor` — the second-perspective operator pipeline.
  - `AutomaticRepairEngine` / `UltimateCausalNovelEngine` / `SecondPerspectiveCausalEngine` / `WorldBuilder` — repair, full-novel audit and world-construction layers.
- **Business engine** (`engine for business.py`) — the SPL four-stage native reasoning pipeline:
  1. `STRIP_NARRATIVE` — identify story elements (foreshadow / turn / climax / setup).
  2. `SCAN_ASSUMPTION` — `ImplicitAssumptionScanner` verifies character motive & plot-logic soundness.
  3. `HEDGE_RISK` — `VulnerabilityHedge` flags OOC, logic holes, pacing problems; `CausalIntersectionBroker` merges world-lines.
  4. `LOCK_RESPONSIBILITY` — emit a quality score with traceable optimizations.
  - Risk levels: `SAFE` / `WARNING` / `CRITICAL` / `FATAL`; node states: `RAW` / `STRIPPED` / `AUDITED` / `PRUNED` / `ACTIVE`.
  - `SPLStoryGenerationEngine` + `StylisticScribe` drive generation; `DeepSeekProvider` / `MockLLM` are the swappable LLM backends.

Both layers share the same cognitive-audit core as the Second-Perspective engine — this is the audit discipline applied to narrative, rather than to decision-making.

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
```

Or run the bundled engines directly:

```bash
python "Story Engine for Creator.py"
python "engine for business.py"
```

</div>

<p align="center">— ✦ —</p>

## ✦ Project Structure

```
STORY-ENGINE/
├── Story Engine for Creator.py    # creator-facing cognitive audit engine
├── engine for business.py         # SPL four-stage editorial reasoning pipeline
├── assets/                        # banner.svg/png, overview.svg/png
└── LICENSE
```

<p align="center">— ✦ —</p>

## ✦ Ecosystem

STORY-ENGINE is one member of the NOHN AI ecosystem — a family of projects built around second-perspective causal audit and deterministic execution:

| Project | Repository | What it is |
|---|---|---|
| **Second-Perspective (GCAE)** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective) | Global cognitive audit engine — the five-operator causal audit core (IMDA 95/100) |
| **NOMOS** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective) (`Intelligent-Decision-Hub--Nomos` branch) | Auditable deterministic decision hub (IMDA 95/100) |
| **SPL-G1** | [nohn3043-arch/SPL-G1-General-purpose-processor](https://github.com/nohn3043-arch/SPL-G1-General-purpose-processor) | Hardware causal-audit Trusted Compute Unit (TCU) |
| **SPL-Virtual-World-Base** | [nohn3043-arch/Second-Reality](https://github.com/nohn3043-arch/Second-Reality) | Virtual-world & metaverse infrastructure (Constitution / Law / Bridge) |
| **Story-Engine** | [nohn3043-arch/story-engine](https://github.com/nohn3043-arch/story-engine) | Long-form narrative consistency engine |
| **Antares** | [nohn3043-arch/Antares](https://github.com/nohn3043-arch/Antares) | GFSIP v1.0 — federated stable interoperability protocol with causal audit |
| **Anthropomorphic-Agent-Engine** | [nohn3043-arch/Anthropomorphic-Agent-Engine](https://github.com/nohn3043-arch/Anthropomorphic-Agent-Engine) | Deterministic anthropomorphic psychology engine (SPL Pure Core V8.0) |
| **PAGES** | [nohn3043-arch/pages](https://github.com/nohn3043-arch/pages) | Official NOHN AI ecosystem landing page |

<p align="center">— ✦ —</p>

## ✦ License & Authorization

This repository is **not open-source**. It uses a dual-track model: free for individual non-commercial research; paid commercial authorization required for government / enterprise. See [LICENSE](./LICENSE).

| User | Purpose | License Requirement |
|------|---------|---------------------|
| Individual (natural person) | Non-commercial academic research / study / personal experimentation | **Free** under the "Free Individual Research License" in [LICENSE](./LICENSE) |
| Government agency / public institution / enterprise | Any purpose (incl. internal deployment, product development, service provision) | **Requires prior written paid authorization** |

- **Individual researchers** may use the Work free of charge for non-commercial research under [LICENSE](./LICENSE), but not for any commercial purpose, nor to provide services to any enterprise or government organization.
- **Government / enterprise users** may not copy, deploy, run, integrate, or distribute the Work before signing a Commercial Authorization Agreement and paying the agreed fee.
- **Apply for authorization**:
  - International / Global: [ai@nohnlins.com](mailto:ai@nohnlins.com)
  - China: [lin@secondai.top](mailto:lin@secondai.top)

The licensor, governing law, and dispute resolution are determined by the user's location as set out in [LICENSE](./LICENSE): users within the PRC → Shanghai Linming Junhua Technology Co., Ltd. (laws of the PRC); users outside the PRC → NOHN AI TECHNOLOGY PTE. LTD. (laws of Singapore, SIAC arbitration).

<p align="center">
  <a href="https://github.com/nohn3043-arch">GitHub</a>
  &nbsp;·&nbsp;
  <a href="https://www.nohnlins.com/">nohnlins.com</a>
  &nbsp;·&nbsp;
  <a href="mailto:ai@nohnlins.com">ai@nohnlins.com</a>
</p>
<p align="center"><sub>NOHN AI · STORY-ENGINE</sub></p>
