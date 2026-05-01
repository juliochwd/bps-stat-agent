<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-30 | Updated: 2026-04-30 -->
# system_prompts

## Purpose
Specialized system prompts for research sub-agents and quality modules. Each prompt defines the persona, capabilities, and constraints for a specific role in the research workflow.

## Key Files
| File | Description |
|------|-------------|
| `orchestrator.md` | System prompt for the research orchestrator — manages phase transitions and delegation |
| `section_writer.md` | System prompt for the section writing sub-agent — academic writing style and citation rules |
| `peer_reviewer.md` | System prompt for the simulated peer reviewer — structured critique format |
| `stat_validator.md` | System prompt for statistical validation — methodology checking rules |
| `citation_verifier.md` | System prompt for citation verification — completeness and format checking |

## For AI Agents

### Working In This Directory
- Each `.md` file is a complete system prompt loaded by the corresponding research module
- Prompts define: role, capabilities, output format, constraints
- Prompts may contain `{PLACEHOLDER}` variables replaced at runtime (e.g., `{TEMPLATE_NAME}`, `{PHASE}`)
- Keep prompts focused on a single role — avoid mixing responsibilities
- Test prompt changes by running research mode: `bpsagent research --title "Test"`

### Prompt Structure Convention
```markdown
# Role
You are a [role description]...

# Capabilities
- Capability 1
- Capability 2

# Output Format
[Structured output requirements]

# Constraints
- Constraint 1
- Constraint 2
```

### Adding a New Sub-Agent Prompt
1. Create `{role_name}.md` in this directory
2. Follow the structure convention above
3. Reference in the corresponding Python module via `config_dir / "system_prompts" / "role_name.md"`

## Dependencies

### Internal
- Loaded by `mini_agent.research.sub_agents` and quality modules
- Referenced via config path resolution in `mini_agent.config`

### External
- None (static markdown content)

<!-- MANUAL: -->
