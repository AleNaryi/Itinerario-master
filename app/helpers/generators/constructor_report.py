"""PDF del Constructor de Reportes: consume el dataset genérico.

No declara COLUMNAS fijas: la forma depende de lo que el usuario construyó
(dimensión + métricas). Reutiliza estilos/tablas de BaseReportGenerator.
"""
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table

from app.helpers.generators.base_report import BaseReportGenerator


def _fmt(valor, tipo):
    if valor is None:
        return '—'
    if tipo == 'moneda':
        return f"${float(valor):,.0f}"
    if tipo == 'decimal_1':
        return f"{float(valor):,.1f}"
    if tipo == 'pct':
        return f"{float(valor):,.0f}%"
    if tipo == 'entero':
        try:
            return f"{int(float(valor)):,}"
        except (ValueError, TypeError):
            return str(valor)
    return str(valor)


class ConstructorReport(BaseReportGenerator):
    MODULO = 'constructor'
    TITULO = 'REPORTE PERSONALIZADO'

    def generar(self, dataset):
        """Devuelve bytes del PDF para el dataset del constructor."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                rightMargin=40, leftMargin=40,
                                topMargin=40, bottomMargin=40)
        story = []
        filtros = dict(dataset.get('meta', {}).get('filtros_aplicados') or {})
        dimension = dataset['dimension']['label']
        filtros.setdefault('agrupado_por', dimension)
        filtros.setdefault('categoria', dataset.get('categoria', ''))
        story.extend(self._header(filtros))

        # KPIs de totales
        columnas = {c['key']: c for c in dataset['columnas']}
        totales = {columnas[k]['label']: v for k, v in dataset.get('totales', {}).items()
                   if k in columnas}
        if totales:
            story.extend(self._seccion_kpis(totales))

        # Tabla principal (dimensión + métricas)
        header = [Paragraph(f"<b>{c['label']}</b>", self.style_bold)
                  for c in dataset['columnas']]
        rows = [header]
        for fila in dataset['filas']:
            rows.append([
                Paragraph(_fmt(fila.get(c['key']), c['tipo'])[:40], self.style_normal)
                if c['key'] == 'dimension' else
                _fmt(fila.get(c['key']), c['tipo'])
                for c in dataset['columnas']
            ])
        if len(rows) > 1:
            total_row = [Paragraph('<b>Total</b>', self.style_bold)]
            for c in dataset['columnas'][1:]:
                total_row.append(
                    Paragraph(f"<b>{_fmt(dataset['totales'].get(c['key']), c['tipo'])}</b>",
                              self.style_bold))
            rows.append(total_row)
            story.extend(self._tabla(rows))

        # Comparativa vs período anterior
        comp = dataset.get('comparacion')
        if comp:
            story.append(Spacer(1, 10))
            story.append(HRFlowable(width="100%", thickness=1,
                                    color=colors.HexColor('#cbd5e1'), spaceAfter=4))
            story.append(Paragraph(
                "<b>Comparativa vs período anterior</b> "
                f"<font size='8' color='#64748b'>({comp['rango_previo'][0]} al "
                f"{comp['rango_previo'][1]})</font>", self.style_normal))
            story.append(Spacer(1, 4))
            comp_rows = [[Paragraph('<b>Métrica</b>', self.style_bold),
                          Paragraph('<b>Variación</b>', self.style_bold)]]
            for k, v in comp.get('variaciones', {}).items():
                label = columnas.get(k, {}).get('label', k.replace('_', ' '))
                comp_rows.append([Paragraph(str(label), self.style_normal),
                                  Paragraph(str(v), self.style_normal)])
            t = Table(comp_rows, colWidths=[280, 120])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ]))
            story.append(t)

        story.append(Spacer(1, 16))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1')))
        meta = dataset.get('meta', {})
        nota = f" — {dataset['modulo']}/{dataset.get('categoria', '')}"
        if meta.get('limit_alcanzado'):
            nota += ' — RESULTADO TRUNCADO POR LÍMITE'
        story.append(Paragraph(
            f"<font size='7' color='#94a3b8'>Constructor de Reportes{nota} — "
            f"{meta.get('generado_en', '')}</font>", self.style_small))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
