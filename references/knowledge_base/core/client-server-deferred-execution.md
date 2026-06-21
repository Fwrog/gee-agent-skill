# Core Guide: Client/Server and Deferred Execution

source_id: core-client-server-deferred-execution
source_type: official-guide
primary_status: canonical
source_url: https://developers.google.com/earth-engine/guides/client_server
last_checked: 2026-06-21
risk_level: medium

## Use

Earth Engine objects are server-side proxies. Python code constructs a computation graph; Earth Engine evaluates it when a value is requested, visualized, or exported. Generated scripts should keep raster/vector work server-side and avoid unnecessary `getInfo()` calls.

## Operator Notes

- Prefer `map`, `filter`, `reduceRegion`, `reduceRegions`, image properties, and exports over client loops that fetch large server objects.
- Use `getInfo()` only for small preflight probes such as collection size, band names, sampled property names, and tiny reducer sanity checks.
- In generated production workflows, avoid `getInfo()` on full collections, large feature collections, or large dictionaries.

## Failure Cases

known_failure: CLIENT_SERVER_MISUSE

Large client-side materialization can time out, exceed memory, or block reproducibility. Recovery: move computation server-side, export results, or reduce the object before fetching.
