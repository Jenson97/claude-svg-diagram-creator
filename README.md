# SVG Diagram Creator

An AI-powered SVG diagram creation plugin for Claude Code. Covers **13 diagram types** across 3 categories — from technical architecture diagrams to comic infographics.

## Categories & Types

| Category | Types |
|----------|-------|
| **Technical (T)** | T1 Vertical Pipeline, T2 Horizontal Matrix, T3 Before/After Comparison, T4 Multi-Layer Architecture, T5 Multi-Column Cards, T6 Branch/Merge Flow, T7 Concentric Nested |
| **Scenario (S)** | S1 Scenario Workflow, S2 Character-Guided, S3 Flywheel Cycle, S4 Data Showcase Cards |
| **Comic (E)** | E1 Comic Infographic, E2 Four-Panel Comic |

## Features

- 🎨 **Dark theme support** — Technical diagrams with JetBrains Mono + export toolbar
- 🔍 **Auto-detection** — Intent matching from natural language descriptions
- 🖼️ **Reference imitation** — Analyze uploaded images and replicate their style
- ✏️ **Iteration mode** — Modify existing diagrams without regenerating
- ✅ **Render QA** — Built-in script for bleed/whitespace detection

## Usage Modes

| Mode | Trigger | Description |
|------|---------|-------------|
| **A. Describe** | "Draw a pipeline diagram" | Generate from description |
| **B. Imitate** | Upload image + "make something like this" | Analyze reference → generate |
| **C. Edit** | "Change the title" | Modify existing SVG/HTML |
| **D. Prompt output** | E1/E2 types | Hover-to-reveal prompts + copy |

## Installation

```bash
claude plugins install svg-diagram-creator@claude-plugins-official
```

Or install directly from source:

```bash
claude plugins install Jenson97/claude-svg-diagram-creator
```

## Output

Generated diagrams are saved to `${CONTENT_ROOT:-/data/wangtao/content}/diagram/<YYYY-MM-DD>-<slug>/`.

## License

MIT — see [LICENSE](./LICENSE) for details.
