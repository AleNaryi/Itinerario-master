from app.helpers.generators.base_report import BaseReportGenerator
from reportlab.platypus import Spacer, Paragraph, HRFlowable, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import io
from datetime import datetime


class TareasReport(BaseReportGenerator):
    MODULO = 'tareas'
    TITULO = 'REPORTE DE TAREAS'
    COLUMNAS = [
        ('Tarea', 'tarea', 150), ('Estado', 'estado', 65),
        ('Asignado a', 'asignado', 80), ('Fecha', 'fecha', 75),
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
            items = [(k, kpis.get(k, 0)) for k in ('pendientes', 'en_progreso', 'completadas') if kpis.get(k, 0) > 0]
            if items:
                story.extend(self._seccion_distribucion('Distribución por Estado', items, colors.HexColor('#15803d')))
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
            Paragraph(str(d.get('nombre_tarea', ''))[:30], self.style_normal),
            str(d.get('estado', 'Pendiente')),
            str(d.get('asignado_a', '—')), str(d.get('fecha_asignacion_tarea', ''))[:10] or '—',
        ] for d in datos]