# Analysis Run Schema

## Schema identity

P7 run records use `analysis_run_v1`. The report renderer independently uses `structicode_report_v1`. These version identifiers describe record and PDF structure; neither indicates engineering verification.

## Stored fields

| Field | Purpose |
| --- | --- |
| `run_id` | Server-generated UUID4. The client cannot select it. |
| `created_at` | UTC time after successful server analysis. |
| `analysis_kind` | `element` or `structure`. |
| `code_family_id`, `element_id` | Stable P6 family and relevant element identifiers. |
| `request_status`, `verification_status` | Transport outcome and engineering verification boundary. |
| `canonical_input_snapshot` | Validated P2 canonical input at execution time. |
| `canonical_result_snapshot` | Normalized result available to the v1 response. |
| `legacy_unverified_snapshot` | Retained compatibility output, explicitly unverified. |
| `warnings` | Ordered, deduplicated run warnings. |
| `capability_snapshot` | P6 family and relevant capability truth at execution time. |
| `engine_metadata` | Engine ID/version, engineering status, schema versions, software provenance, and trace notes. |
| `canonical_units` | P2 units: mm, N, MPa, N·mm, N/mm, N/mm², mm², mm⁴, and rad. |
| `input_hash_sha256`, `result_hash_sha256`, `record_hash_sha256` | Deterministic trace hashes. |

## Hash coverage

All hashes use SHA-256 over deterministic UTF-8 JSON: sorted keys, compact separators, ASCII escaping, finite JSON values, and no object representations. Input hash covers only `canonical_input_snapshot`. Result hash covers canonical and legacy result snapshots. Record hash covers analysis kind, family/element identifiers, request/verification status, all snapshots, warnings, capability snapshot, engine metadata, canonical units, and schema version.

`run_id`, `created_at`, generated PDF timestamp, and derived hashes are excluded from record-hash input. This makes equal engineering content reproducible even when it is executed at different times. Those fields are still retained in the run record and visible in the report.

## Immutability and lifetime

The model is frozen. The in-memory store deep-copies on insertion and retrieval so nested JSON snapshots returned to a caller cannot mutate the stored record. P7 records are process-local and bounded; eviction is FIFO. Restarting the process destroys every run. This is an explicit P9 persistence handoff, not durable engineering project history.

## Capability and engine truth

Capability snapshots come from the P6 registry. Legacy claims and source-blocked targets remain metadata boundaries, never authoritative standard editions. Current element compatibility uses `legacy_element_compatibility` with `LEGACY_UNVERIFIED` engineering status. Structure traces identify bounded P3 2D mechanics separately from the still-unverified complete structure design response.
