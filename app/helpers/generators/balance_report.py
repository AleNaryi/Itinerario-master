from app.helpers.generators.base_report import BaseReportGenerator
from reportlab.platypus import Spacer, Paragraph, HRFlowable, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import io
from datetime import datetime


class BalanceReport(BaseReportGenerator):
    MODULO = 'balance'
    TITULO = 'REPORTE DE PAGOS / BALANCE'
    COLUMNAS = [
        ('Patrocinador', 'nombre_patrocinador', 120),
        ('Tipo Pago', 'tipo_pago', 70),
        ('Monto', 'monto', 75),
        ('Referencia', 'referencia', 85),
        ('Fecha Pago', 'fecha_pago', 70),
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
            Paragraph(str(d.get('nombre_patrocinador', '—'))[:28], self.style_normal),
            str(d.get('tipo_pago', '—')),
            f"${float(d.get('monto', 0) or 0):,.0f}",
            str(d.get('referencia', '—'))[:20],
            str(d.get('fecha_pago', '—'))[:10] if d.get('fecha_pago') else '—',
        ] for d in datos]