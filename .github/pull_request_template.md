## Summary

Describe the user-facing change and whether it affects docs, templates, validation, preflight, export, or packaging.

## Validation

- [ ] `python -m pytest`
- [ ] `gee-skill smoke-test --json`
- [ ] `python -m build --sdist --wheel`
- [ ] Not run; reason:

## Capability Boundary

- [ ] HK NDVI golden example behavior remains accurate.
- [ ] Non-golden recipe claims are limited to plan/render/validate unless live support is implemented and verified.
- [ ] Preflight success is not described as export submission.

## Safety

- [ ] No credentials, tokens, service account JSON, or local credential paths committed
- [ ] Live Earth Engine behavior requires explicit confirmation
- [ ] Run traces do not write credential material

## Notes

For live Earth Engine changes, include the project-independent evidence: command, run id, preflight result, task state, monitored output, and any interpretation limits.
