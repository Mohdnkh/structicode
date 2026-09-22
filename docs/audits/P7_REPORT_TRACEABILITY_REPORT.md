# P7 Engineering Reports and Traceability Audit

## Scope and baseline

P7 started on `codex/p7-report-traceability` from synchronized `main` at `dea5be9a1d62c15c11036899d96a29f8a9f493bb`. The former `/generate-pdf` endpoint accepted client-owned input/result JSON and wrote a shared `report.pdf`, providing no server-side analysis identity or immutable trace chain. It is retained solely for compatibility and is explicitly labelled `LEGACY_CLIENT_SUPPLIED_UNVERIFIED`.

## Trusted reporting implementation

The new v1 chain is validated request → completed server analysis → UUID4 analysis-run record → bounded server store → run-ID PDF. Element and structure success responses return `analysis_run_id`. `GET /api/v1/analysis-runs/{run_id}` returns the typed stored record, and `GET /api/v1/reports/{run_id}.pdf` returns an in-memory `application/pdf` report derived only from that record. No POST endpoint exists for client-submitted result registration.

`AnalysisRunRecord` includes canonical snapshots, status fields, warnings, P6 capability snapshot, engine and software provenance, P2 canonical units, and SHA-256 hashes. Hash serialization is sorted-key compact UTF-8 JSON. The content hash excludes run UUID, analysis timestamp, and later PDF generation timestamp so equal engineering content has equal hashes. The store uses an `AnalysisRunStore` interface and thread-safe bounded FIFO implementation with a 100-record default. It is explicitly process-local and ephemeral; P9 must add durable, owned persistence.

## Report truth

The report header, traceability section, capability section, canonical inputs, normalized structure results, legacy/unverified boundary, and limitations section distinguish report success from engineering verification. Reports snapshot P6 metadata without creating a second family map. Concrete legacy reports preserve the P4 `NOT_EVALUATED` boundary where reinforcement is absent. Steel reports preserve P5 `UNVERIFIED` / `NOT_EVALUATED` semantics and never promote a legacy comparison to SAFE/UNSAFE. Structure reports separate P3 mechanics (`ENGINEERING_REVIEW_REQUIRED`) from complete structure design and load combinations (`LEGACY_UNVERIFIED`). P4 and P5 remain source blocked.

The new renderer uses the tracked DejaVu Sans font, generates bytes in memory, uses run-specific filenames/headers, wraps untrusted text, and does not use generic safety boilerplate. It does not create persistent PDF files or shared report context.

## Files

Added: `backend/api/reporting/__init__.py`, `models.py`, `run_store.py`, `trace.py`, `pdf.py`, `report_api.py`; `backend/tests/test_reporting.py`; `docs/engineering/REPORT_TRACEABILITY.md`; `docs/engineering/ANALYSIS_RUN_SCHEMA.md`; and this audit.

Modified: `backend/api/domain/schemas.py`, `backend/api/v1.py`, `backend/api/main.py`, `backend/api/utils/pdf_generator.py`, `frontend/src/api/client.js`, and the roadmap.

No reporting, database, identity, calculation, solver, load factor, seismic, or section-property file was deleted or changed beyond the listed report compatibility hardening.

## Validation

The P7 suite contains 11 tests covering server ownership, no result-registration endpoint, deterministic hashing, immutable deep-copy retrieval, deterministic eviction, unknown-run structured errors, P6 capability snapshotting, P3/design separation, P4/P5 safety semantics, report headers, forged client result isolation, concurrency isolation, legacy endpoint labelling, and Unicode/long-text rendering. The full backend suite passed 377 tests; explicit P3, P4, P5, and P6 regressions passed 41, 25, 43, and 144 tests. Frontend adapter tests passed 3 tests, the Vite build completed with 469 modules transformed, backend import verification passed, and `git diff --check` passed. Visual inspection rendered a two-page local sample report and confirmed its header, section hierarchy, page footer, wrapping, status labels, and canonical units were readable.

## Limitations

P7 storage is process-local and lost on restart. The raw legacy PDF remains client-supplied and non-traceable for compatibility. The report renderer does not verify any legacy equation, code edition, section data, load factor, or seismic output. P8 owns presentation integration and P9 owns durable run storage, identity, projects, and ownership.
