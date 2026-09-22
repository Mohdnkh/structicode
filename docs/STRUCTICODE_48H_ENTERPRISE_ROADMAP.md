# STRUCTICODE

## 48-Hour Enterprise Stabilization & Development Roadmap

Local-first execution. Deployment is the final gate only.

| Repository | Mohdnkh/structicode |
| --- | --- |
| Maximum execution window | 48 hours |
| Primary workflow | ChatGPT review -> Codex implementation -> report -> review -> commit/push decision |
| Deployment policy | No deployment work before Phase P12 |
| Document language | English only |

**Purpose**

Convert the current prototype into a reliable, testable, traceable engineering platform foundation, with one validated calculation path and an architecture capable of adding verified international design-code modules without duplicating or fabricating engineering logic.

## Execution Rules

- All development and verification before Phase P12 must run locally. Railway or any other production deployment must not be changed during P0-P11.
- Codex receives one implementation prompt per phase. Prompts are not stored in this roadmap.
- At the start of a phase, Codex may change that phase status from HOLD to IN PROGRESS. When implementation and its own checks are complete, Codex may change it only to READY FOR REVIEW.
- Codex must never mark a phase APPROVED or PUSHED. Those states are assigned only after independent review and an explicit commit/push decision.
- Every phase must end with a written implementation report: files changed, behavior changed, tests executed, test results, known limitations, unresolved risks, and recommended next action.
- No engineering calculation may return an authoritative SAFE/UNSAFE verdict when required inputs, code provisions, unit definitions, or validation evidence are incomplete. Use NOT VERIFIED, NOT EVALUATED, or INCOMPLETE instead.
- Calculation sources must be authoritative and versioned. Each verified module must record the applicable standard edition, assumptions, units, references, and benchmark evidence.
- If a phase uncovers a critical defect that invalidates later work, the phase may be marked BLOCKED and the defect must be resolved before continuing.
- A phase deferred because an authoritative external source or license is unavailable does not automatically freeze unrelated later phases. Later work may proceed only when the blocker is external rather than an unresolved software defect that invalidates later calculations, known safety-critical misleading behavior from the deferred phase has been contained, and the next phase does not technically depend on the missing verified capability. The deferred exit gate remains unmet. Product acceptance and deployment must not treat the deferred phase as complete.
- Before P11 or P12 can be completed, every deferred engineering phase must be completed and verified, intentionally removed from release scope, or retained as explicitly UNVERIFIED / NOT IMPLEMENTED with consistent product, UI, and report claims. A deferred capability cannot silently become a release-ready verified capability.

### Phase Branch Workflow (P3 onward)

- Start each phase from current `main` and use one dedicated phase branch.
- Codex commits and pushes only the phase branch, then opens a pull request directly into `main`.
- The phase remains READY FOR REVIEW while the pull request is open; independent review examines the GitHub pull request.
- Codex must not merge its own pull request. Only after explicit approval and a successful merge may the phase become PUSHED.
- Rework stays on the same phase branch and pull request. Deployment remains prohibited until P12.

### Status Workflow

| Status | Who sets it | Meaning |
| --- | --- | --- |
| HOLD | Roadmap default | Phase has not started. |
| IN PROGRESS | Codex | Implementation is actively being executed. |
| READY FOR REVIEW | Codex | Implementation report and tests are complete; waiting for independent review. |
| REWORK REQUIRED | Reviewer | Review found defects that must be corrected before approval. |
| APPROVED | Reviewer | Phase changes and evidence have passed review; not yet pushed. |
| PUSHED | Reviewer / Git owner | Approved phase has been committed and pushed to the repository. |
| BLOCKED | Codex or Reviewer | A critical dependency or defect prevents safe continuation. |
| DEFERRED — SOURCE BLOCKED | Reviewer / Git owner | Planned verified scope remains incomplete because an authoritative external source or license is unavailable. Safety-critical findings must be contained; technically independent later phases may proceed under the execution rules. The deferred exit gate must be revisited before product acceptance or release. |

## Master Execution Tracker

Codex must keep this tracker current in the repository copy of the roadmap. Only the active phase row and factual notes should be updated unless explicitly instructed otherwise.

| Phase | Name | Time Box | Status | Review / Commit | Notes |
| --- | --- | --- | --- | --- | --- |
| P0 | Repository Safety & Baseline | 0-2 h | PUSHED | - | - |
| P1 | Local Development & Reproducible Build | 2-5 h | PUSHED | - | - |
| P2 | API Contracts & Unit System Foundation | 5-9 h | PUSHED | - | - |
| P3 | Structural Solver Stabilization | 9-14 h | PUSHED | - | - |
| P4 | Verified Concrete Core | 14-20 h | DEFERRED — SOURCE BLOCKED | - | Verified ACI CODE-318-25 core not implemented; authorized source access required. P4 safety remediation merged. No concrete capability promoted to VERIFIED. |
| P5 | Verified Steel Core | 20-25 h | DEFERRED — SOURCE BLOCKED | - | Exact ANSI/AISC 360-22 provisions, applicable errata, authoritative section properties, and independent reference examples remain unavailable. Legacy steel safety claims are contained; no steel rule is VERIFIED. Verified P5 exit gate remains unmet. |
| P6 | Design-Code Registry & International Architecture | 25-29 h | PUSHED | - | Typed registry and read-only capability API implemented and merged to main. P4/P5 remain deferred and no design module became VERIFIED. |
| P7 | Engineering Reports & Traceability | 29-33 h | READY FOR REVIEW | - | Server-owned v1 run records, trace hashes, bounded ephemeral store, run lookup, and in-memory PDF reports implemented. P4/P5 remain deferred; no legacy output is promoted to VERIFIED. |
| P8 | Enterprise UI/UX & Engineering Workspace | 33-39 h | HOLD | - | - |
| P9 | Projects, Identity & Enterprise Data Foundation | 39-42 h | HOLD | - | - |
| P10 | QA, Security & Reliability Gate | 42-45 h | HOLD | - | - |
| P11 | Product Acceptance & Documentation | 45-47 h | HOLD | - | - |
| P12 | Deployment Decision & Release Packaging | 47-48 h | HOLD | - | - |

## 48-Hour Scope Boundary

- The 48-hour target is a stable enterprise-grade foundation, a validated calculation core, a reliable local workflow, and a credible product experience. It is not a claim that every structural code in the world can be fully verified within two days.
- International code support must move from marketing-style labels to explicit capability states: VERIFIED, BETA / ENGINEERING REVIEW REQUIRED, NOT IMPLEMENTED, or LEGACY.
- Within this window, priority is correctness, traceability, tests, and architecture. Additional verified standards can then be added as independent modules without rewriting the platform.
- No production launch is required at the end of 48 hours. Phase P12 produces the deployment decision and release package; hosting provider selection can be made after the engineering gates pass.

## P0 - Repository Safety & Baseline

Time box: 0-2 hours  |  Initial status: HOLD

Objective: Freeze a trustworthy starting point and remove ambiguity about what is being changed.

- Create a dedicated working branch for the 48-hour remediation effort; do not develop directly on the production branch.
- Capture the current commit SHA, repository tree, dependency manifests, known failing commands, and current local startup behavior.
- Add or update the repository roadmap copy and initialize all phase statuses to HOLD.
- Document current critical findings from the audit as reproducible defects, including unit inconsistencies, unsafe verdict paths, broken structure analysis flow, report trust issues, and build problems.
- Prevent accidental deployment actions during P0-P11 and document the local-only rule.
- Identify tracked generated artifacts and repository hygiene issues such as node_modules, dist output, __pycache__, generated reports, and duplicate datasets.

Exit gate: A reproducible baseline exists, the working branch is isolated, the roadmap is in the repository, and no application behavior has been silently changed.

## P1 - Local Development & Reproducible Build

Time box: 2-5 hours  |  Initial status: HOLD

Objective: Make the project start, test, and build consistently on a clean local machine before touching engineering logic.

- Standardize the root development commands for frontend and backend with cross-platform behavior.
- Choose one JavaScript package manager, regenerate and validate the lockfile, and remove conflicting dependency artifacts.
- Normalize Python startup paths and module imports so FastAPI starts from the repository root without environment-specific hacks.
- Configure the Vite development proxy or an explicit local API base so frontend requests reach FastAPI reliably.
- Remove tracked generated dependencies/build outputs from version control and fix ignore rules.
- Add health/readiness endpoints suitable for local verification.
- Establish clean install, clean build, frontend start, backend start, and smoke-test commands.

Exit gate: A clean checkout can install dependencies, start frontend/backend locally, execute a smoke request, and build the frontend without relying on Railway or prebuilt dist files.

## P2 - API Contracts & Unit System Foundation

Time box: 5-9 hours  |  Initial status: HOLD

Objective: Eliminate silent unit conversion and data-contract ambiguity across UI, API, solver, and calculation modules.

- Define a canonical internal unit system for force, length, stress, area, inertia, moment, and distributed loads.
- Create explicit conversion utilities and prohibit scattered ad-hoc conversion constants inside engineering formulas.
- Replace unrestricted analysis dictionaries with typed request/response schemas and bounded validation where practical.
- Define normalized enums/identifiers for design codes, element types, support types, load cases, and result states.
- Unify API prefixes and endpoint contracts used by both Analyzer and Structure Designer.
- Return structured validation errors without exposing internal exceptions to clients.
- Add contract tests for representative frontend payloads and invalid-unit/invalid-range cases.

Exit gate: Every calculation receives normalized typed data in the canonical unit system, API routes are consistent, and contract tests prove the frontend/backend agreement.

## P3 - Structural Solver Stabilization

Time box: 9-14 hours  |  Initial status: HOLD

Objective: Turn the 2D frame engine into a deterministic, unit-consistent, benchmarked solver rather than a prototype matrix calculation.

- Correct load-combination behavior so absent load cases receive a zero factor, not a default factor of one.
- Correct element load vectors, sign conventions, transformation handling, reaction recovery, and member-end force recovery.
- Make material stiffness units consistent with geometry and force units.
- Replace equal slab-load distribution with an explicitly defined tributary-load method or mark slab distribution unavailable until verified.
- Validate supports, connectivity, zero-length members, duplicate nodes/members, and global stability before solving.
- Return useful mechanism/singular-system diagnostics instead of raw NumPy errors.
- Add analytical benchmark tests for simple beams, cantilevers, and at least one frame, checking reactions, displacements, and member forces within documented tolerances.

Exit gate: The solver passes the benchmark suite with documented tolerances and no known unit or load-combination defect remains in the supported 2D scope.

## P4 - Verified Concrete Core

Time box: 14-20 hours  |  Initial status: HOLD

Objective: Replace generic concrete checks with a traceable, validated concrete-design core for the first supported standard family.

- Select and record the exact initial concrete design standard edition and load standard used by the verified path.
- Remove fabricated As_provided behavior and require actual provided reinforcement when a capacity verdict depends on it.
- Correct concrete beam, column, slab, footing, and staircase unit handling before exposing any design verdict.
- For the 48-hour verified scope, prioritize a fully tested reinforced-concrete beam path, then the most reliable additional element checks that can meet the same evidence standard.
- Implement explicit NOT VERIFIED / NOT IMPLEMENTED results for unsupported modes such as placeholder section types or incomplete interaction checks.
- Record assumptions, applicability limits, demand/capacity values, governing checks, and source references in structured calculation results.
- Add benchmark examples, edge cases, invalid-input tests, and regression tests for every calculation considered verified.

Exit gate: At least one concrete design path is end-to-end verified with source/edition metadata, unit proofs, benchmark tests, and truthful capability states for everything outside that verified scope.

Restart condition: Resume verified P4 work only when authorized access to the applicable SI content of ACI CODE-318-25, or authorized ACI 318 PLUS access covering that edition, permits checking the exact provisions, equations, tables, limits, strength-reduction rules, and detailing requirements for the intended implementation. The P4 exit gate remains unmet until the verified work and evidence are complete.

## P5 - Verified Steel Core

Time box: 20-25 hours  |  Initial status: HOLD

Objective: Replace the current duplicated and unit-inconsistent steel logic with one authoritative, testable steel-design engine.

- Remove or consolidate duplicate steel calculation paths so there is one source of truth.
- Correct section-property units and all moment/axial conversions; stop reconstructing authoritative section properties from unsafe approximations when validated catalog values exist.
- Version the steel section dataset and define its property units and source provenance.
- Implement the first verified beam and column scope using the selected steel standard edition, including only checks that are actually implemented and validated.
- Expose unbraced length, effective length, axis, section properties, and other required engineering inputs explicitly instead of hiding assumptions.
- Add benchmark cases for flexure and compression and regression tests for the previously reproduced unit failures.
- Return NOT EVALUATED for checks that are outside the implemented scope rather than treating omission as success.

Exit gate: Steel beam/column results come from a single unit-consistent engine, benchmark tests pass, and unsupported limit states are clearly reported rather than silently ignored.

Source-blocked restart condition: Resume verified P5 only when the exact applicable ANSI/AISC 360-22 provisions and limits, applicable errata checked against the source printing, authoritative section properties such as AISC Shapes Database v16.0 with definitions and units, and published/reference beam and column examples can be inspected for independent benchmarks. The verified exit gate remains unmet while P5 is deferred.

## P6 - Design-Code Registry & International Architecture

Time box: 25-29 hours  |  Initial status: HOLD

Objective: Create the architecture needed to support international standards honestly and incrementally.

- Replace free-form code names with a central design-code registry containing jurisdiction, material scope, standard name, edition, status, and applicable load/seismic references.
- Separate VERIFIED implementations from BETA, LEGACY, and NOT IMPLEMENTED entries.
- Remove generic wrappers that merely rename ACI-style formulas while implying independent code compliance.
- Define a module contract for code-specific material rules, combinations, checks, clauses/references, assumptions, and benchmark suites.
- Support code edition selection and national annex/jurisdiction metadata where required by the standard family.
- Keep unsupported code families visible only if the UI clearly communicates their real capability state.
- Create a documented onboarding template for adding the next verified international code without duplicating platform logic.

Exit gate: The application can accurately state what is verified, beta, legacy, or unimplemented, and future code modules have a strict technical contract and validation path.

## P7 - Engineering Reports & Traceability

Time box: 29-33 hours  |  Initial status: HOLD

Objective: Turn reports into server-generated engineering records tied to immutable analysis inputs and engine metadata.

- Generate reports from trusted server-side analysis results rather than accepting arbitrary result objects from the browser.
- Assign unique analysis/report identifiers and eliminate shared filenames that can collide across requests.
- Include input snapshot, units, code edition, engine version, assumptions, warnings, governing checks, demand/capacity values, and verification status.
- Add tables/diagrams that explain the calculation outcome instead of only printing raw JSON-style values.
- Support Unicode text correctly and verify report generation for both supported interface languages where required.
- Make report failures deterministic and test concurrent report generation.
- Never label an incomplete calculation as safe in the generated report.

Exit gate: A report can be regenerated from a stored/identified analysis run and contains enough metadata to audit which inputs, engine version, and design standard produced it.

## P8 - Enterprise UI/UX & Engineering Workspace

Time box: 33-39 hours  |  Initial status: HOLD

Objective: Replace the prototype form experience with a professional engineering workflow suitable for students, academics, and professional organizations.

- Define an enterprise design system: typography, spacing, form controls, validation states, tables, cards, dialogs, severity/status language, and responsive behavior.
- Rebuild the main workflow around Project -> Model/Input -> Loads -> Analysis -> Design Checks -> Results -> Report.
- Restore and redesign the element analyzer so code selection, element selection, inputs, validation, results, warnings, and assumptions are all visible and usable.
- Upgrade the Structure Designer with support assignment, property editing, selection, deletion, snapping/grid behavior, loads, materials/sections, model validation, and clear analysis controls.
- Add result visualization for deformed shape and supported force diagrams where the solver data is validated.
- Make verified/beta/not-implemented capability states prominent before the user runs a calculation.
- Improve bilingual layout support without duplicating engineering logic; ensure accessibility basics and usable keyboard/focus behavior.
- Remove misleading controls for features that do not actually work.

Exit gate: The application presents a coherent engineering workspace, does not overstate capabilities, and allows a user to complete the validated analysis flow without hidden or broken UI steps.

## P9 - Projects, Identity & Enterprise Data Foundation

Time box: 39-42 hours  |  Initial status: HOLD

Objective: Lay the minimum enterprise SaaS foundation for persistent projects and future institutional subscriptions without delaying engineering validation.

- Define project, organization, user, analysis-run, report, and engine-version data models.
- Add a local database configuration and migrations for the minimum persistent project/analysis workflow.
- Implement authentication and basic role boundaries only to the depth that can be safely completed and tested in the time box.
- Define tenant ownership on project and analysis data so later multi-organization isolation is explicit.
- Create audit fields for who created/ran/changed records and when.
- Keep billing/subscription integration outside the critical path; define entitlement boundaries and extension points instead of rushing payment code.

Exit gate: Projects and analysis runs have a versionable persistence model with ownership/audit concepts, and no incomplete enterprise feature is presented as production-ready.

## P10 - QA, Security & Reliability Gate

Time box: 42-45 hours  |  Initial status: HOLD

Objective: Create the automated evidence required to prevent regression in a high-consequence engineering application.

- Run the full unit, benchmark, API contract, report, frontend, and end-to-end smoke test suites.
- Add CI configuration that executes deterministic tests and build checks on every pull request/push.
- Restrict CORS to configured local/approved origins and remove raw internal exception leakage.
- Add request size/value limits, model complexity limits, and defensive validation around computational endpoints.
- Check dependency security, secret handling, environment templates, and repository hygiene.
- Verify that two different project/organization contexts cannot accidentally read or overwrite one another in the implemented persistence scope.
- Document known numerical limitations, unsupported calculations, and remaining security work before any public release.

Exit gate: CI is green, benchmark calculations pass, clean build passes, critical security misconfigurations are removed, and known limitations are explicit.

## P11 - Product Acceptance & Documentation

Time box: 45-47 hours  |  Initial status: HOLD

Objective: Freeze the repaired product candidate and confirm that documentation, behavior, and engineering claims match reality.

- Execute a clean-start acceptance run from a fresh checkout using documented local commands.
- Run representative element and structure workflows from UI input through calculation, visualization, persistence where implemented, and report export.
- Verify every visible design code and element type against its declared capability state.
- Resolve every deferred engineering phase by verifying it, intentionally excluding it from release scope, or consistently declaring its remaining capability UNVERIFIED / NOT IMPLEMENTED across product, UI, and reports.
- Prepare architecture, local development, calculation-engine, code-registry, validation, and known-limitations documentation.
- Prepare a release checklist covering tests, migrations, environment variables, backups, observability, security, and rollback requirements.
- Remove temporary debug code, stale generated files, dead UI controls, and contradictory documentation.

Exit gate: The candidate is reproducible locally, all supported workflows pass, documentation matches implementation, and the project is ready for an explicit deployment decision.

## P12 - Deployment Decision & Release Packaging

Time box: 47-48 hours  |  Initial status: HOLD

Objective: Decide where and how to publish only after all engineering and product gates are complete.

- Do not assume Railway remains the target. Compare deployment requirements against the completed architecture and select the hosting model only now.
- Define production topology for frontend, API, database, persistent/report storage, secrets, HTTPS, backups, logs, monitoring, and migrations.
- Create production-ready build artifacts/configuration without weakening the local development workflow.
- Prepare health checks, rollback procedure, environment configuration, database backup/restore procedure, and release verification steps.
- Perform deployment only after explicit approval; otherwise stop with a deployment-ready package and documented provider options.
- Before a deployment decision, confirm that no deferred engineering capability is presented as verified or silently counted toward a completed exit gate.
- After any deployment, run the same acceptance smoke tests against the deployed environment and record the release version.

Exit gate: A documented go/no-go decision exists. If approved, the release is deployed with rollback and verification controls; if not approved, the project remains safely runnable locally with a complete deployment package.

## 48-Hour Completion Criteria

- Clean local install/start/build is reproducible.
- API contracts and units are explicit and tested.
- The supported 2D structural solver scope passes analytical benchmarks.
- At least one concrete design path and one steel design path meet the verified-module evidence standard, or are clearly marked as not verified if evidence is incomplete.
- Every visible design code has an honest capability status and edition metadata.
- No placeholder or incomplete calculation can produce an authoritative SAFE verdict.
- Reports are traceable to server-side analysis runs and include engine/code metadata.
- The primary UI workflow is complete, professional, and does not expose nonfunctional features as finished.
- Automated tests and CI protect the validated calculations and build.
- Deployment was not touched before P12 and is subject to a final go/no-go decision.

## Required Phase Report Format

- Phase ID and final phase status.
- Summary of what was implemented.
- Exact files added, modified, deleted, or moved.
- Important technical decisions and why they were made.
- Engineering references/standard editions used for calculation changes.
- Tests and commands executed, with pass/fail results.
- New problems discovered during implementation.
- Known limitations or deferred work.
- Whether the phase is READY FOR REVIEW or BLOCKED.
- No commit or push unless explicitly instructed after review.

## Repository Roadmap Maintenance Rule

- The repository should contain a Markdown copy of this roadmap under docs/STRUCTICODE_48H_ENTERPRISE_ROADMAP.md.
- Codex should update the Master Execution Tracker and concise factual notes after each phase; it should not rewrite the roadmap scope without explicit instruction.
- After a phase reaches READY FOR REVIEW, implementation work should stop until the review outcome is provided.
- If review returns REWORK REQUIRED, the same phase remains active until it passes. The next phase must stay HOLD.
- PUSHED means the reviewed phase has actually been committed and pushed to the Git repository; it is not a synonym for implementation complete.

*Controlled working document - update the execution tracker after each phase*
