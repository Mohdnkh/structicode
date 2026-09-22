# Pre-P12 Release Checklist

This is a go/no-go checklist for P12. It is not a deployment procedure.

- [ ] Roadmap shows P0-P3 and P6-P10 pushed, P4/P5 `DEFERRED — SOURCE BLOCKED`, P11 reviewed, and P12 hold until approval.
- [ ] P4/P5 remain excluded from verified release scope; no ACI 318-25 or AISC 360-22 claim is made.
- [ ] Full backend, protected P3-P10 regressions, frontend tests, build, import, hygiene, migration, and whitespace checks pass.
- [ ] GitHub Actions is green on the exact release revision.
- [ ] Clean migration and rollback strategy are demonstrated.
- [ ] Production environment variables and a >=32-byte auth secret are managed safely.
- [ ] Dependency advisories have an explicit risk decision and maintenance owner.
- [ ] Capability matrix, engineering limitations, unit contract, and report trust language are current.
- [ ] Production database, backups, retention, and recovery objectives are selected.
- [ ] PDF/report storage and blob lifecycle are selected; local regenerated PDFs are not treated as durable storage.
- [ ] HTTPS, secret manager, observability, distributed rate limiting, multi-instance behavior, and tenant controls are verified.
- [ ] Smoke tests cover health, capabilities, anonymous analysis, project analysis, restart retrieval, cross-tenant denial, reports, English, Arabic/RTL, and responsive layouts.
- [ ] P12 records the final provider, cost, operational ownership, rollback plan, and release decision.
