from fpdf import FPDF
import os

class PDFReport(FPDF):
    def header(self):
        self.set_font("DejaVu", "", 16)
        self.cell(0, 10, "Test PDF", ln=True, align="C")

def generate_pdf(data, result, filename="test_report.pdf"):
    pdf = PDFReport()
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")

    # فحص وجود ملف الخط
    print(f"[DEBUG] Font path exists: {os.path.exists(font_path)}")
    pdf.add_font("DejaVu", "", font_path, uni=True)

    pdf.set_font("DejaVu", size=12)
    pdf.add_page()
    pdf.cell(0, 10, "✅ Hello from Railway PDF test!", ln=True)

    # مسار الحفظ
    output_dir = os.path.abspath("reports")
    os.makedirs(output_dir, exist_ok=True)
    full_path = os.path.join(output_dir, filename)

    pdf.output(full_path)
    print(f"[DEBUG] PDF generated at: {full_path}")

    return full_path
