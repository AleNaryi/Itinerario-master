from app.helpers.generators.base_report import BaseReportGenerator
from reportlab.platypus import Spacer, Paragraph, HRFlowable, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import io
from datetime import datetime


class PremiosReport(BaseReportGenerator):
    MODULO = 'premios'
    TITULO = 'REPORTE DE PREMIOS'
    COLUMNAS = [
        ('Nombre', 'nombre', 120), ('Patrocinador', 'patrocinador', 90),
        ('Estado', 'estado', 55), ('Total', 'total', 35), ('Entreg.', 'entregados', 40),
        ('Creación', 'creacion', 65),
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
        if kpis:
            items = [(k, kpis.get(k, 0)) for k in ('pendientes', 'entregados') if kpis.get(k, 0) > 0]
            if items:
                story.extend(self._seccion_distribucion('Distribución por Estado', items, colors.HexColor('#f59e0b')))
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
            str(d.get('nombre', ''))[:28],
            str(d.get('patrocinador_nombre', '—')),
            str(d.get('estado', '')), str(d.get('cantidad', 1)),
            str(d.get('cantidad_entregada', 0)),
            str(d.get('fecha_creacion', ''))[:10] if d.get('fecha_creacion') else '—',
        ] for d in datos]