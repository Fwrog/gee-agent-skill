# Recipe Card: table-export-csv

source_id: recipe-table-export-csv
source_type: curated-recipe-card
primary_status: curated
recipe_id: table-export-csv
task_type: export_table
description: Export a validated feature collection to Drive as CSV with explicit selectors.
required_inputs: feature_collection, output_schema, export
optional_inputs: drive_folder, file_prefix
candidate_datasets: none
default_dataset_policy: Use table output from the upstream reducer recipe.
template: recipes/export_table
preflight_profile: export_table
validation_profile: export_table_csv
output_schema: selectors, file_format, export_description, drive_folder
live_risk_level: high
last_checked: 2026-06-24
risk_level: high

## Use

Export a validated feature collection to Drive as CSV with explicit selectors.

## Required Inputs

- feature_collection
- output_schema
- export

## Optional Inputs

- drive_folder
- file_prefix

## Dataset Policy

Use table output from the upstream reducer recipe.

Candidate datasets: none.

## Template and Safety

- Template: `recipes/export_table`
- Preflight profile: `export_table`
- Validation profile: `export_table_csv`
- Live risk level: `high`

## Output Schema

- selectors
- file_format
- export_description
- drive_folder

## Examples

- Export zonal statistics as CSV.

## Limitations

- CSV exports need stable selectors and monitored task state before claiming success.
