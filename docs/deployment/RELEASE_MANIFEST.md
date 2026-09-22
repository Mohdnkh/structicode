# Release Manifest

| Field | P12 proposal |
| --- | --- |
| Proposed release identifier | `p12-493db3fa` |
| Source Git commit | `ceefb11a91fc64ab2c55ed9dd9dfb8dab4105918` (main base) |
| P12 commit SHA | 493db3fa (implementation commit; verify full SHA with git rev-parse HEAD) |
| Python runtime | Python 3.12 |
| Node build runtime | Node.js 20 in the container build stage |
| Database migration head | `20260922_p9_initial` |
| Analysis-run schema | `analysis_run_v1` |
| Report schema | `structicode_report_v1` |
| Engineering release scope | P3 bounded mechanics; P4/P5 source blocked; legacy design unverified |
| Container artifact | Provider-neutral multi-stage Docker image; no image pushed |
| Deployment decision | `NO-GO` |

No registry digest, Git tag, or GitHub Release is created by P12.
