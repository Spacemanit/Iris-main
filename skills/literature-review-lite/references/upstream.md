# Source and scope

Inspired by [K-Dense-AI/claude-scientific-writer](https://github.com/K-Dense-AI/claude-scientific-writer/tree/main), inspected on 2026-10-13. This package is an independently written, reduced workflow, not a mirror of the source repository or an official K-Dense distribution.

The selected concepts come from:

- [Literature review](https://github.com/K-Dense-AI/claude-scientific-writer/blob/main/skills/literature-review/SKILL.md): scoping, screening, evidence extraction, and thematic synthesis.
- [Citation management](https://github.com/K-Dense-AI/claude-scientific-writer/blob/main/skills/citation-management/SKILL.md): bibliographic verification, deduplication, and manuscript/reference checks.
- [Writing workflow](https://github.com/K-Dense-AI/claude-scientific-writer/blob/main/CLAUDE.md): evidence before drafting, saved research records, and a final review pass.

The implementation combines these into one Codex skill and a standard-library helper. It omits the upstream agent runtime, paid search integration, full manuscript generation, grants, clinical workflows, slides, obligatory generated figures, and automatic PDF production. It supports bounded narrative reviews, not a complete systematic-review or meta-analysis protocol.

The upstream project is MIT licensed, copyright (c) 2025–2026 K-Dense Inc. Its notice is preserved in [../LICENSE](../LICENSE). No upstream executable scripts are bundled. The helper and reduced instructions are newly written for this package.
