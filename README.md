

# Story Engine

> A writing tool that keeps your story consistent from beginning to end – no more plot holes or characters acting out of character.

## What does it do?

You give it a starting idea. It helps you write a full story where:
- Characters stay true to themselves (no sudden personality changes)
- The plot flows logically (no "wait, how did we get here?" moments)
- Past events are remembered (foreshadowing doesn't get lost)

## Who is it for?

- Writers who struggle with long-form consistency
- Screenwriters who need to track plot threads
- Game developers who build narrative-driven worlds
- Anyone who wants to tell a story without breaking its own rules

## Architecture Overview

### Core Engines

**UltimateCausalNovelEngine** - Main story generation engine that:
- Plans and generates chapter-by-chapter outlines
- Manages global story state
- Renders chapters with emotional and logical consistency
- Automatically registers characters and tracks their development

**SPLStoryGenerationEngine** - Structured story generation engine that:
- Processes chapters with tension control
- Manages emotional contagion across narrative
- Compiles complete novels from chapter graphs

**CognitiveAuditEngine** - Quality assurance system that:
- Audits phase space safety for characters
- Checks story quality against logical rules
- Validates narrative consistency

### Key Components

**Narrative Elements:**
- `CausalNode` - Individual story beats with cause-effect relationships
- `CausalLine` - Chains of cause-effect events
- `Chapter` - Story divisions with titles and content
- `GlobalState` - Persistent story world state

**Character Management:**
- `CharacterPhaseSpace` - Tracks character personality boundaries
- `ImplicitAssumption` - Detections of unstated character traits
- `EmotionalConstraint` - Emotional consistency rules

**Audit System:**
- `ImplicitAssumptionDetector` - Finds hidden assumptions in story logic
- `VulnerabilityAssessor` - Evaluates plot weaknesses
- `AutomaticRepairEngine` - Suggests fixes for logical gaps

**LLM Integration:**
- `MockLLM` - Testing provider
- `DeepSeekProvider` - Production LLM integration
- `StylisticSque` - Narrative rendering with style profiles

## How to use it

### Installation

```bash
git clone https://gitee.com/nohn-ecosystem/story-engine.git
cd story-engine
```

### Dependencies

- Python 3.9+
- Dependencies as specified in requirements.txt

### Basic Usage

```python
from story_engine import UltimateCausalNovelEngine, GlobalState

# Initialize engine with story concept
engine = UltimateCausalNovelEngine(
    novel_title="Mystery at Dawn",
    initial_global_state=GlobalState(...),
    output_language="en"
)

# Set up LLM provider (optional)
engine.set_llm_provider(DeepSeekProvider(api_key="your-key"))

# Generate novel from chapter plans
result = engine.generate_novel(chapter_plans)
```

### Chapter-by-Chapter Generation

```python
# Plan individual chapters
chapter = engine.plan_chapter(
    chapter_id=1,
    title="The Discovery",
    causal_lines=[...]
)

# Render chapter content
content = engine.render_chapter(chapter)
```

## Example

**Input:**
`Elena, a detective, finds a torn photo in her missing partner's drawer.`

**Output (short excerpt):**
*"Elena stares at the photo. It was taken two days before he vanished. Her hand shakes – not from fear, but from the realisation that the person in the background is her own boss."*

The engine ensures that later chapters never forget the photo, the boss's role, or Elena's emotional state.

## Features

- **Cause-Effect Tracking**: Every story beat connects logically to the next
- **Character Consistency**: Characters maintain established personality traits
- **State Management**: Global story state persists across all chapters
- **Logical Auditing**: Automatic detection of plot holes and inconsistencies
- **Gap Bridging**: Automatic generation of transitional content
- **Visual Reporting**: Generate visual story flow diagrams
- **Multi-Language Support**: Output stories in multiple languages

## License & Authorization

This repository is a technical showcase for **Story Engine**. Copyright © 2026 Shanghai Linming Junhua Technology Co., Ltd. and NOHN AI TECHNOLOGY PTE. LTD. All rights reserved.

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

## Get started

```bash
git clone https://e.gitee.com/nohn-ecosystem/story-engine.git
cd story-engine
```

Happy writing – without the headaches. ✍️