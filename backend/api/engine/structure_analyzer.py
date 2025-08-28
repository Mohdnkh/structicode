import numpy as np

# ================================
# Structure Analyzer (2D Frame v2) + Load Combinations
# ================================

class StructureAnalyzer:
    def __init__(self, structure: dict):
        self.structure = structure
        self.nodes = {n["id"]: n for n in structure["nodes"]}
        self.members = structure["members"]
        self.slabs = structure.get("slabs", [])
        self.sections = {s["id"]: s for s in structure["sections"]}
        self.materials = {m["id"]: m for m in structure["materials"]}
        self.loads = structure.get("loads", {})

        # degrees of freedom per node (ux, uy, rotation)
        self.dofs_per_node = 3
        self.ndof = len(self.nodes) * self.dofs_per_node

        # mapping node -> dof indices
        self.node_dofs = {
            nid: [i*self.dofs_per_node, i*self.dofs_per_node+1, i*self.dofs_per_node+2]
            for i, nid in enumerate(self.nodes.keys())
        }

    # ================================
    # Run All Load Combinations
    # ================================
    def analyze_combinations(self):
        """
        بيرجع النتائج لكل Combination (D, L, E ...)
        """
        results = {}
        combos = self.loads.get("combinations", [{"id":"LC1","name":"1.0D","expr":"1.0D"}])

        for combo in combos:
            combo_id, expr = combo["id"], combo["expr"]

            # scale loads بناءً على التعبير (ex: 1.2D+1.6L)
            load_factors = self._parse_load_combination(expr)

            res = self._analyze_single_case(load_factors)
            results[combo_id] = {
                "name": combo["name"],
                "expr": expr,
                "displacements": res["displacements"],
                "member_forces": res["member_forces"]
            }

        return results

    # ================================
    # Analyze Single Load Case
    # ================================
    def _analyze_single_case(self, load_factors: dict):
        # 1. Global stiffness matrix
        K = np.zeros((self.ndof, self.ndof))
        F = np.zeros(self.ndof)

        # 2. Assemble members
        for member in self.members:
            self._assemble_member(K, F, member, load_factors)

        # 3. Slab loads -> distribute to beams
        for slab in self.slabs:
            self._distribute_slab_load(F, slab, load_factors)

        # 4. Apply supports
        fixed_dofs = self._get_support_dofs()
        free_dofs = [i for i in range(self.ndof) if i not in fixed_dofs]

        # 5. Solve displacements
        Kff = K[np.ix_(free_dofs, free_dofs)]
        Ff = F[free_dofs]
        Uf = np.linalg.solve(Kff, Ff)

        # build full U vector
        U = np.zeros(self.ndof)
        for i, dof in enumerate(free_dofs):
            U[dof] = Uf[i]

        # 6. Recover forces in members
        member_forces = {}
        for member in self.members:
            member_forces[member["id"]] = self._recover_forces(member, U)

        return {
            "displacements": self._format_displacements(U),
            "member_forces": member_forces,
        }

    # ================================
    # Helpers
    # ================================
    def _assemble_member(self, K, F, member, load_factors):
        n1 = self.nodes[member["n1"]]
        n2 = self.nodes[member["n2"]]

        x1, y1 = n1["x"], n1["y"]
        x2, y2 = n2["x"], n2["y"]

        L = np.sqrt((x2-x1)**2 + (y2-y1)**2)
        c, s = (x2-x1)/L, (y2-y1)/L

        sec = self.sections[member["sectionId"]]
        mat = self.materials[member["materialId"]]

        E = mat["E"]
        A = sec["params"].get("A", sec["params"]["bw"]*sec["params"]["h"])
        I = (sec["params"]["bw"]*sec["params"]["h"]**3)/12.0

        # local stiffness matrix (6x6)
        k_local = np.array([
            [ A*E/L,        0,              0, -A*E/L,        0,              0],
            [ 0,     12*E*I/L**3,  6*E*I/L**2,  0, -12*E*I/L**3,  6*E*I/L**2],
            [ 0,      6*E*I/L**2, 4*E*I/L,     0,  -6*E*I/L**2, 2*E*I/L],
            [-A*E/L,        0,              0,  A*E/L,        0,              0],
            [ 0, -12*E*I/L**3, -6*E*I/L**2,  0,  12*E*I/L**3, -6*E*I/L**2],
            [ 0,      6*E*I/L**2, 2*E*I/L,     0,  -6*E*I/L**2, 4*E*I/L]
        ])

        # transformation matrix
        T = np.array([
            [ c,  s, 0,  0, 0, 0],
            [-s,  c, 0,  0, 0, 0],
            [ 0,  0, 1,  0, 0, 0],
            [ 0,  0, 0,  c, s, 0],
            [ 0,  0, 0, -s, c, 0],
            [ 0,  0, 0,  0, 0, 1]
        ])
        k_global = T.T @ k_local @ T

        # assemble into K
        dofs = self.node_dofs[member["n1"]] + self.node_dofs[member["n2"]]
        for i in range(6):
            for j in range(6):
                K[dofs[i], dofs[j]] += k_global[i, j]

        # add uniform load (scaled)
        for load in member.get("loads", []):
            w = load.get("w", 0.0)  # kN/m
            load_type = load.get("type", "D")  # default = Dead
            factor = load_factors.get(load_type, 1.0)
            w_eff = w * factor

            # fixed-end forces
            f_local = np.array([0, w_eff*L/2, w_eff*L**2/12, 0, w_eff*L/2, -w_eff*L**2/12])
            f_global = T.T @ f_local
            for i in range(6):
                F[dofs[i]] += f_global[i]

    def _distribute_slab_load(self, F, slab, load_factors):
        # self-weight of slab as Dead load
        q = slab["t"] * 25.0 * slab["w"] * slab["h"]  # kN تقريبية
        q_eff = q * load_factors.get("D", 1.0)

        per_member = q_eff / max(1, len(self.members))
        for member in self.members:
            dofs = self.node_dofs[member["n1"]] + self.node_dofs[member["n2"]]
            F[dofs[1]] += -per_member/2
            F[dofs[4]] += -per_member/2

    def _get_support_dofs(self):
        fixed = []
        for nid, node in self.nodes.items():
            dofs = self.node_dofs[nid]
            if node["support"] == "fix":
                fixed += dofs
            elif node["support"] == "pin":
                fixed += [dofs[0], dofs[1]]
            elif node["support"] == "roller":
                fixed += [dofs[1]]
        return fixed

    def _recover_forces(self, member, U):
        """
        استرجاع القوى الداخلية (N, V, M) لكل عضو
        """
        n1, n2 = self.nodes[member["n1"]], self.nodes[member["n2"]]
        x1, y1, x2, y2 = n1["x"], n1["y"], n2["x"], n2["y"]
        L = np.sqrt((x2-x1)**2 + (y2-y1)**2)

        dofs = self.node_dofs[member["n1"]] + self.node_dofs[member["n2"]]
        u_elem = U[dofs]

        c, s = (x2-x1)/L, (y2-y1)/L
        T = np.array([
            [ c,  s, 0,  0, 0, 0],
            [-s,  c, 0,  0, 0, 0],
            [ 0,  0, 1,  0, 0, 0],
            [ 0,  0, 0,  c, s, 0],
            [ 0,  0, 0, -s, c, 0],
            [ 0,  0, 0,  0, 0, 1]
        ])

        sec = self.sections[member["sectionId"]]
        mat = self.materials[member["materialId"]]
        E = mat["E"]
        A = sec["params"].get("A", sec["params"]["bw"]*sec["params"]["h"])
        I = (sec["params"]["bw"]*sec["params"]["h"]**3)/12.0

        k_local = np.array([
            [ A*E/L,        0,              0, -A*E/L,        0,              0],
            [ 0,     12*E*I/L**3,  6*E*I/L**2,  0, -12*E*I/L**3,  6*E*I/L**2],
            [ 0,      6*E*I/L**2, 4*E*I/L,     0,  -6*E*I/L**2, 2*E*I/L],
            [-A*E/L,        0,              0,  A*E/L,        0,              0],
            [ 0, -12*E*I/L**3, -6*E*I/L**2,  0,  12*E*I/L**3, -6*E*I/L**2],
            [ 0,      6*E*I/L**2, 2*E*I/L,     0,  -6*E*I/L**2, 4*E*I/L]
        ])

        u_local = T @ u_elem
        f_local = k_local @ u_local

        N, V, M = f_local[0], f_local[1], f_local[2]
        return {"Nmax": float(N), "Vmax": float(V), "Mmax": float(M)}

    def _format_displacements(self, U):
        disp = {}
        for nid, dofs in self.node_dofs.items():
            disp[nid] = {"ux": float(U[dofs[0]]), "uy": float(U[dofs[1]]), "rz": float(U[dofs[2]])}
        return disp

    def _parse_load_combination(self, expr: str):
        """
        Parse load combination expression like '1.2D+1.6L+0.9E'
        """
        factors = {}
        terms = expr.replace("-", "+-").split("+")
        for t in terms:
            t = t.strip()
            if not t: continue
            if t[-1].isalpha():
                factor, ltype = float(t[:-1]), t[-1]
                factors[ltype] = factor
        return factors
