<p align="center">
  <em>No plot holes. No character drift. Every thread is tied.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/engine-causal_chain-D4AF37?style=flat-square" alt="causal">
  <img src="https://img.shields.io/badge/python-3.9+-2C2C2C?style=flat-square" alt="python">
  <img src="https://img.shields.io/badge/genre-agnostic-2C2C2C?style=flat-square" alt="genre">
</p>

---

&nbsp;

## ✦ Story Engine

A logic-consistent story-generation engine that helps long-form writers maintain narrative integrity — from the first chapter to the last.

&nbsp;

## ✦ Consistency Pipeline

```mermaid
flowchart LR
    SEED(("Seed<br/>Prompt")):::input --> CH(("Chapter<br/>Outline")):::gen
    CH --> CC(("Character<br/>Consistency")):::check
    CH --> CL(("Causal<br/>Logic")):::check
    CH --> EM(("Event<br/>Memory")):::check

    CC --> |"pass"| OUT(("Coherent<br/>Output")):::output
    CL --> |"pass"| OUT
    EM --> |"pass"| OUT

    CC --> |"fail"| FIX(("Flag &amp;<br/>Suggest")):::alert
    CL --> |"fail"| FIX
    EM --> |"fail"| FIX
    FIX --> CH

    classDef input fill:#FAFAFA,stroke:#D4AF37,stroke-width:2px,color:#2C2C2C
    classDef gen fill:#F5F0E6,stroke:#C9A96E,stroke-width:1px,color:#2C2C2C
    classDef check fill:#FAFAFA,stroke:#B8B8B8,stroke-width:1px,color:#2C2C2C
    classDef output fill:#FAFAFA,stroke:#D4AF37,stroke-width:1px,color:#2C2C2C
    classDef alert fill:#FAFAFA,stroke:#E0E0E0,stroke-width:0.5px,color:#8B8B8B
```

&nbsp;

## ✦ Three Core Guarantees

| Guarantee | Mechanism |
|-----------|-----------|
| **Character Consistency** | Personality vectors remain stable across chapters |
| **Causal Logic** | Every plot point has a "because → therefore" chain |
| **Event Memory** | All foreshadowing is tracked and echoed in later chapters |

&nbsp;

## ✦ Quick Start

```bash
python story_engine.py --seed "A young woman discovers her best friend has been lying to her for years."
```

The engine generates chapter-by-chapter outlines, checks causal logic, and outputs a self-consistent story. **No technical background needed** — the engine handles logic checks automatically.

&nbsp;

## ✦ Example

**Input:**
> *Elena, a detective, finds a torn photo in her missing partner's drawer.*

**Output (excerpt):**
> *Elena stares at the photo. It was taken two days before he vanished. Her hand shakes — not from fear, but from the realization that the person in the background is her own boss.*

The engine ensures all subsequent chapters remember: the photo, the boss's role, Elena's emotional state, and every planted clue.

&nbsp;

## ✦ For Whom

> Novelists · Screenwriters · Game Narrative Designers · Anyone writing long-form stories

&nbsp;

---

<p align="center">
  <a href="mailto:ai@nohnlins.com">ai@nohnlins.com</a>
</p>
<p align="center">
  <sub>© 2026 Shanghai Linming Junhua &amp; NOHN AI Technology · All Rights Reserved</sub>
</p>
