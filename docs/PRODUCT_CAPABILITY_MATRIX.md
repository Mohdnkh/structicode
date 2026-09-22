# Product Capability Matrix

This table is a documentation view of `backend/api/domain/design_code_registry.py`. The automated P11 acceptance test checks family IDs and representative statuses against the registry and the `/api/v1/capabilities` response. `LEGACY` means `LEGACY_UNVERIFIED`; `REVIEW` means `ENGINEERING_REVIEW_REQUIRED`; `N/I` means `NOT_IMPLEMENTED`; `SOURCE BLOCKED` identifies a future verification target.

| Family ID | Display name | Jurisdiction | Metadata confidence | Concrete elements | Steel elements | Structure analysis | Structure design | Load combination | Seismic | Source-blocked target |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `aci` | ACI family | United States | LEGACY_CLAIM | LEGACY | LEGACY | REVIEW | LEGACY | LEGACY | LEGACY (v1 false) | `aci_318_25` |
| `bs` | British Standards family | United Kingdom | LEGACY_CLAIM | LEGACY | LEGACY | REVIEW | LEGACY | LEGACY | LEGACY (v1 false) | — |
| `eurocode` | Eurocode family | Europe; national annex unspecified | LEGACY_CLAIM | LEGACY | LEGACY | REVIEW | LEGACY | LEGACY | LEGACY (v1 false) | — |
| `as` | Australian Standards family | Australia | LEGACY_CLAIM | LEGACY | LEGACY | REVIEW | LEGACY | LEGACY | LEGACY (v1 false) | — |
| `csa` | Canadian Standards family | Canada | LEGACY_CLAIM | LEGACY | LEGACY | REVIEW | LEGACY | LEGACY | LEGACY (v1 false) | — |
| `is` | Indian Standards family | India | LEGACY_CLAIM | LEGACY | N/I | REVIEW | LEGACY | LEGACY | LEGACY (v1 false) | — |
| `jordan` | Jordanian Code family | Jordan | LEGACY_CLAIM | LEGACY | LEGACY | REVIEW | LEGACY | LEGACY | LEGACY (v1 false) | — |
| `egypt` | Egyptian Code family | Egypt | LEGACY_CLAIM | LEGACY | LEGACY | REVIEW | LEGACY | LEGACY | LEGACY (v1 false) | — |
| `saudi` | Saudi Building Code family | Saudi Arabia | LEGACY_CLAIM | LEGACY | LEGACY | REVIEW | LEGACY | LEGACY | LEGACY (v1 false) | — |
| `uae` | UAE Building Code family | United Arab Emirates | LEGACY_CLAIM | LEGACY | LEGACY | REVIEW | LEGACY | LEGACY | LEGACY (v1 false) | — |
| `turkey` | Turkish Code family | Turkey | LEGACY_CLAIM | LEGACY | LEGACY | REVIEW | LEGACY | LEGACY | LEGACY (v1 false) | — |
| `steel` | Generic steel legacy family | Unspecified | UNKNOWN | N/I | LEGACY | N/I | N/I | N/I | N/I | `aisc_360_22` |

Every family also contains explicit per-element records for all seven element IDs. The UI reads those records rather than maintaining a second matrix. Family presence, a legacy claim, or a successful transport response does not establish code compliance.
