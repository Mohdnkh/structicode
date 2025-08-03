from fpdf import FPDF
import os

class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Simple Test PDF", ln=True, align="C")

def generate_pdf(data, result, filename="simple_report.pdf"):
    pdf = PDFReport()

    # ✅ استخدم خط داخلي فقط (بدون DejaVu أو ملفات .ttf)
    pdf.set_font("Arial", size=12)
    pdf.add_page()
    pdf.cell(0, 10, "This is a basic PDF without external fonts.", ln=True)
    pdf.cell(0, 10, f"Code: {data.get('code', 'N/A')}", ln=True)
    pdf.cell(0, 10, f"Element: {data.get('element', 'N/A')}", ln=True)

    output_dir = os.path.abspath("reports")
    os.makedirs(output_dir, exist_ok=True)
    full_path = os.path.join(output_dir, filename)

    pdf.output(full_path)
    print(f"[DEBUG] PDF generated at: {full_path}")
    return full_path
