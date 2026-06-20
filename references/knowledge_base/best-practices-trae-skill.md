# TRAE Skill Best Practices

source_id: trae-skill-guidelines
source_type: internal-best-practice
publisher: gee-agent-skill
retrieved_at: 2026-06-21
primary_status: project-standard
risk_level: low

## Requirements

- Keep `SKILL.md` concise, preferably below 500 lines.
- Use progressive disclosure: detailed API notes belong in references, deterministic operations belong in scripts, and reusable code templates belong in assets.
- Keep one responsibility per skill.
- State when not to use the skill.
- Define inputs, outputs, failure modes, and validation checks.
- Use clear and consistent terminology.
- Avoid OS-specific paths in skill instructions and generated scripts.
- Avoid time-sensitive conditions unless the source and retrieval date are recorded.
- Never include credentials or credential paths.

