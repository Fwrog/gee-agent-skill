from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _add_src_to_path() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def _csv(values: list[str]) -> str:
    return ", ".join(str(value) for value in values) if values else "none"


def _bullets(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values) if values else "- none"


def _recipe_markdown(recipe: dict) -> str:
    recipe_id = recipe["recipe_id"]
    template = recipe.get("template") or "not-yet-template-backed"
    return f"""# Recipe Card: {recipe_id}

source_id: recipe-{recipe_id}
source_type: curated-recipe-card
primary_status: curated
recipe_id: {recipe_id}
task_type: {recipe["task_type"]}
description: {recipe["description"]}
required_inputs: {_csv(recipe["required_inputs"])}
optional_inputs: {_csv(recipe["optional_inputs"])}
candidate_datasets: {_csv(recipe["candidate_datasets"])}
default_dataset_policy: {recipe["default_dataset_policy"]}
template: {template}
preflight_profile: {recipe["preflight_profile"]}
validation_profile: {recipe["validation_profile"]}
output_schema: {_csv(recipe["output_schema"])}
live_risk_level: {recipe["live_risk_level"]}
last_checked: 2026-06-24
risk_level: {recipe["live_risk_level"]}

## Use

{recipe["description"]}

## Required Inputs

{_bullets(recipe["required_inputs"])}

## Optional Inputs

{_bullets(recipe["optional_inputs"])}

## Dataset Policy

{recipe["default_dataset_policy"]}

Candidate datasets: {_csv(recipe["candidate_datasets"])}.

## Template and Safety

- Template: `{template}`
- Preflight profile: `{recipe["preflight_profile"]}`
- Validation profile: `{recipe["validation_profile"]}`
- Live risk level: `{recipe["live_risk_level"]}`

## Output Schema

{_bullets(recipe["output_schema"])}

## Examples

{_bullets(recipe["examples"])}

## Limitations

{_bullets(recipe["limitations"])}
"""


def main(argv: list[str] | None = None) -> int:
    _add_src_to_path()
    from geeskill.recipes import load_recipe_registry

    parser = argparse.ArgumentParser(description="Generate RAG-visible recipe cards from the recipe registry.")
    parser.add_argument("--out-dir", default="references/knowledge_base/recipes")
    args = parser.parse_args(argv)

    registry = load_recipe_registry()
    recipes = [item.to_dict() for item in registry["recipes"]]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for recipe in recipes:
        path = out_dir / f"{recipe['recipe_id']}.md"
        path.write_text(_recipe_markdown(recipe), encoding="utf-8")
    print(f"wrote {len(recipes)} recipe cards -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
