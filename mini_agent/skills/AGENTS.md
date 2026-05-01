<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-30 | Updated: 2026-04-30 -->
# skills — Claude Skills Directory

## Purpose

Bundled skill packages that provide domain-specific guidance and instructions to the agent. Skills are loaded on-demand using **progressive disclosure** — only metadata (names + descriptions) is injected into the system prompt at startup (Level 1); full skill content is retrieved via the `get_skill` tool when the agent needs it (Level 2).

13 skill packages covering academic research, BPS data expertise, document creation, design, testing, and more.

## Key Files

| File | Description |
|------|-------------|
| `README.md` | Overview of the skills system and available skills. |
| `AGENTS.md` | This file. |
| `agent_skills_spec.md` | Specification for skill package format and progressive disclosure protocol. |
| `THIRD_PARTY_NOTICES.md` | Third-party attribution for bundled skills. |

## Skill Packages

| Skill | Description |
|-------|-------------|
| `academic-research/` | Academic paper writing methodology, IMRaD structure, citation practices, peer review preparation. Includes `references/` subdirectory. |
| `algorithmic-art/` | Generative art and creative coding patterns. Includes `templates/` for art generation. |
| `artifacts-builder/` | Building structured artifacts (documents, presentations, reports). Includes `scripts/` for automation. |
| `bps-master/` | BPS Indonesia data query expertise, domain knowledge, API usage patterns, statistical indicator references. Includes `references/` and `scripts/`. |
| `brand-guidelines/` | Brand identity and design system guidance. |
| `canvas-design/` | Canvas/visual design patterns. Includes `canvas-fonts/` for typography. |
| `document-skills/` | Comprehensive document creation: DOCX (with OOXML schemas, validation scripts, templates), PDF (with scripts), PPTX (with OOXML schemas, validation), XLSX. |
| `internal-comms/` | Internal communication drafting. Includes `examples/` for reference. |
| `mcp-builder/` | Building MCP servers and tools. Includes `reference/` docs and `scripts/`. |
| `skill-creator/` | Meta-skill for creating new skills. Includes `scripts/` for scaffolding. |
| `slack-gif-creator/` | Slack-compatible GIF creation. Includes `core/` logic and `templates/`. |
| `template-skill/` | Template for creating new skills. Copy this to start a new skill package. |
| `theme-factory/` | UI theme and styling generation. Includes `themes/` directory. |
| `webapp-testing/` | Web application testing strategies. Includes `examples/` and `scripts/`. |

## For AI Agents

### Working In This Directory

- Each skill is a subdirectory containing markdown files with instructions and examples
- Skills are discovered by `mini_agent.tools.skill_loader.SkillLoader` at startup
- **Progressive disclosure (2 levels)**:
  1. **Level 1 (startup):** Skill names + short descriptions injected into system prompt via `{SKILLS_METADATA}` placeholder
  2. **Level 2 (on-demand):** Full skill content loaded via `get_skill` tool when agent needs domain-specific guidance
- To create a new skill: copy `template-skill/`, add markdown content, skill is auto-discovered on next startup
- Skill directory must contain at least one `.md` file to be recognized
- Skills are **read-only at runtime** — they provide guidance, not executable code
- The `.claude-plugin` directory contains Claude-specific plugin metadata

### Skill Package Structure
```
my-skill/
  README.md          # Skill overview (first line = title, used for Level 1 metadata)
  instructions.md    # Detailed instructions (loaded at Level 2)
  examples.md        # Usage examples (optional)
  references/        # Reference materials (optional)
  scripts/           # Helper scripts (optional)
```

### Adding a New Skill

1. Create directory under `skills/` with kebab-case name (e.g., `my-new-skill/`)
2. Add `README.md` with skill name as first line and description
3. Add instruction/example markdown files
4. Skill is automatically discovered on next agent startup
5. No code changes needed — the `SkillLoader` auto-discovers new directories

### Testing Requirements

- Verify all skill directories contain at least one `.md` file
- Test `SkillLoader` discovery with the skills directory
- Test `GetSkillTool` retrieval of specific skill content
- Test `{SKILLS_METADATA}` placeholder replacement in system prompt
- Verify skill content is read-only (no write operations)

### Common Patterns

- Skill metadata extraction: first line of `README.md` = title, rest = description
- Skills with `references/` subdirectories contain domain-specific reference materials
- Skills with `scripts/` subdirectories contain automation helpers
- `document-skills/` is the most complex skill with nested OOXML schema directories

## Dependencies

### Internal
- Consumed by `mini_agent.tools.skill_loader.SkillLoader`
- Exposed via `mini_agent.tools.skill_tool.GetSkillTool`

### External
- None (static markdown content)
