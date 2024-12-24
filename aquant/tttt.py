import aquant as qs
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def generate_metrics_pdf(metrics_data, filename="investment_metrics.pdf", return_bytes=False):
    """Generate a PDF report from metrics data"""
    buffer = BytesIO() if return_bytes else filename
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    elements.append(Paragraph("Investment Performance Metrics", title_style))

    def format_value(value):
        if isinstance(value, float):
            return f"{value * 100:.2f}%" if abs(value) < 10 else f"{value:.4f}"
        return str(value)

    def create_section(title, data):
        elements.append(Paragraph(title, styles['Heading2']))
        elements.append(Spacer(1, 12))

        table_data = [[k.replace('_', ' ').title(), format_value(v)]
                      for k, v in data.items()]

        t = Table(table_data, colWidths=[2.5 * inch, 2 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))

    # Add sections
    sections = [
        ("General Information", metrics_data['general']),
        ("Returns", metrics_data['returns']),
        ("Risk Metrics", metrics_data['risk']),
        ("Performance Ratios", metrics_data['ratios']),
        ("Drawdown Analysis", metrics_data['drawdown']),
        ("Trading Statistics", metrics_data['timing'])
    ]

    for title, data in sections:
        create_section(title, data)

    # Build PDF
    doc.build(elements)

    if return_bytes:
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    return filename


# extend pandas functionality with metrics, etc.
qs.extend_pandas()

# fetch the daily returns for a stock
stock = qs.utils.download_returns('META')


# qs.plots.snapshot(stock, title='Facebook Performance', show=True)
# show sharpe ratio
returns = qs.stats.sharpe(stock)

# or using extend_pandas() :)
print(stock.sharpe())
# Get metrics as structured data
metrics_data = qs.reports.get_metrics_data(stock)

# generate_metrics_pdf(metrics_data)
# Get bytes:
pdf_bytes = generate_metrics_pdf(metrics_data, return_bytes=True)
with open("investment_metrics.pdf", "wb") as f:
    f.write(pdf_bytes)

# Access specific metrics
print(f"Sharpe Ratio: {metrics_data['ratios']['sharpe']}")
print(f"Max Drawdown: {metrics_data['drawdown']['max_drawdown']}%")


qs.reports.metrics(mode="basic", returns=stock)
# qs.reports.full(...)
# qs.reports.html(stock, "SPY", output="meta_analysis.html")

