# Known Engineering Limitations

This document describes factual release-candidate boundaries. Passing the P10 QA gate does not verify engineering design calculations.

- P4 concrete verification remains deferred because authorized ACI CODE-318-25 source access was unavailable.
- P5 steel verification remains deferred because an authoritative steel design source was unavailable.
- Legacy concrete, steel, footing, slab, staircase, and seismic results remain `UNVERIFIED` unless a later phase explicitly establishes verification evidence.
- P3 covers bounded two-dimensional linear-elastic frame mechanics only.
- Legacy code-specific load-factor sets and design-code formulas are not independently verified.
- The v1 seismic path is not implemented as a verified design workflow.
- Frame slab-load transfer remains unsupported in the v1 structure contract.
- Report generation creates traceable output but does not create engineering verification.
- Project persistence and authorization do not create engineering verification.
