"""Small-displacement, linear elastic Euler-Bernoulli 2D frame solver.

Solver units: m, kN, kN/m, kN/m2, m2, m4. Positive member w acts
in local negative-y. End actions act on nodes; section moments are
positive in sagging.
"""

from dataclasses import dataclass
import math

import numpy as np

from .load_combination import LOAD_CASES, parse_combination


class SolverInputError(ValueError):
    code = "SOLVER_INPUT_INVALID"


class UnsupportedSlabError(SolverInputError):
    code = "NOT_IMPLEMENTED"


class StructureUnstableError(SolverInputError):
    code = "STRUCTURE_UNSTABLE"


class SolverNumericalError(RuntimeError):
    code = "SOLVER_NUMERICAL_ERROR"


def _finite(value, label):
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise SolverInputError(f"{label} must be finite") from exc
    if not math.isfinite(number):
        raise SolverInputError(f"{label} must be finite")
    return number


def _positive(value, label):
    number = _finite(value, label)
    if number <= 0:
        raise SolverInputError(f"{label} must be positive")
    return number


def _indexed(items, label):
    if not isinstance(items, list) or not items:
        raise SolverInputError(f"{label} must be a nonempty list")
    indexed = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip():
            raise SolverInputError(f"Every {label} entry needs a nonempty string ID")
        if item["id"] in indexed:
            raise SolverInputError(f"Duplicate {label} ID: {item['id']}")
        indexed[item["id"]] = item
    return indexed


@dataclass(frozen=True)
class MemberState:
    id: str
    dofs: tuple[int, ...]
    length: float
    e: float
    inertia: float
    transform: np.ndarray
    stiffness: np.ndarray
    loads: tuple[tuple[str, float], ...]

    def factored_load(self, factors):
        return sum(w * factors.get(case_id, 0.0) for case_id, w in self.loads)

    def equivalent_load(self, w):
        """Consistent external local nodal vector for a uniform local -y load."""
        length = self.length
        return np.array((0, -w*length/2, -w*length**2/12,
                         0, -w*length/2, w*length**2/12), dtype=float)


class StructureAnalyzer:
    def __init__(self, structure: dict):
        if not isinstance(structure, dict):
            raise SolverInputError("Structure must be a mapping")
        if structure.get("slabs"):
            raise UnsupportedSlabError("Slab load transfer to frame members is not implemented")
        units = structure.get("units")
        if units is not None and units != {"length": "m", "force": "kN", "modulus": "kN/m2"}:
            raise SolverInputError("Frame solver requires m, kN, and kN/m2 units")
        self.nodes = _indexed(structure.get("nodes"), "nodes")
        self.sections = _indexed(structure.get("sections"), "sections")
        self.materials = _indexed(structure.get("materials"), "materials")
        members = _indexed(structure.get("members"), "members")
        self.node_dofs = {node_id: (3*i, 3*i+1, 3*i+2)
                          for i, node_id in enumerate(self.nodes)}
        self.ndof = 3*len(self.nodes)
        for node_id, node in self.nodes.items():
            _finite(node.get("x"), f"node {node_id} x")
            _finite(node.get("y"), f"node {node_id} y")
            if node.get("support", "free") not in {"free", "pin", "roller", "fix", "fixed"}:
                raise SolverInputError(f"Unsupported support at node {node_id}")
        self.member_states = tuple(self._make_member(member) for member in members.values())
        loads = structure.get("loads", {})
        if not isinstance(loads, dict):
            raise SolverInputError("loads must be a mapping")
        combinations = loads.get("combinations")
        if combinations is None:
            combinations = [{"id": "LC1", "name": "1.0D", "expr": "1.0D"}]
        if not isinstance(combinations, list) or not combinations:
            raise SolverInputError("At least one load combination is required")
        self.combinations = []
        combo_ids = set()
        for combo in combinations:
            if not isinstance(combo, dict) or not isinstance(combo.get("id"), str) or not combo["id"].strip():
                raise SolverInputError("Every combination requires an ID")
            if combo["id"] in combo_ids:
                raise SolverInputError(f"Duplicate combination ID: {combo['id']}")
            combo_ids.add(combo["id"])
            try:
                factors = parse_combination(combo.get("expr"))
            except ValueError as exc:
                raise SolverInputError(f"Invalid combination {combo['id']}: {exc}") from exc
            self.combinations.append((combo["id"], combo.get("name", combo["id"]), combo["expr"], factors))

    def _make_member(self, member):
        member_id = member["id"]
        n1_id, n2_id = member.get("n1"), member.get("n2")
        if not isinstance(n1_id, str) or not isinstance(n2_id, str):
            raise SolverInputError(f"Member {member_id} requires string node references")
        if n1_id not in self.nodes or n2_id not in self.nodes:
            raise SolverInputError(f"Member {member_id} references an unknown node")
        section_id, material_id = member.get("sectionId"), member.get("materialId")
        if not isinstance(section_id, str) or not isinstance(material_id, str):
            raise SolverInputError(f"Member {member_id} requires string section and material references")
        if section_id not in self.sections or material_id not in self.materials:
            raise SolverInputError(f"Member {member_id} references an unknown section or material")
        n1, n2 = self.nodes[n1_id], self.nodes[n2_id]
        dx, dy = float(n2["x"])-float(n1["x"]), float(n2["y"])-float(n1["y"])
        length = math.hypot(dx, dy)
        if not math.isfinite(length) or length <= 0:
            raise SolverInputError(f"Member {member_id} has invalid or zero length")
        c, s = dx/length, dy/length
        params = self.sections[section_id].get("params")
        if not isinstance(params, dict):
            raise SolverInputError(f"Section {section_id} requires params")
        if self.sections[section_id].get("shape", "rectRC") != "rectRC":
            raise SolverInputError(f"Section {section_id} must be rectangular rectRC")
        if "I" in params or "inertia" in params:
            raise SolverInputError(f"Explicit inertia for section {section_id} is not supported")
        b = _positive(params.get("bw"), f"section {section_id} width")
        h = _positive(params.get("h"), f"section {section_id} depth")
        a = _positive(params.get("A", b*h), f"section {section_id} area")
        inertia = _positive(b*h**3/12, f"section {section_id} inertia")
        e = _positive(self.materials[material_id].get("E"), f"material {material_id} E")
        ea, ei, l2, l3 = e*a, e*inertia, length**2, length**3
        k = np.array([
            [ea/length, 0, 0, -ea/length, 0, 0],
            [0, 12*ei/l3, 6*ei/l2, 0, -12*ei/l3, 6*ei/l2],
            [0, 6*ei/l2, 4*ei/length, 0, -6*ei/l2, 2*ei/length],
            [-ea/length, 0, 0, ea/length, 0, 0],
            [0, -12*ei/l3, -6*ei/l2, 0, 12*ei/l3, -6*ei/l2],
            [0, 6*ei/l2, 2*ei/length, 0, -6*ei/l2, 4*ei/length],
        ], dtype=float)
        t = np.array([
            [c, s, 0, 0, 0, 0], [-s, c, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
            [0, 0, 0, c, s, 0], [0, 0, 0, -s, c, 0], [0, 0, 0, 0, 0, 1],
        ], dtype=float)
        if not np.isfinite(k).all():
            raise SolverInputError(f"Member {member_id} stiffness is non-finite")
        raw_loads = member.get("loads", [])
        if not isinstance(raw_loads, list):
            raise SolverInputError(f"Member {member_id} loads must be a list")
        member_loads = []
        for load in raw_loads:
            if not isinstance(load, dict) or load.get("type") not in LOAD_CASES:
                raise SolverInputError(f"Member {member_id} has an unsupported load type")
            member_loads.append((load["type"], _finite(load.get("w"), f"member {member_id} w")))
        return MemberState(member_id, self.node_dofs[n1_id]+self.node_dofs[n2_id],
                           length, e, inertia, t, k, tuple(member_loads))

    def _get_support_dofs(self):
        constrained = set()
        for node_id, node in self.nodes.items():
            dofs = self.node_dofs[node_id]
            support = node.get("support", "free")
            if support in {"fix", "fixed"}:
                constrained.update(dofs)
            elif support == "pin":
                constrained.update(dofs[:2])
            elif support == "roller":
                constrained.add(dofs[1])
        return sorted(constrained)

    def _parse_load_combination(self, expr):
        return parse_combination(expr)

    def analyze_combinations(self):
        return {combo_id: {"name": name, "expr": expression, **self._analyze_single_case(factors)}
                for combo_id, name, expression, factors in self.combinations}

    def _analyze_single_case(self, factors):
        stiffness = np.zeros((self.ndof, self.ndof))
        force = np.zeros(self.ndof)
        factored_loads = {}
        for member in self.member_states:
            dofs = list(member.dofs)
            stiffness[np.ix_(dofs, dofs)] += member.transform.T @ member.stiffness @ member.transform
            w = member.factored_load(factors)
            factored_loads[member.id] = w
            force[dofs] += member.transform.T @ member.equivalent_load(w)
        if not np.isfinite(stiffness).all() or not np.isfinite(force).all():
            raise SolverNumericalError("Frame assembly produced non-finite values")
        constrained = self._get_support_dofs()
        constrained_set = set(constrained)
        free = [index for index in range(self.ndof) if index not in constrained_set]
        displacement = np.zeros(self.ndof)
        warnings = []
        if free:
            kff = stiffness[np.ix_(free, free)]
            diagonal = np.diag(kff)
            if np.any(diagonal <= 0) or not np.isfinite(diagonal).all():
                raise StructureUnstableError("Frame has disconnected free degrees of freedom")
            scaling = 1/np.sqrt(diagonal)
            scaled = scaling[:, None]*kff*scaling[None, :]
            try:
                singular = np.linalg.svd(scaled, compute_uv=False)
            except np.linalg.LinAlgError as exc:
                raise SolverNumericalError("Frame stability assessment failed") from exc
            if not np.isfinite(singular).all() or singular[0] <= 0:
                raise StructureUnstableError("Frame has no stable free stiffness")
            if singular[-1] <= len(free)*np.finfo(float).eps*singular[0]:
                raise StructureUnstableError("Frame is unstable or has a mechanism")
            if singular[0]/singular[-1] > 1/math.sqrt(np.finfo(float).eps):
                warnings.append("Free stiffness is ill-conditioned after diagonal scaling; results may lose precision.")
            try:
                displacement[free] = np.linalg.solve(kff, force[free])
            except np.linalg.LinAlgError as exc:
                raise StructureUnstableError("Frame stiffness cannot be solved") from exc
        if not np.isfinite(displacement).all():
            raise SolverNumericalError("Frame displacements are non-finite")
        residual = stiffness @ displacement-force
        if not np.isfinite(residual).all():
            raise SolverNumericalError("Frame reactions are non-finite")
        reactions = {}
        for node_id, dofs in self.node_dofs.items():
            if any(dof in constrained_set for dof in dofs):
                reactions[node_id] = {
                    "rx": float(residual[dofs[0]]) if dofs[0] in constrained_set else 0.0,
                    "ry": float(residual[dofs[1]]) if dofs[1] in constrained_set else 0.0,
                    "mz": float(residual[dofs[2]]) if dofs[2] in constrained_set else 0.0,
                }
        member_forces = {member.id: self._recover_forces(member, displacement, factored_loads[member.id])
                         for member in self.member_states}
        return {
            "displacements": {node_id: {"ux": float(displacement[dofs[0]]),
                                        "uy": float(displacement[dofs[1]]),
                                        "rz": float(displacement[dofs[2]])}
                              for node_id, dofs in self.node_dofs.items()},
            "member_forces": member_forces, "reactions": reactions, "warnings": warnings,
        }

    @staticmethod
    def _recover_forces(member, displacement, w):
        local_u = member.transform @ displacement[list(member.dofs)]
        ends = member.stiffness @ local_u-member.equivalent_load(w)
        length = member.length
        axial, shear_0, moment_0 = -ends[0], ends[1], -ends[2]
        def shear(x):
            return shear_0-w*x
        def moment(x):
            return moment_0+shear_0*x-w*x*x/2
        points = [0.0, length]
        if w:
            stationary = shear_0/w
            if 0 < stationary < length:
                points.append(stationary)
        governing_x = max(points, key=lambda x: abs(moment(x)))
        shear_x = max((0.0, length), key=lambda x: abs(shear(x)))
        mid = length/2
        hermite = np.array((0.5, length/8, 0.5, -length/8))
        midspan = (hermite @ local_u[[1, 2, 4, 5]]
                   - w*mid**2*(length-mid)**2/(24*member.e*member.inertia))
        if not np.isfinite((axial, shear(shear_x), moment(governing_x), midspan, *ends)).all():
            raise SolverNumericalError(f"Member {member.id} recovery is non-finite")
        return {
            "Nmax": float(axial), "Vmax": float(shear(shear_x)),
            "Mmax": float(moment(governing_x)), "Mmax_x": float(governing_x),
            "midspan_local_y_displacement": float(midspan),
            "applied_uniform_load": float(w),
            "end_1": {"axial": float(ends[0]), "shear": float(ends[1]), "moment": float(ends[2])},
            "end_2": {"axial": float(ends[3]), "shear": float(ends[4]), "moment": float(ends[5])},
        }
