<p align="center">
  <img src="https://sourceforge.net/p/story-engine/git/ci/main/tree/assets/banner.png?format=raw" alt="STORY-ENGINE banner" style="width:100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/nlp--D4AF37?style=flat-square" alt="nlp">  <img src="https://img.shields.io/badge/consistency--D4AF37?style=flat-square" alt="consistency">  <img src="https://img.shields.io/badge/long-form-D4AF37?style=flat-square" alt="long-form">
</p>

<blockquote align="center">
  <em>Long-Form Narrative Consistency Engine</em>
</blockquote>

<div style="max-width:880px;margin:0 auto;padding:0 16px">

## ✦ About

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">STORY-ENGINE is a narrative consistency checking engine for long-form fiction, performing automated audits on character settings, causal timelines, and memory threads to ensure million-word works remain coherent across characters, plots, and worldbuilding. It transforms an editor's intuitive checks into a reusable, structured pipeline.</p>

<p align="center">
  <img src="https://sourceforge.net/p/story-engine/git/ci/main/tree/assets/overview.png?format=raw" alt="STORY-ENGINE overview" style="width:100%">
</p>

</div>

<p align="center">— ✦ —</p>

## ✦ Quick Start

```bash
git clone https://github.com/NOHN-AI/Story-engine.git
# Gitee mirror (enterprise): https://e.gitee.com/nohn-ecosystem/story-engine.git
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
  - `CognitiveAuditEngine` + pluggable `AuditPlugin`s — composable audit dimensions.
  - `CausalNode` with implicit assumptions and a `vulnerability_score` — traces *because → so* logic and grades fragility.
- **Business engine** (`engine for business.py`) — the SPL four-stage native reasoning pipeline:
  1. `STRIP_NARRATIVE` — identify story elements (foreshadow / turn / climax / setup).
  2. `SCAN_ASSUMPTION` — verify character motive & plot-logic soundness.
  3. `HEDGE_RISK` — flag OOC, logic holes, pacing problems.
  4. `LOCK_RESPONSIBILITY` — emit a quality score with traceable optimizations.
  - Risk levels: `SAFE` / `WARNING` / `CRITICAL` / `FATAL`; node states: `RAW` / `STRIPPED` / `AUDITED` / `PRUNED` / `ACTIVE`.

</div>

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

## ✦ Project Structure

```
STORY-ENGINE/
├── Story Engine for Creator.py    # creator-facing cognitive audit engine
├── engine for business.py         # SPL four-stage editorial reasoning pipeline
├── assets/                        # banner.png, overview.png
└── LICENSE
```

## ✦ License & Authorization

This repository is **not open-source**. It uses a dual-track model: free for individual non-commercial research, paid commercial authorization required for government / enterprise. See [LICENSE](./LICENSE).

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
  <a href="https://github.com/NOHN-AI">NOHN-AI</a>
  &nbsp;·&nbsp;
  <a href="https://www.nohnlins.com/">nohnlins.com</a>
  &nbsp;·&nbsp;
  <a href="mailto:ai@nohnlins.com">ai@nohnlins.com</a>
</p>
<p align="center"><sub>NOHN AI · STORY-ENGINE</sub></p>
