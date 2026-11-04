from app.helpers.generators.base_report import BaseReportGenerator
from reportlab.platypus import Spacer, Paragraph, HRFlowable, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import io
from datetime import datetime


class MantenimientoReport(BaseReportGenerator):
    MODULO = 'mantenimiento'
    TITULO = 'REPORTE DE MANTENIMIENTO'
    COLUMNAS = [
        ('Recurso', 'recurso', 110), ('Estado', 'estado', 65),
        ('Ingreso', 'ingreso', 65), ('Diagnóstico', 'diagnostico', 130),
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
            items = [(k, kpis.get(k, 0)) for k in ('en_espera', 'en_reparacion', 'reparados', 'dados_baja') if kpis.get(k, 0) > 0]
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
            Paragraph(str(d.get('recurso_nombre', '—'))[:24], self.style_normal),
            str(d.get('estado', '—')),
            str(d.get('fecha_ingreso', ''))[:10] if d.get('fecha_ingreso') else '—',
            str(d.get('diagnostico', '—'))[:28],
        ] for d in datos]