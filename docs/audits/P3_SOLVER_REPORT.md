# P3 structural solver audit and benchmark report

## Repository and scope

- Base `main` SHA: `6be04153450ae2ff5a590b4983d4e93f45afeb57`.
- Phase branch: `codex/p3-structural-solver`, created directly from synchronized `main` in the canonical workspace.
- Scope: deterministic, linear-elastic, small-displacement Euler-Bernoulli 2D frame assembly, support reactions, uniform transverse-load recovery, and benchmark evidence. P4 and deployment were not started.
- Public structure response status remains `UNVERIFIED`: legacy design handlers and design-code combination sets were not independently verified.

## Confirmed defects and corrections

| Previous behavior | P3 correction |
| --- | --- |
| An omitted load case inherited factor 1.0 during member assembly and in `combine_loads`. | Missing case factors are 0.0. A dead-plus-live member under `1.4D` applies only `1.4 × dead`. |
| Combination parsing silently accepted malformed input or discarded unknown cases. | Decimal D/L/W/S/E terms, spaces, signed terms, and duplicate cases are handled deterministically; malformed expressions raise an input error. |
| The member load vector sign was undocumented and inconsistent with force recovery. | Positive `w` is local negative-y; the single consistent external nodal vector is used for assembly and subtracted in recovery. |
| Force recovery reported only `k_local u_local` at end 1 and labeled it as maxima. | Both end actions use `k_local u_local - p_local`; governing signed axial, shear, and moment values and governing moment location are evaluated analytically for full-span uniform load. |
| The solver lacked support reactions. | `R=KU-F` returns only constrained DOFs in kN/kN/kN·m; v1 exposes N/N/N·mm typed fields. |
| A mechanism surfaced as a raw NumPy singular-matrix failure. | Free stiffness is diagonal-scaled and checked by singular values; `STRUCTURE_UNSTABLE` maps to structured HTTP 422. Ill-conditioned solvable systems add a warning. |
| Slab weight was divided equally among every member, regardless of tributary geometry. | Slab geometry raises `NOT_IMPLEMENTED` directly and returns structured HTTP 400 through v1. The equal-distribution path is removed. |

## Solver contract and architecture

Solver-local units are m, kN, kN/m, kN/m², m², and m⁴; displacement is m, rotation rad, and moment kN·m. P2 converts the public N-mm-MPa structure input before solver entry. Rectangular properties are `A=bh` or explicit positive `A`, and `I=bh³/12`. Explicit inertia is rejected. `MemberState` builds one geometry/transformation/stiffness/load state for assembly and recovery, eliminating duplicated member formulas.

Global positive x/y are right/up; local x goes from end 1 to end 2 and local y is counterclockwise from local x. Positive `w` acts local negative-y, not necessarily global down. Positive end actions act on nodes in local positive x/y and counterclockwise z. Reaction signs are global support actions on the model. Internal moment is positive sagging. See [STRUCTURAL_SOLVER.md](../STRUCTURAL_SOLVER.md) for equations and complete conventions.

The global system is `K U = F` on free DOFs. The consistent local external vector is `[0,-wL/2,-wL²/12,0,-wL/2,+wL²/12]`. Member section functions are `N=-f1x`, `V=f1y-wx`, and `M=-f1m+f1y x-wx²/2`. Reaction and member outputs are checked for finiteness. The new explicit solver exceptions are `SolverInputError`, `StructureUnstableError`, `UnsupportedSlabError`, and `SolverNumericalError`.

## Analytical benchmarks

All three benchmarks use `E=25,000,000 kN/m²`, `b=0.3 m`, `h=0.5 m`, `A=0.15 m²`, `I=0.003125 m⁴`, `EI=78,125 kN·m²`, and `w=10 kN/m` in local negative-y. Error is `|solver - closed form|`. For nonzero values, assertions use relative tolerance `1e-11`; expected-zero actions and equilibrium use absolute tolerance `1e-9` in solver units. These tight tolerances apply to these small, well-conditioned textbook models.

### Cantilever beam, L = 4 m

| Quantity | Closed form | Solver | Absolute error |
| --- | ---: | ---: | ---: |
| Fixed vertical reaction, `wL` (kN) | 40 | 40 | 0 |
| Fixed reaction moment, `wL²/2` (kN·m) | 80 | 80 | 0 |
| Tip vertical displacement, `-wL⁴/(8EI)` (m) | -0.004096 | -0.004096 | 0 |
| Tip rotation, `-wL³/(6EI)` (rad) | -0.0013653333333333333 | -0.0013653333333333332 | < 3e-19 |
| Governing internal moment at x=0 (kN·m) | -80 | -80 | 0 |
| End 1 shear / moment (kN / kN·m) | 40 / 80 | 40 / 80 | 0 / 0 |
| End 2 shear / moment (kN / kN·m) | 0 / 0 | -3.55e-15 / 3.55e-15 | < 4e-15 each |

Vertical and moment equilibrium residuals are zero at displayed precision.

### Simply supported beam, L = 6 m

| Quantity | Closed form | Solver | Absolute error |
| --- | ---: | ---: | ---: |
| Pin vertical reaction, `wL/2` (kN) | 30 | 30 | 0 |
| Roller vertical reaction, `wL/2` (kN) | 30 | 30 | 0 |
| Max sagging moment, `wL²/8` (kN·m) | 45 | 45 | 0 |
| Max moment location, `L/2` (m) | 3 | 3 | 0 |
| Midspan local-y displacement, `-5wL⁴/(384EI)` (m) | -0.00216 | -0.00216 | 0 |
| End 1 / end 2 moments (kN·m) | 0 / 0 | -3.55e-15 / 3.55e-15 | < 4e-15 each |

Vertical and global moment equilibrium residuals are zero at displayed precision. The midspan displacement uses Hermite interpolation plus the exact uniform-load bubble.

### Fixed-base rigid frame, column H = 3 m, cantilever beam L = 4 m

The fixed-base vertical column supports a horizontal loaded beam at its top. Closed-form base moment is `M=wL²/2=80 kN·m`. Top-joint rotation is `-MH/(EI)`; its horizontal translation is `MH²/(2EI)`; axial shortening is `-wLH/(EA)`. Beam-tip vertical translation is top vertical translation plus `L × top rotation` plus the beam's cantilever deflection.

| Quantity | Closed form | Solver | Absolute error |
| --- | ---: | ---: | ---: |
| Base vertical reaction (kN) | 40 | 40.000000000000014 | < 1.5e-14 |
| Base moment (kN·m) | 80 | 80.00000000000023 | < 2.3e-13 |
| Top-joint rotation (rad) | -0.003072 | -0.0030720000000000035 | < 4e-18 |
| Top-joint horizontal translation (m) | 0.004608 | 0.004608000000000008 | < 9e-18 |
| Top-joint axial shortening (m) | -0.000032 | -0.00003200000000000001 | < 2e-20 |
| Beam-tip vertical translation (m) | -0.016416 | -0.016416000000000007 | < 8e-18 |
| Beam end 1 shear (kN) | 40 | 40 | 0 |
| Beam end 1 moment (kN·m) | 80 | 79.99999999999996 | < 5e-14 |
| Column end 2 moment (kN·m) | -80 | -79.99999999999997 | < 3e-14 |

The horizontal base reaction is `-5.68e-14 kN` against zero expected. Vertical and moment equilibrium residuals are below `3e-13` in solver units. The benchmark directly tests a coupled frame joint, not just isolated beams.

## Regressions and API behavior

- A `1.4D` cantilever with dead `10 kN/m` and live `100 kN/m` produces `14 kN/m` applied load and `56 kN` vertical reaction; the live contribution is zero. `combine_loads({"dead":10,"live":100},{"dead":1.4})` returns 14.
- The consistent nodal vector has `ΣFy=-wL` and `ΣM=-wL²/2`. A fixed-fixed beam has zero displacement but nonzero recovered end actions `V=wL/2`, `M=±wL²/12`, proving fixed-end load effects participate in recovery.
- A rotated vertical cantilever proves positive `w` follows local negative-y, producing a horizontal global load and reaction. Halving explicit area doubles the rigid-frame column's axial shortening.
- Direct mechanism input raises `StructureUnstableError`; v1 returns HTTP 422 with `STRUCTURE_UNSTABLE` and `NOT_EVALUATED`. Direct slab input raises `UnsupportedSlabError`; v1 returns HTTP 400 with `NOT_IMPLEMENTED`. No equal-member distribution occurs.
- Direct solver validation tests cover duplicate node/member IDs, missing references, zero length, invalid support, nonpositive E/A, unsupported explicit I, non-finite load, and wrong unit declaration.
- Stable v1 HTTP response includes typed canonical reactions, end actions, governing moment location, displacements, and overall `UNVERIFIED` status. Health returns HTTP 200.

## Validation commands and results

| Command | Working directory | Result |
| --- | --- | --- |
| `.venv\Scripts\python.exe -m pytest backend/tests -q` | Repository root | 154 passed, 0 failed after final solver tests. |
| `node --test frontend/tests/api-adapters.test.mjs` | Repository root | 3 passed, 0 failed; Node reports an existing module-type warning. |
| `npm run build` | Repository root | Vite 5.4.21, 469 modules transformed, output `frontend/dist`; existing Vite CJS API deprecation warning. |
| `npm run verify:backend` with repository `.venv\Scripts` first on `PATH` | Repository root | Passed. Without the activated virtual environment it used system Python and failed to import installed `fpdf`; no project files were changed to bypass this local environment requirement. |
| `git diff --check` | Repository root | Passed. |

The final command evidence, status, source-scope review, and pull request details are recorded in the P3 execution report. Generated `frontend/dist` and Python caches are ignored and are not staged.

## Known limitations and deferred work

The solver has no nodal point-load input, so a separate axial point-load benchmark is outside this contract; axial shortening is instead independently tested in the rigid frame. It lacks nonlinear or second-order effects, dynamic/seismic analysis, member releases, varying or partial-span loads, point loads, temperature loads, support settlement, 3D behavior, tributary slab loading, and design-code verification. Its rank and conditioning criterion identifies numerical rank loss but does not certify every near-mechanism or every large model. The existing generated design-code combination coefficients remain unverified. Legacy structure design verdicts and reports remain outside P3 verification and must not be treated as authoritative.

No concrete design formula, steel design formula, or design-code coefficient was modified in P3. Dockerfile, `.dockerignore`, and `railway.json` were untouched. There was no Railway action, deployment, hosting change, or production operation.
