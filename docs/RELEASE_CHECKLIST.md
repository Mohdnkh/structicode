# Pre-P12 Release Checklist

This is a go/no-go checklist for P12. It is not a deployment procedure.

- [x] Roadmap shows P0-P3 and P6-P11 pushed, P4/P5 `DEFERRED — SOURCE BLOCKED`, and P12 `READY FOR REVIEW` after package review.
- [x] P4/P5 remain excluded from verified release scope; no ACI 318-25 or AISC 360-22 claim is made.
- [x] Local backend, protected P3-P10 regressions, frontend tests, build, import, hygiene, migration, and whitespace checks pass.
- [ ] GitHub Actions is green on the exact release revision.
- [x] Clean migration and rollback strategy are documented; production execution remains pending.
- [ ] Production environment variables and a >=32-byte auth secret are managed safely.
- [ ] Dependency advisories have an explicit owner decision and maintenance owner. **UNRESOLVED — NO-GO.**
- [x] Capability matrix, engineering limitations, unit contract, and report trust language are current.
- [ ] Production database, backups, retention, and recovery objectives are selected. **UNRESOLVED — NO-GO.**
- [x] PDF/report storage and blob lifecycle are documented; local regenerated PDFs are not treated as durable storage.
- [x] HTTPS, secret manager, observability, distributed rate limiting, multi-instance behavior, and tenant-control requirements are documented. Provider verification and deployment remain pending.
- [ ] Smoke tests cover health, capabilities, anonymous analysis, project analysis, restart retrieval, cross-tenant denial, reports, English, Arabic/RTL, and responsive layouts.
- [x] P12 records provider options, rollback plan, owner decisions, and the `NO-GO` release decision.
