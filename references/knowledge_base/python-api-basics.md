# Python API Basics

source_id: google-ee-client-server
source_type: official-guide
publisher: Google Earth Engine
url: https://developers.google.com/earth-engine/guides/client_server
retrieved_at: 2026-06-21
primary_status: canonical
risk_level: low

## Server-Side Model

Earth Engine objects represent deferred server-side computations. Generated Python code should compose server-side operations and exports instead of pulling large data to the client.

Avoid unnecessary `getInfo()` calls. They block execution, can be slow, and can move large data from the server to the local process. Use exports, reducers, server-side mapping, and metadata properties for production workflows.

## Mapping

When mapping over `ImageCollection`, `FeatureCollection`, or `ee.List`, keep mapped functions serializable. Do not use local Python side effects, local file writes, or client-side branching inside server-side mapped functions.

