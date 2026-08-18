from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime
import os

class EditorialPDF(FPDF):
    def __init__(self, title_doc):
        super().__init__()
        self.title_doc = title_doc
        self.set_auto_page_break(auto=True, margin=25)
        
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(120, 120, 120)
            try:
                clean_title = self.title_doc.encode('latin-1', 'replace').decode('latin-1')
            except:
                clean_title = "Informe"
            self.cell(0, 10, f'{clean_title} | Perspectiva Institucional', align='R')
            self.ln(15)

    def footer(self):
        self.set_y(-20)
        self.set_font('Times', 'I', 10)
        self.set_text_color(128)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

class ReportGenerator:
    def __init__(self, query, filename="Articulo.pdf"):
        self.query = query
        self.filename = filename
        self.pdf = EditorialPDF(query)
        self.pdf.set_title(query)
        self.pdf.set_author("Smart Research Assistant")

    def _clean(self, text):
        if not text: return ""
        text = str(text)
        # Clean common HTML entities for PDF text flow
        replacements = {
            '\u201c': '"', '\u201d': '"', '\u2019': "'", '\u2018': "'",
            '\u2013': '-', '\u2014': '-', '\u2026': '...', '\u2022': '*',
            '<p>': '', '</p>': '\n\n', 
            '<strong>': '<b>', '</strong>': '</b>', # Map to FPDF html bold
            '<h1>': '', '</h1>': '\n',
            '<h2>': '', '</h2>': '\n',
            '<h3>': '', '</h3>': '\n',
            '<li>': '  - ', '</li>': '\n',
            '<ul>': '', '</ul>': '\n',
            '&nbsp;': ' '
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        
        # Safe encode for latin-1 limitations
        return text.encode('latin-1', 'replace').decode('latin-1')

    def create_cover_page(self):
        self.pdf.add_page()
        self.pdf.set_margins(25, 25, 25)
        
        # Branding
        self.pdf.set_font('Helvetica', 'B', 10)
        self.pdf.set_text_color(100)
        self.pdf.cell(0, 10, "SMART RESEARCH | INTELIGENCIA ESTRATÉGICA", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        self.pdf.ln(30)
        
        # Title
        self.pdf.set_font('Times', 'B', 32)
        self.pdf.set_text_color(20, 20, 40) # Almost black
        # Clean title but keep it raw string for multi_cell
        safe_title = self.query.upper().encode('latin-1', 'replace').decode('latin-1')
        self.pdf.multi_cell(0, 14, safe_title, align='L')
        
        self.pdf.ln(10)
        
        # Date
        self.pdf.set_font('Helvetica', '', 12)
        self.pdf.set_text_color(80)
        date_str = datetime.now().strftime('%d de %B de %Y')
        # Translate months manually if needed or rely on locale (simple replacement)
        months = {
            "January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
            "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
            "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
        }
        for eng, esp in months.items():
            date_str = date_str.replace(eng, esp)
            
        self.pdf.cell(0, 10, f"Informe Generado | {date_str}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.pdf.ln(20)
        self.pdf.set_draw_color(0)
        self.pdf.set_line_width(0.5)
        self.pdf.line(25, self.pdf.get_y(), 185, self.pdf.get_y())
        self.pdf.ln(20)
        
        # Abstract
        self.pdf.set_font('Times', 'I', 14)
        self.pdf.set_text_color(60)
        abstract = "Este informe exhaustivo sintetiza los hallazgos más recientes de nuestras bases de conocimiento internas e inteligencia de mercado externa. Su objetivo es proporcionar una visión estratégica del panorama actual, identificando tendencias clave, cambios técnicos y métricas comparativas relevantes para la toma de decisiones en Argentina y la región."
        self.pdf.multi_cell(0, 9, abstract.encode('latin-1', 'replace').decode('latin-1'))
        
        self.pdf.ln(40)

    def add_section_title(self, title):
        if self.pdf.get_y() > 250:
            self.pdf.add_page()
            
        self.pdf.ln(10)
        self.pdf.set_font('Helvetica', 'B', 18)
        self.pdf.set_text_color(0, 51, 102) # Navy Blue
        safe_title = title.encode('latin-1', 'replace').decode('latin-1')
        self.pdf.multi_cell(0, 10, safe_title, align='L')
        self.pdf.ln(5)

    def add_paragraph(self, text):
        if not text: return
        self.pdf.set_font('Times', '', 12)
        self.pdf.set_text_color(30)
        
        # Clean text specifically for write_html compatibility
        # We need to preserve <b> but remove other html tags that FPDF doesnt support well like div/span
        # Our _clean method does a basic job, let's refine it for write_html
        
        # Simple cleanup
        clean_text = self._clean(text)
        
        # FPDF write_html needs basic html structure to work best or write directly
        # But write_html supports <b> which is what we want for keywords
        try:
            self.pdf.write_html(clean_text)
            self.pdf.ln(8)
        except Exception:
            # Fallback if html parsing fails
            self.pdf.multi_cell(0, 6, clean_text)
            self.pdf.ln(8)

    def add_pricing_table(self, data):
        self.pdf.ln(5)
        self.pdf.set_font('Helvetica', 'B', 10)
        self.pdf.set_fill_color(240, 240, 240)
        self.pdf.cell(90, 10, "Concepto", border=1, fill=True)
        self.pdf.cell(0, 10, "Estimación de Costo", border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.pdf.set_font('Helvetica', '', 10)
        for k, v in data.items():
            k_safe = k.encode('latin-1', 'replace').decode('latin-1')
            v_safe = v.encode('latin-1', 'replace').decode('latin-1')
            self.pdf.cell(90, 10, k_safe, border=1)
            self.pdf.cell(0, 10, v_safe, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.pdf.ln(10)

    def save(self):
        self.pdf.output(self.filename)
        print(f"[*] PDF Profesional guardado: {os.path.abspath(self.filename)}")