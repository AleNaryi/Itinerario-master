from app.helpers.generators.base_report import BaseReportGenerator
from reportlab.platypus import Spacer, Paragraph, HRFlowable, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import io
from datetime import datetime


class InventarioReport(BaseReportGenerator):
    MODULO = 'inventario'
    TITULO = 'REPORTE DE INVENTARIO'
    COLUMNAS = [
        ('ID', 'id', 30), ('Nombre', 'nombre', 130),
        ('Tipo', 'tipo_nombre', 80), ('Estado', 'estado_nombre', 70),
        ('Compra', 'fecha_compra', 70),
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
        else:
            story.append(Spacer(1, 20))
            story.append(Paragraph("<font color='#64748b'>No hay datos para mostrar.</font>", self.style_normal))

        if kpis:
            tipos_l = [(k, v) for k, v in kpis.get('tipos', {}).items() if v > 0]
            if tipos_l:
                story.extend(self._seccion_distribucion('Distribución por Tipo', tipos_l))
            estados_l = [(k, v) for k, v in kpis.get('estados', {}).items() if v > 0]
            if estados_l:
                story.extend(self._seccion_distribucion('Distribución por Estado', estados_l, colors.HexColor('#15803d')))

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
            str(d.get('id', '')),
            str(d.get('nombre', ''))[:28],
            str(d.get('tipo_nombre', '')), str(d.get('estado_nombre', '')),
            str(d.get('fecha_compra', ''))[:10] if d.get('fecha_compra') else '—',
        ] for d in datos]