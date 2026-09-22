"""Conservative, in-memory PDF rendering from immutable P7 run snapshots."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from fpdf import FPDF

from .models import AnalysisRunRecord, REPORT_SCHEMA_VERSION


FONT_PATH = Path(__file__).resolve().parents[1] / "utils" / "DejaVuSans.ttf"


class TracePDF(FPDF):
    def __init__(self, run: AnalysisRunRecord):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.run = run
        self.set_auto_page_break(auto=True, margin=18)
        self.set_margins(14, 18, 14)
        self.add_font("Trace", "", str(FONT_PATH), uni=True)

    def header(self):
        self.set_font("Trace", "", 11)
        self.set_text_color(25, 55, 85)
        self.cell(0, 6, "Structicode | Traceable Engineering Report", ln=True)
        self.set_draw_color(160, 175, 190)
        self.line(14, 25, 196, 25)
        self.ln(3)

    def footer(self):
        self.set_y(-13)
        self.set_font("Trace", "", 8)
        self.set_text_color(90, 90, 90)
        self.cell(0, 5, f"Run {self.run.run_id} | Page {self.page_no()}", align="C")


def _text(value: Any) -> str:
    """Display data as inert text; PDF generation never evaluates markup."""
    if value is None:
        return "not supplied"
    return str(value).replace("\x00", " ")


def _lines(value: Any, prefix: str = "", depth: int = 0) -> list[str]:
    if depth > 5:
        return [f"{prefix}: [nested value omitted]"]
    if isinstance(value, dict):
        output: list[str] = []
        for key in sorted(value):
            if key in {"legacy_status", "status"} and str(value[key]).lower() in {"safe", "unsafe"}:
                continue
            label = f"{prefix}.{key}" if prefix else str(key)
            output.extend(_lines(value[key], label, depth + 1))
        return output
    if isinstance(value, list):
        output = []
        for index, item in enumerate(value):
            output.extend(_lines(item, f"{prefix}[{index}]", depth + 1))
        return output
    return [f"{prefix}: {_text(value)}"]


def _section(pdf: TracePDF, title: str) -> None:
    pdf.set_fill_color(230, 237, 245)
    pdf.set_text_color(20, 45, 70)
    pdf.set_font("Trace", "", 11)
    pdf.cell(0, 7, title, ln=True, fill=True)
    pdf.set_text_color(20, 20, 20)
    pdf.set_font("Trace", "", 8.5)


def _paragraph(pdf: TracePDF, text: str) -> None:
    pdf.multi_cell(0, 4.7, _text(text))


def _key_values(pdf: TracePDF, values: list[tuple[str, Any]]) -> None:
    for key, value in values:
        pdf.set_font("Trace", "", 8.5)
        pdf.multi_cell(0, 4.7, f"{key}: {_text(value)}")


def _warning_lines(run: AnalysisRunRecord) -> list[str]:
    source_targets = run.capability_snapshot.get("verification_targets", [])
    target_lines = [
        f"Future verification target remains source blocked: {item.get('target_id', 'unknown')}"
        for item in source_targets if item.get("status") == "SOURCE_BLOCKED"
    ]
    return list(dict.fromkeys([*run.warnings, *run.capability_snapshot.get("warnings", []), *target_lines]))


def _render_structure_results(pdf: TracePDF, run: AnalysisRunRecord) -> None:
    combinations = run.canonical_result_snapshot.get("combinations", {})
    for combo_id, combo in combinations.items():
        pdf.set_font("Trace", "", 9)
        pdf.multi_cell(0, 5, f"Combination {combo_id}: {combo.get('name')} ({combo.get('expression')})")
        for node_id, displacement in combo.get("displacements", {}).items():
            _paragraph(pdf, f"Node {node_id} displacement: ux={displacement.get('ux_mm')} mm, "
                            f"uy={displacement.get('uy_mm')} mm, rz={displacement.get('rz_rad')} rad")
        for node_id, reaction in combo.get("reactions", {}).items():
            _paragraph(pdf, f"Node {node_id} reaction: Rx={reaction.get('rx_n')} N, "
                            f"Ry={reaction.get('ry_n')} N, Mz={reaction.get('mz_n_mm')} N·mm")
        for member_id, force in combo.get("member_forces", {}).items():
            _paragraph(pdf, f"Member {member_id}: Nmax={force.get('nmax_n')} N, "
                            f"Vmax={force.get('vmax_n')} N, Mmax={force.get('mmax_n_mm')} N·mm, "
                            f"Mmax location={force.get('mmax_x_mm')} mm")
            for end_name in ("end_1", "end_2"):
                end = force.get(end_name, {})
                _paragraph(pdf, f"  {end_name}: axial={end.get('axial_n')} N, "
                                f"shear={end.get('shear_n')} N, moment={end.get('moment_n_mm')} N·mm")
        for warning in combo.get("warnings", []):
            _paragraph(pdf, f"Solver warning: {warning}")


def render_report_bytes(run: AnalysisRunRecord) -> bytes:
    """Build one report in memory, using only the supplied stored run record."""
    pdf = TracePDF(run)
    pdf.add_page()
    generated_at = datetime.now(timezone.utc).isoformat()

    _section(pdf, "Report Header")
    _key_values(pdf, [
        ("Analysis run ID", run.run_id), ("Analysis timestamp", run.created_at.isoformat()),
        ("Report generation timestamp", generated_at), ("Analysis kind", run.analysis_kind),
        ("Code family", run.code_family_id),
        ("Engineering verification status", run.verification_status.value),
    ])

    _section(pdf, "Traceability")
    _key_values(pdf, [
        ("Run record SHA-256", run.record_hash_sha256), ("Input SHA-256", run.input_hash_sha256),
        ("Result SHA-256", run.result_hash_sha256), ("Run schema", run.schema_version),
        ("Report schema", REPORT_SCHEMA_VERSION), ("Engine", run.engine_metadata.engine_id),
        ("Engine version", run.engine_metadata.engine_version),
        ("Repository commit", run.engine_metadata.repository_commit_sha),
        ("Standard metadata confidence", run.capability_snapshot["standard_metadata"]["confidence"]),
    ])

    _section(pdf, "Canonical Unit System")
    _key_values(pdf, list(run.canonical_units.items()))

    _section(pdf, "Capability and Verification")
    _key_values(pdf, [
        ("Family display name", run.capability_snapshot["display_name"]),
        ("Jurisdiction label", run.capability_snapshot["jurisdiction"]),
        ("Structure analysis mechanics", run.capability_snapshot["structure_analysis"]["status"]),
        ("Structure design", run.capability_snapshot["structure_design"]["status"]),
        ("Load combinations", run.capability_snapshot["load_combination"]["status"]),
        ("Seismic", run.capability_snapshot["seismic"]["status"]),
    ])
    if run.element_id:
        relevant = run.capability_snapshot.get("relevant_element_capability", {})
        _key_values(pdf, [("Relevant element", run.element_id),
                          ("Element capability", relevant.get("status", "NOT_IMPLEMENTED"))])
    claims = run.capability_snapshot["standard_metadata"].get("legacy_claims", [])
    if claims:
        _paragraph(pdf, "Legacy claimed labels (not authoritative editions): " + "; ".join(claims))
    _paragraph(pdf, "Family presence and a successfully generated report do not establish engineering verification or design-code compliance.")

    _section(pdf, "Canonical Input Snapshot")
    for line in _lines(run.canonical_input_snapshot):
        _paragraph(pdf, line)

    if run.analysis_kind == "structure":
        _section(pdf, "Normalized Structural Results")
        _render_structure_results(pdf, run)
    else:
        _section(pdf, "Normalized Analysis Result")
        for line in _lines(run.canonical_result_snapshot):
            _paragraph(pdf, line)

    _section(pdf, "Legacy / Unverified Design Output")
    _paragraph(pdf, "These legacy design calculations have not been independently verified and must not be interpreted as an authoritative design-code compliance result.")
    _paragraph(pdf, "Any retained legacy comparison is NOT EVALUATED for engineering adequacy in this report.")
    if run.analysis_kind == "element" and run.element_id in {"steel_beam", "steel_column"}:
        _paragraph(pdf, "Steel legacy output remains UNVERIFIED with check state NOT_EVALUATED; no PASS/FAIL conclusion is reported.")
    if run.analysis_kind == "element" and run.element_id in {"beam", "column", "slab", "footing", "staircase"}:
        _paragraph(pdf, "Concrete legacy output remains unverified. Where provided reinforcement is absent, flexure and overall adequacy remain NOT_EVALUATED.")

    _section(pdf, "Limitations and Required Review")
    for warning in _warning_lines(run):
        _paragraph(pdf, f"- {warning}")
    for note in run.engine_metadata.notes:
        _paragraph(pdf, f"- Engine trace: {note}")
    _paragraph(pdf, "Independent engineering review is required before relying on any legacy design output.")

    rendered = pdf.output(dest="S")
    return rendered.encode("latin-1") if isinstance(rendered, str) else bytes(rendered)
