from app.helpers.generators.base_report import BaseReportGenerator
from reportlab.platypus import Spacer, Paragraph, HRFlowable, SimpleDocTemplate
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import io
from datetime import datetime, date


class ContratosReport(BaseReportGenerator):
    MODULO = 'contratos'
    TITULO = 'REPORTE DE CONTRATOS'
    COLUMNAS = [
        ('Empresa', 'nombre_empresa', 115),
        ('Tipo', 'tipo', 50),
        ('Estatus', 'estatus', 50),
        ('Inicio', 'fecha_inicio', 60),
        ('Fin', 'fecha_fin', 60),
        ('Días', 'dias_restantes', 35),
        ('Monto', 'monto_total', 60),
    ]

    def generate(self, datos, filtros=None, kpis=None, opciones=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=letter,
            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40,
        )

        story = []
        story.extend(self._header(filtros))

        if kpis:
            story.extend(self._seccion_kpis(kpis))
        story.extend(self._secciones_analisis(kpis, opciones))

        rows = self._build_rows(datos)
        if rows:
            header = [Paragraph(f"<b>{h}</b>", self.style_bold) for h, _, _ in self.COLUMNAS]
            table_data = [header] + rows
            story.extend(self._tabla(table_data))
        else:
            story.append(Spacer(1, 20))
            story.append(Paragraph(
                "<font color='#64748b'>No hay datos para mostrar.</font>",
                self.style_normal
            ))

        if kpis:
            tipos = [(k, kpis.get(k, 0)) for k in ('bronce', 'plata', 'oro') if kpis.get(k, 0) > 0]
            if tipos:
                story.extend(self._seccion_distribucion('Distribución por Tipo', tipos))
            estatus_items = [(k, kpis.get(k, 0)) for k in ('vigentes', 'vencidos', 'borradores') if kpis.get(k, 0) > 0]
            if estatus_items:
                story.extend(self._seccion_distribucion('Distribución por Estatus', estatus_items, colors.HexColor('#15803d')))

        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1')))
        story.append(Paragraph(
            f"<font size='7' color='#94a3b8'>Reporte generado automáticamente — "
            f"{self.TITULO} — {datetime.now().strftime('%d/%m/%Y %H:%M')}</font>",
            self.style_small
        ))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _build_rows(self, datos):
        return [[
            Paragraph(str(d.get('nombre_empresa', '—'))[:30], self.style_normal),
            str(d.get('tipo', '—')),
            str(d.get('estatus', '—')),
            str(d.get('fecha_inicio', '—'))[:10],
            str(d.get('fecha_fin', '—'))[:10],
            str(d.get('dias_restantes', '—')),
            f"${float(d.get('monto_total', 0) or 0):,.0f}",
        ] for d in datos]
