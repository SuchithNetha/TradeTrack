from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import os

def generate_pdf_report(metrics, temp_images):
    """Generate a PDF report with metrics and charts."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    flowables = []

    flowables.append(Paragraph("TradeTrack - Performance Report", styles["Title"]))
    flowables.append(Spacer(1, 8))
    
    # KPIs summary
    flowables.append(Paragraph(f"Total Trades: {metrics['total_trades']}", styles["Normal"]))
    flowables.append(Paragraph(f"Win Rate: {metrics['win_rate']:.2f}%", styles["Normal"]))
    flowables.append(Paragraph(f"Total PnL: {float(metrics['pnl_series'].sum()):.2f}", styles["Normal"]))
    flowables.append(Paragraph(f"Expectancy: {metrics['expectancy']:.2f}", styles["Normal"]))
    flowables.append(Paragraph(f"Profit Factor: {metrics['profit_factor']:.2f}", styles["Normal"]))
    flowables.append(Paragraph(f"Sharpe (mean/std): {metrics['sharpe']:.2f}", styles["Normal"]))
    flowables.append(Paragraph(f"Max Drawdown: {metrics['max_drawdown']:.2f}", styles["Normal"]))
    flowables.append(Spacer(1, 12))

    # Add charts into the PDF
    for img_path in temp_images:
        try:
            if os.path.exists(img_path):
                flowables.append(RLImage(img_path, width=450, height=250))
                flowables.append(Spacer(1, 12))
        except Exception:
            pass

    doc.build(flowables)
    buffer.seek(0)
    return buffer

def cleanup_temp_images(temp_images):
    """Remove temporary image files."""
    for p in temp_images:
        try:
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            pass
