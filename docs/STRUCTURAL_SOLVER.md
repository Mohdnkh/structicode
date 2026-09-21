# 2D structural solver: P3 supported scope

The frame core solves linear elastic, small-displacement, planar Euler-Bernoulli members. Its analytical benchmarks exercise equilibrium, translations, rotations, member end actions, and uniform-load moment extrema. This evidence applies to the solver core within the scope below. The overall structure API remains `UNVERIFIED` because legacy design checks and the design-code combination sets have not been independently verified.

## Units and section properties

| Quantity | Solver-local unit | Public v1 canonical unit |
| --- | --- | --- |
| Coordinates, member length, displacement | m | mm |
| Force and axial/shear action | kN | N |
| Uniform member line load | kN/m | N/mm |
| Elastic modulus | kN/m² | MPa |
| Area | m² | mm² |
| Second moment of area | m⁴ | mm⁴ |
| Bending or reaction moment | kN·m | N·mm |
| Rotation | rad | rad |

The v1 adapter converts the public input to solver-local units before analysis. A direct solver input may declare `{"length":"m","force":"kN","modulus":"kN/m2"}`; any other declared unit set is rejected. For a rectangular `rectRC` section, `A = b h` unless an explicit positive area is supplied, and `I = b h³/12` about the local bending axis. Explicit inertia is rejected because the existing v1 contract does not support it. Member stiffness uses `EA` and `EI` in these units.

## Kinematics, axes, loads, and signs

Each node has global `ux`, `uy`, and counterclockwise `rz`. Global positive x is right and positive y is up. The member local x-axis runs from `n1` to `n2`; local y is 90 degrees counterclockwise from local x. The orthogonal transformation `u_local = T u_global` maps both nodal translations and rotations into the member frame. Positive rotation is counterclockwise about positive global z.

A positive member `w` acts uniformly in **local negative-y**, for every member orientation. It is not interpreted as global gravity. The only supported member load is a full-length uniform transverse line load. Its local external consistent nodal vector, in `[u1,v1,r1,u2,v2,r2]` order, is:

```text
p_local = [0, -wL/2, -wL²/12, 0, -wL/2, +wL²/12]
```

The global external force vector receives `Tᵀ p_local`. The load-vector components sum to the total applied force and moment. Positive nodal translations and rotation follow the global axes above. Reaction values are `R = K U - F`, meaning support forces and moments acting on the model in the positive global directions; only constrained DOFs are reported. A pin constrains `ux,uy`; a roller constrains `uy`; `fix` or `fixed` constrains all three; `free` constrains none. Unsupported support labels are rejected.

Reported member `end_1` and `end_2` values are local element actions **on the nodes**, `f_local = k_local u_local - p_local`. Their axial, shear, and moment signs follow positive local x, positive local y, and counterclockwise local z at each end. Internal section actions use tension-positive axial force, local positive-y shear at the left cut, and positive sagging moment. Consequently an upward fixed support moment on a downward-loaded cantilever appears as a negative hogging internal moment at its root.

## Load combinations and member response

The combination parser accepts finite decimal coefficients for D, L, W, S, and E; whitespace and additive or subtractive terms are supported. Duplicate case factors add. Malformed expressions and unsupported case letters are rejected. A case absent from an expression has factor **zero**. For example, `1.4D` does not apply a member's live load. The existing code-specific combination coefficient sets are unchanged and remain unverified.

For each member, one validated state holds geometry, transformation, local stiffness, and raw loads. That state is used in global assembly and recovery. The solver evaluates:

```text
K = sum(Tᵀ k_local T)
F = sum(Tᵀ p_local)
U_free = solve(K_free, F_free)
R = K U - F
f_end_local = k_local (T U_member) - p_local
```

For a full-span uniform transverse load, with `x` measured from `n1`, internal actions are `N(x) = -f_end1,axial`, `V(x) = f_end1,shear - w x`, and `M(x) = -f_end1,moment + f_end1,shear x - w x²/2`. `Nmax`, `Vmax`, and `Mmax` retain legacy names but now contain the signed value with largest absolute magnitude over the supported member length. The candidate moment locations are both ends and the stationary point `V(x)=0` when it lies inside the member; `Mmax_x` reports its location in metres. This convention should not be read as a design-code capacity verdict.

The response also includes both local end actions and a midspan local-y displacement. Midspan displacement uses cubic Hermite interpolation of the member DOFs plus the exact Euler-Bernoulli uniform-load bubble term `-w x²(L-x)²/(24EI)`. This permits direct comparison with the simply supported beam closed form.

The v1 structure response converts reaction fields to `rx_n`, `ry_n`, `mz_n_mm` and provides explicit canonical units for member end actions, governing moment location, applied uniform load, and midspan displacement. Legacy raw result keys remain available for the existing design handlers, whose outputs remain `UNVERIFIED`.

## Stability and unsupported inputs

The solver validates unique IDs, references, finite geometry and loads, nonzero member length, supported sections/supports/load cases, positive `E`, `A`, and `I`, and nonempty valid combinations. It checks free DOFs before solution. Diagonal scaling of the free stiffness removes unit-driven diagonal magnitude differences, then singular values detect rank loss using `n ε σ_max`. A mechanism raises `STRUCTURE_UNSTABLE`; v1 returns structured HTTP 422. A condition number above `1/sqrt(ε)` after scaling produces a precision warning. NumPy solve failures and non-finite outputs are handled without exposing a raw matrix exception through v1.

Slab geometry is explicitly unsupported in the frame path. Direct solver use raises `NOT_IMPLEMENTED`; v1 returns structured HTTP 400. No slab load is distributed equally among members.

## Analytical benchmarks and tolerances

The benchmark suite uses `E = 25,000,000 kN/m²`, `b = 0.3 m`, `h = 0.5 m`, `A = 0.15 m²`, `I = 0.003125 m⁴`, `EI = 78,125 kN·m²`, and `w = 10 kN/m`.

- Cantilever of length `L=4 m`: vertical reaction `wL`, root reaction moment `wL²/2`, tip displacement `-wL⁴/(8EI)`, tip rotation `-wL³/(6EI)`.
- Pin-roller beam of length `L=6 m`: each vertical reaction `wL/2`, sagging maximum `wL²/8` at `L/2`, midspan displacement `-5wL⁴/(384EI)`.
- Fixed-base rigid frame with `H=3 m` column and `L=4 m` horizontal cantilever beam: base vertical reaction `wL`, base moment `wL²/2`, top rotation `-MH/(EI)`, top horizontal displacement `MH²/(2EI)`, top vertical displacement `-wLH/(EA)`, beam tip vertical displacement `u_y,top + L θ_top - wL⁴/(8EI)`.

Benchmark assertions use relative tolerance `1e-11` for nonzero closed-form quantities and absolute tolerance `1e-9` in solver units for expected-zero actions and global equilibrium. These tolerances are for deterministic, small textbook models, not a general conditioning guarantee for arbitrary frames. The full measured values and errors are in [P3_SOLVER_REPORT.md](audits/P3_SOLVER_REPORT.md).

## Excluded features

The solver does not implement nonlinear material or geometric behavior, second-order/P-Delta effects, Timoshenko shear deformation, plastic hinges, dynamic or seismic analysis, member releases or hinges, variable or partial-span distributed loads, nodal or member point loads, temperature loads, support settlements, 3D behavior, tributary slab loading, or design-code verification. It does not validate construction details, connection behavior, or geotechnical response. A zero-result unloaded combination does not establish structural adequacy.
