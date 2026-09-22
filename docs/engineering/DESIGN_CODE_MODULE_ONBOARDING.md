# Verified Design-Code Module Onboarding

## Contract

Use a stable family ID only for software routing. A verified module must identify an exact standard and edition separately, with the applicable jurisdiction, national annex or adoption where relevant. `VerifiedEvidence` and the lightweight `VerifiedDesignModule` protocol in `backend/api/domain/design_code_registry.py` define the registration contract. No dynamic plugin loader is needed.

The evidence record must include standard ID/title/edition, material type, bounded element and check scope, canonical input and result contracts, engineering engine ID/version, authoritative provision references, assumptions, applicability limits, independently checked benchmark IDs, and explicitly unsupported scope. A verified capability cannot be registered without this evidence and authoritative standard metadata.

## Required sequence

1. Select the exact governing standard, edition, printing, and jurisdiction or national annex. Record any local adoption and applicable errata.
2. Secure authorized access to authoritative source text and property data. Confirm that the actual provisions, tables, equations, definitions, and limits can be inspected.
3. Define a bounded element/check scope. List excluded limit states and inputs that cannot be evaluated.
4. Specify canonical units for every input, intermediate quantity, and output. Define conversion boundaries and dimension checks.
5. Implement an isolated engineering engine behind canonical input and result contracts. Keep its behavior separate from legacy compatibility handlers.
6. Map each implemented rule to the exact inspected provisions, including assumptions, applicability limits, and governing edition or annex. Do not infer references from handler comments or memory.
7. Add independent published/reference benchmarks. Record source identifiers, inputs, expected values, tolerances, and the reason each case is independent of the implementation.
8. Add boundary, invalid-input, unsupported-scope, unit-conversion, and failure tests. Verify that an omitted check cannot silently become PASS.
9. Register the bounded capability and `VerifiedEvidence` only after the evidence and tests exist. Keep unrelated family elements and material types `LEGACY_UNVERIFIED` or `NOT_IMPLEMENTED`.
10. Obtain independent engineering and code review of equations, metadata, scope, benchmark provenance, and API/report claims.
11. Only after that review may the exact bounded capability be marked `VERIFIED`; update client and report claims to match its limits.

## Deferred-source examples

P4 could not inspect the authorized ACI CODE-318-25 SI provisions needed for a verified concrete core. P5 could not inspect the exact applicable ANSI/AISC 360-22 provisions and errata or obtain authoritative section properties and independent examples for a verified steel core. Their existing software paths remain legacy/unverified, and their verification targets remain source blocked. Do not substitute another edition or treat a plausible calculation as evidence.

## Review and release

Reviewers must confirm that family labels and legacy claims never substitute for the evidence record. Release acceptance must separately decide whether any deferred capability is verified, excluded, or consistently presented as unverified/not implemented. Registry status, v1 API, UI, and reports must agree before a release decision.
