
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generar_pdf_estado_cuenta(contrato_id, contrato_data, monto_pagado_contrato, monto_total_contrato, saldo_pendiente_contrato, pagos_contrato, usuario_actual):
    """
    Genera el reporte PDF en memoria y devuelve el valor del buffer de bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40,
    )

    story = []
    styles = getSampleStyleSheet()

    style_titulo = ParagraphStyle(
        'TituloReporte',
        parent=styles['Heading1'],
        fontSize=20, leading=24,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6,
    )
    style_normal = styles['Normal']
    style_bold = ParagraphStyle(
        'TextoNegrita', parent=style_normal, fontName='Helvetica-Bold'
    )

    # Extraer datos del usuario operador de forma segura
    usuario_operador = getattr(usuario_actual, 'nombre', 'Sistema')
    rol_usuario = getattr(usuario_actual, 'rol', 'Administrador')
    depto_usuario = getattr(usuario_actual, 'departamento', 'Operaciones')

    # Encabezado
    story.append(Paragraph("<b>ESTADIO ANTONIO HERRERA GUTI\u00c9RREZ</b>", style_bold))
    story.append(Paragraph(f"Departamento: {depto_usuario} | Rol: {rol_usuario}", style_normal))
    story.append(Paragraph(f"<b>Generado por:</b> {usuario_operador.upper()}", style_normal))
    story.append(Paragraph(f"<b>Fecha de Emisión:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", style_normal))
    story.append(Spacer(1, 15))

    story.append(Paragraph(f"ESTADO DE CUENTA - CONTRATO #{contrato_id}", style_titulo))
    story.append(Spacer(1, 10))

    # Información del Patrocinador
    datos_patrocinador = [
        [Paragraph("<b>Patrocinador:</b>", style_normal),
         Paragraph(contrato_data.get('nombre_patrocinador', 'Sin nombre'), style_normal)],
        [Paragraph("<b>Monto Total Contratado:</b>", style_normal),
         Paragraph(f"${monto_total_contrato:,.2f}", style_normal)],
        [Paragraph("<b>Total Pagado a la Fecha:</b>", style_normal),
         Paragraph(f"${monto_pagado_contrato:,.2f}", style_normal)],
        [Paragraph("<b>Saldo Pendiente Neto:</b>", style_normal),
         Paragraph(f"<font color='red'><b>${saldo_pendiente_contrato:,.2f}</b></font>", style_normal)],
    ]

    tabla_info = Table(datos_patrocinador, colWidths=[150, 380])
    tabla_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    story.append(tabla_info)
    story.append(Spacer(1, 25))

    # Tabla de Transacciones
    story.append(Paragraph("<b>Desglose de Transacciones Registradas</b>", styles['Heading3']))
    story.append(Spacer(1, 8))

    tabla_pagos_data = [[
        Paragraph("<b>ID Pago</b>", style_bold),
        Paragraph("<b>Fecha</b>", style_bold),
        Paragraph("<b>Tipo de Pago</b>", style_bold),
        Paragraph("<b>Referencia</b>", style_bold),
        Paragraph("<b>Monto</b>", style_bold),
    ]]

    for p in pagos_contrato:
        tabla_pagos_data.append([
            Paragraph(str(p.id_pago), style_normal),
            Paragraph(p.fecha_pago.strftime('%d/%m/%Y') if p.fecha_pago else '-', style_normal),
            Paragraph(p.tipo_pago or '-', style_normal),
            Paragraph(p.referencia or '-', style_normal),
            Paragraph(f"${float(p.monto):,.2f}", style_normal),
        ])

    if len(pagos_contrato) == 0:
        tabla_pagos_data.append([
            Paragraph("No se registran movimientos de pago para este contrato.", style_normal),
            "", "", "", "",
        ])

    tabla_pagos = Table(tabla_pagos_data, colWidths=[60, 90, 120, 130, 130])
    estilo_tabla_pagos = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#273aaadd")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ]
    if len(pagos_contrato) == 0:
        estilo_tabla_pagos.append(('SPAN', (0, 1), (-1, 1)))

    tabla_pagos.setStyle(TableStyle(estilo_tabla_pagos))
    story.append(tabla_pagos)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()