# Traceable Engineering Reports

## Trusted v1 report lifecycle

P7 adds a server-owned report path for typed v1 analyses:

`POST /api/v1/analysis/element` or `POST /api/v1/analysis/structure` → `analysis_run_id` → `GET /api/v1/analysis-runs/{id}` → `GET /api/v1/reports/{id}.pdf`

The server validates the v1 request, executes the existing analysis, normalizes the response, snapshots the capability metadata, creates an immutable analysis-run record, stores it, and only then returns the generated UUID4 run ID. The PDF endpoint accepts only that run ID. It reads the stored snapshot and does not re-run a calculation or accept client result JSON. A browser cannot register an arbitrary result as a trusted run because no result-registration endpoint exists.

The new report is a traceable software record, not an engineering certificate. PDF generation success, transport success, capability status, engineering verification status, and a calculation check state remain separate concepts.

## P7 run-store boundary

`AnalysisRunStore` defines the storage boundary. P7 supplies `InMemoryAnalysisRunStore`, a thread-safe FIFO store with a configurable `STRUCTICODE_ANALYSIS_RUN_LIMIT` and default maximum of 100 records. It deep-copies records on storage and lookup, preventing caller mutation from changing a stored snapshot. When capacity is exceeded, it deterministically evicts the oldest record.

This store is process-local and ephemeral: records are lost on restart, are not durable project history, and are not safe for multi-instance production use. P9 must replace or implement this interface with persistent, owned enterprise storage. P7 does not add a database, identity, project ownership, migrations, or durable history.

## Immutable snapshots and hashes

Run records capture canonical input, normalized canonical result, legacy/unverified result snapshot where applicable, warnings, P6 capability snapshot, engine metadata, canonical units, and status metadata. Report generation reads only this stored record, which prevents client mutation, re-analysis after a code change, and shared report context.

Trace hashing uses SHA-256 over UTF-8 JSON with sorted keys, compact separators, `ensure_ascii=true`, and no Python `repr()` values. Input hash covers the canonical input snapshot. Result hash covers canonical and legacy result snapshots. Record hash covers all engineering-relevant trace fields: analysis kind, code/element, request and verification status, snapshots, ordered warnings, capability snapshot, engine metadata, canonical units, and run schema version. Operational UUID, analysis timestamp, and later PDF generation timestamp are intentionally excluded, so identical engineering content has a stable content hash. They remain visible trace fields and do not alter a stored run hash when a report is downloaded later.

Repository commit SHA is resolved once when the reporting module starts and falls back to `unknown` without Git metadata. It is software provenance only, not an engineering-method version. Engine metadata identifies `legacy_element_compatibility` for current v1 element paths and `p3_linear_elastic_frame_with_legacy_design` for structure responses.

## P6 capability and deferred-phase integration

Every run snapshots its P6 `FamilyCapability`, including family ID, display/jurisdiction labels, metadata confidence, legacy claims, element or structure capabilities, load-combination and seismic capabilities, warnings, and source-blocked future targets. No report-specific code-family truth table exists.

P4 remains `DEFERRED — SOURCE BLOCKED`: current concrete legacy output remains unverified, and missing provided reinforcement leaves relevant flexure/overall checks `NOT_EVALUATED`. P5 remains `DEFERRED — SOURCE BLOCKED`: steel legacy output remains `UNVERIFIED` and `NOT_EVALUATED`; retained `legacy_status` is never turned into a PDF PASS/FAIL or SAFE/UNSAFE conclusion. P3 bounded 2D frame mechanics are reported separately as `ENGINEERING_REVIEW_REQUIRED`; complete structure design and load factors remain `LEGACY_UNVERIFIED`.

## PDF content and safety

The v1 PDF is generated in memory with a unique run-specific download filename and headers. It does not create a shared `report.pdf`. It contains a report header, traceability hashes and software provenance, canonical units, P6 capability statuses, canonical input snapshot, normalized structure results where applicable, legacy/unverified output boundaries, and factual limitations/review requirements. It uses the repository's tracked DejaVu Sans font for stable English and Unicode display without relying on an OS font. Identifiers and values are treated as inert wrapped text; no markup is evaluated.

The report never concludes that a current legacy beam, column, structure, or steel member is SAFE/UNSAFE. It does not repeat generic engineering boilerplate. It visibly identifies the run's engineering verification status and requires independent review for legacy results.

## Legacy PDF compatibility boundary

`POST /generate-pdf` remains only for existing clients. It still accepts client-supplied input and result data, uses its legacy shared-file implementation, returns `X-Structicode-Report-Status: LEGACY_CLIENT_SUPPLIED_UNVERIFIED`, and adds an explicit PDF warning. It is not traceable and is not the P7 solution. Its server error response is generic and does not expose internal exception details.

## P9 handoff

P9 should replace the in-memory store behind `AnalysisRunStore` with durable records owned by projects/organizations/users, preserve immutable input/result/capability snapshots and hash semantics, add retention/audit policies, and coordinate report storage across instances. It must preserve the P7 server-owned run boundary.
