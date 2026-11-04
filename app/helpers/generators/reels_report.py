from app.helpers.generators.base_report import BaseReportGenerator
from reportlab.platypus import (
    Spacer, Paragraph, HRFlowable, SimpleDocTemplate,
    Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import io
from datetime import datetime


class ReelsReport(BaseReportGenerator):
    MODULO = 'reels'
    TITULO = 'REPORTE DE REELS'
    COLUMNAS = []

    def _setup_styles(self):
        super()._setup_styles()
        self.style_reel_title = ParagraphStyle('ReelTitle', parent=self.style_normal,
            fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#1e40af'),
            spaceBefore=8, spaceAfter=2)
        self.style_reel_info = ParagraphStyle('ReelInfo', parent=self.style_normal,
            fontSize=8, textColor=colors.HexColor('#64748b'), spaceAfter=4)
        self.style_video_header = ParagraphStyle('VideoHeader', parent=self.style_normal,
            fontSize=8, fontName='Helvetica-Bold', textColor=colors.HexColor('#475569'),
            spaceBefore=2, spaceAfter=2)

    def generate(self, datos, filtros=None, kpis=None, opciones=None):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        story.extend(self._header(filtros))
        if kpis:
            story.extend(self._seccion_kpis(kpis))
        story.extend(self._secciones_analisis(kpis, opciones))
        if not datos:
            story.append(Paragraph("<font color='#64748b'>No hay reels para mostrar.</font>", self.style_normal))
        else:
            for reel in datos:
                block = []
                block.extend(self._seccion_reel(reel))
                block.extend(self._tabla_videos(reel.get('videos', [])))
                block.append(Spacer(1, 6))
                story.append(KeepTogether(block))
        story.append(Spacer(1, 16))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1')))
        story.append(Paragraph(
            f"<font size='7' color='#94a3b8'>Reporte generado automáticamente — {self.TITULO} — {datetime.now().strftime('%d/%m/%Y %H:%M')}</font>",
            self.style_small))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _seccion_reel(self, reel):
        nombre = reel.get('nombre', 'Sin nombre')
        patrocinador = reel.get('patrocinado') or '—'
        duracion = reel.get('duracion', '—')
        creado = reel.get('creado_en', '—')
        if hasattr(creado, 'strftime'):
            creado = creado.strftime('%d/%m/%Y')
        elif isinstance(creado, str) and len(creado) > 10:
            creado = creado[:10]
        info_parts = [f"Patrocinador: <b>{patrocinador}</b>", f"Duración: <b>{duracion}</b>", f"Creado: <b>{creado}</b>"]
        return [
            HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#1e40af'), spaceAfter=2),
            Paragraph(f"▶ {nombre}", self.style_reel_title),
            Paragraph('  |  '.join(info_parts), self.style_reel_info),
        ]

    def _tabla_videos(self, videos):
        if not videos:
            return [Paragraph("<font size='8' color='#94a3b8'><i>Sin videos registrados</i></font>", self.style_normal)]
        header_row = [
            Paragraph('<b>#</b>', self.style_video_header),
            Paragraph('<b>Nombre</b>', self.style_video_header),
            Paragraph('<b>Duración</b>', self.style_video_header),
            Paragraph('<b>Patrocinador</b>', self.style_video_header),
        ]
        rows = [header_row]
        for i, v in enumerate(videos, 1):
            dur_seg = v.get('duracion_segundos', 0) or 0
            dur_min = int(dur_seg // 60)
            dur_s = int(dur_seg % 60)
            dur_str = f"{dur_min}m {dur_s}s" if dur_min > 0 else f"{dur_s}s"
            rows.append([
                Paragraph(str(i), self.style_normal),
                Paragraph(str(v.get('nombre', ''))[:35], self.style_normal),
                Paragraph(dur_str, self.style_normal),
                Paragraph(str(v.get('patrocinador_nombre', '—')), self.style_normal),
            ])
        col_widths = [25, 200, 60, 180]
        table = Table(rows, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#475569')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (0, -1), 8),
        ]))
        return [table]

    def _build_rows(self, datos):
        return []