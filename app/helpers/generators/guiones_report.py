from datetime import datetime
from app.helpers.generators.base_report import BaseReportGenerator
from reportlab.platypus import Spacer, Paragraph, HRFlowable, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import io


class GuionesReport(BaseReportGenerator):
    MODULO = 'guiones'
    TITULO = 'REPORTE DE GUIONES'
    COLUMNAS = [
        ('Nombre', 'nombre', 150), ('Game', 'game', 40),
        ('Pre-Game', 'pregame', 50), ('Ejecución', 'fecha_ejecucion', 70),
        ('Estado', 'estado', 60), ('Tiempo', 'tiempo_total', 60),
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
            items = [(k, kpis.get(k, 0)) for k in ('borradores', 'publicados', 'en_vivo', 'finalizados') if kpis.get(k, 0) > 0]
            if items:
                story.extend(self._seccion_distribucion('Distribución por Estado', items))
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
            Paragraph(str(d.get('nombre', ''))[:35], self.style_normal),
            str(d.get('game', 0)), str(d.get('pregame', 0)),
            str(d.get('fecha_ejecucion', '—')), str(d.get('estado', '')),
            str(d.get('tiempo_total', '0m')),
        ] for d in datos]