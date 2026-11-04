from app.helpers.generators.base_report import BaseReportGenerator
from reportlab.platypus import Spacer, Paragraph, HRFlowable, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import io
from datetime import datetime


class UsuariosReport(BaseReportGenerator):
    MODULO = 'usuarios'
    TITULO = 'REPORTE DE USUARIOS'
    COLUMNAS = [
        ('Nombre', 'nombre', 110), ('Email', 'email', 120),
        ('Rol', 'rol', 70), ('Depto', 'depto', 70), ('Estado', 'estado', 55),
    ]

    def generate(self, datos, filtros=None, kpis=None, opciones=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        story.extend(self._header(filtros))
        if kpis:
            story.extend(self._seccion_kpis(kpis))
        story.extend(self._secciones_analisis(kpis, opciones))
        rows = self._build_rows(datos)
        if rows:
            header = [Paragraph(f"<b>{h}</b>", self.style_bold) for h, _, _ in self.COLUMNAS]
            story.extend(self._tabla([header] + rows))
        story.append(Spacer(1, 16))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1')))
        story.append(Paragraph(
            f"<font size='7' color='#94a3b8'>Reporte generado automáticamente — {self.TITULO} — {datetime.now().strftime('%d/%m/%Y %H:%M')}</font>",
            self.style_small))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _build_rows(self, datos):
        return [[
            str(d.get('nombre', ''))[:24], str(d.get('email', ''))[:26],
            str(d.get('rol', '—')), str(d.get('departamento', '—')),
            'Activo' if d.get('activo') else 'Inactivo',
        ] for d in datos]