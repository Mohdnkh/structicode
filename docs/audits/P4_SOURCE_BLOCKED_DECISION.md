# P4 Source-Blocked Recovery Decision

## Decision and evidence

The planned P4 exit gate is an end-to-end VERIFIED ACI CODE-318-25 reinforced-concrete capability, initially focused on a reinforced-concrete beam. That gate remains unmet. No authorized copy of the applicable SI content of ACI CODE-318-25, or authorized ACI 318 PLUS access covering that edition, is currently available for checking the applicable provisions, equations, tables, limits, strength-reduction rules, and detailing requirements. No concrete capability is promoted to VERIFIED by this decision.

The fabricated reinforcement and misleading overall-status defects identified during P4 were contained in the safety remediation merged through PR #3. The merge is present on `main` at `995ceb65c80e2bc17887a3c08f68a129501cf439`. The historical [P4 safety remediation audit](P4_BLOCKED_SAFETY_REMEDIATION.md) retains the BLOCKED status recorded at that time. This decision updates the current workflow state to `DEFERRED — SOURCE BLOCKED`; it does not retrospectively change that audit or complete the verified concrete work.

## Continuation boundary

P5 steel work does not technically depend on ACI concrete provisions. It may be proposed after this documentation recovery is reviewed and merged, subject to its own authoritative steel sources, evidence, and phase approval. P5 remains HOLD until a separate instruction starts it. Independent phases may continue only if the blocker is external rather than an unresolved defect invalidating their calculations, known safety-critical misleading behavior has been contained, and their work does not rely on the missing verified concrete capability.

The deferred P4 exit gate remains open. Before P11/P12 completion, the deferred capability must be completed and verified, intentionally removed from release scope, or retained as explicitly UNVERIFIED / NOT IMPLEMENTED with consistent product, UI, and report claims. It cannot be counted as a verified release capability by silence or by progress in later phases.

## Restart condition

Resume verified P4 work only when authorized access to the applicable SI edition/content of ACI CODE-318-25, or authorized ACI 318 PLUS access covering that edition, allows the exact applicable provisions, equations, tables, limits, strength-reduction rules, and detailing requirements to be checked for the intended scope. Verified implementation, benchmark evidence, and exit-gate review remain separate future work.

This record changes documentation and workflow only. It contains no engineering calculation or deployment change.
