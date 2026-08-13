# Story Engine（故事引擎）

<p align="center">
  <img src="https://img.shields.io/badge/story--engine-D4AF37?style=flat-square" alt="story-engine">  <img src="https://img.shields.io/badge/spl--pipeline-D4AF37?style=flat-square" alt="spl-pipeline">  <img src="https://img.shields.io/badge/multi--causal-D4AF37?style=flat-square" alt="multi-causal">
</p>

基于 **SPL（故事/系统处理语言）** 的故事生成与推演引擎。以四阶段确定性流水线驱动，融合多因果网络，产出结构一致、因果可追溯的叙事。

---

## ✨ 特性

- **SPL 四阶段流水线**：叙事解构 → 因果建模 → 分支推演 → 渲染输出。
- **多因果网络**：支持多条并行因果链与交汇，保证情节闭合而非随机发散。
- **引擎与创作器分离**：`engine for business.py` 提供可嵌入的业务接口；`Story Engine for Creator.py` 面向创作者的编排工具。
- **确定性输出**：相同输入产生一致结果，便于审计与复现。
- **可集成 LLM**：默认内置 Mock 推理，可替换为真实大模型提供方。

## 📦 模块

| 文件 | 用途 |
|------|------|
| `engine for business.py` | 业务侧引擎：状态机、角色推断、章节渲染、可嵌入接口 |
| `Story Engine for Creator.py` | 创作者侧：自动状态抽取、章节编译、整书渲染 |
| `compile_all.py` / `render_chapter` | 章节级与整书级渲染入口 |

## 🚀 快速开始

```bash
# 依赖
pip install -r requirements.txt   # 或仅标准库即可运行演示

# 运行演示
python "engine for business.py"
python "Story Engine for Creator.py"
```

## 🧩 工作原理（简述）

1. **叙事解构**：将大纲拆分为场景、角色、目标等结构化单元。
2. **因果建模**：为每个单元建立因果前驱/后继，构成多因果网络。
3. **分支推演**：在决策点按声明规则展开分支，检测悬空与死锁。
4. **渲染输出**：将选定路径渲染为连贯文本，保留因果标注。

## 🔗 相关

- 因果审计内核：第二视角决策引擎（second-perspective / nomos）
- 拟人化智能体引擎：Anthropomorphic-Agent-Engine
- 在线体验：https://nohnlins.com/

## 📜 许可与授权

本仓库**非开源**。采用双轨模式：个人非商业研究免费；政府 / 企业需事先取得书面商业授权。详见 [LICENSE](./LICENSE)。

---

<p align="center">
  <a href="https://github.com/NOHN-AI">NOHN-AI</a>
  &nbsp;·&nbsp;
  <a href="https://www.nohnlins.com/">nohnlins.com</a>
  &nbsp;·&nbsp;
  <a href="mailto:lin@secondai.top">lin@secondai.top</a>
</p>
<p align="center"><sub>NOHN AI · Story Engine</sub></p>
