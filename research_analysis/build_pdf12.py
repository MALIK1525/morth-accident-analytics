"""Phase 12 PDF via reportlab (mirrors DOCX; content from Phase 11)."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import pandas as pd

doc = SimpleDocTemplate('FINAL_SUBMISSION_PACKAGE/01_FINAL_REPORT/FINAL_BTECH_RESEARCH_REPORT.pdf',
                        pagesize=A4, topMargin=0.8 * inch, bottomMargin=0.8 * inch)
styles = getSampleStyleSheet()
story = []
story.append(Paragraph('<b>A Multi-Level Data-Driven Analysis of Road Traffic Accidents in India</b>', styles['Title']))
story.append(Paragraph('Geographical, Temporal, Seasonal, Environmental and Severity Assessment', styles['Heading2']))
story.append(Paragraph('B.Tech Research Report — 2026 (conventional B.Tech format; department template unavailable)', styles['Normal']))
story.append(PageBreak())
abs_txt = open('FINAL_SUBMISSION_PACKAGE/03_ABSTRACT/FINAL_ABSTRACT.md', encoding='utf-8').read()
story.append(Paragraph('<b>Abstract</b>', styles['Heading1']))
for para in abs_txt.split('\n\n')[1:]:
    story.append(Paragraph(para.replace('\n', ' '), styles['Normal']))
    story.append(Spacer(1, 6))
figs = [('F01', 'India accidents 2018-2024 (counts are not risk).'),
        ('F02', 'India fatalities (+12.4%).'), ('F03', 'Severity 33.50 to 36.33.'),
        ('F04', 'Zone trends (no ranking).'), ('F07', 'Rain vs accidents r=-0.234 (associational).'),
        ('F08', 'Tmax vs fatalities r=+0.498 (not causal).'),
        ('F09', 'Violation fatalities 2024 (reported category).'),
        ('F11', 'Road-user fatalities 2024 (counts, not risk).'),
        ('F13', 'NCRB monthly 2024 (NCRB vintage).'),
        ('F15', 'Actual vs predicted; naive wins (honest null).'),
        ('F16', 'K-means K=2 (exploratory).')]
for fid, cap in figs:
    story.append(Paragraph(f'<b>Figure {fid}.</b> {cap}', styles['Heading3']))
    story.append(Image(f'FINAL_SUBMISSION_PACKAGE/FIGURES/{fid}.png', width=5.5 * inch, height=3.4 * inch))
    story.append(Spacer(1, 12))
story.append(Paragraph('<b>Key tables.</b> Friedman chi2=25.29 p=3.0e-4 W=0.72; naive RMSE 1038.6/286.3; '
                       'May 8.84% / July 7.46%; over-speeding 70.3%; two-wheelers 46.2%. Full tables: FINAL_TABLES.md.',
                       styles['Normal']))
story.append(Paragraph('<b>Limitations.</b> Vehicle stock, microdata, monthly MoRTH, N=213, vintages.',
                       styles['Normal']))
story.append(Paragraph('<b>References.</b> Per FINAL_REFERENCES.md (mirrors labeled; nothing invented).',
                       styles['Normal']))
doc.build(story)
print('pdf saved')
