"""Step 1 PDF mirror (reportlab; same content spine as DOCX)."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.units import inch

PKG = 'FINAL_SUBMISSION_PACKAGE'
doc = SimpleDocTemplate(f'{PKG}/01_FINAL_REPORT/FINAL_BTECH_RESEARCH_REPORT.pdf', pagesize=A4,
                        topMargin=0.9 * inch, bottomMargin=0.9 * inch,
                        leftMargin=1 * inch, rightMargin=1 * inch,
                        title='Multi-Level Data-Driven Analysis of Road Traffic Accidents in India',
                        author='B.Tech Research Report 2026')
ss = getSampleStyleSheet()
ss['BodyText'].alignment = TA_JUSTIFY
ss['BodyText'].fontName = 'Times-Roman'
ss['BodyText'].fontSize = 12
ss['BodyText'].leading = 18
for h in ['Heading1', 'Heading2', 'Heading3']:
    ss[h].fontName = 'Times-Bold'
cap = ParagraphStyle('cap', parent=ss['BodyText'], fontSize=10, alignment=TA_CENTER, spaceBefore=4)
story = []
story.append(Paragraph('<b>A Multi-Level Data-Driven Analysis of Road Traffic Accidents in India</b>', ss['Title']))
story.append(Paragraph('Geographical, Temporal, Seasonal, Environmental and Severity Assessment', ss['Heading2']))
story.append(Paragraph('B.Tech Research Report — 2026 (conventional format; department template unavailable)', ss['Normal']))
story.append(PageBreak())
story.append(Paragraph('Certificate / Declaration / Acknowledgement — placeholders for candidate completion.', ss['Normal']))
story.append(Paragraph('Abstract', ss['Heading1']))
for para in open(f'{PKG}/03_ABSTRACT/FINAL_ABSTRACT.md', encoding='utf-8').read().split('\n\n')[1:]:
    story.append(Paragraph(para.replace('\n', ' '), ss['BodyText']))
story.append(Paragraph('Abbreviations: MoRTH, NCRB, ADSI, IMD, CMPG, ABDB, RGI, BRSI, TRW, OLS, FDR, BH, RMSE, MAE, KNN (supervised).', ss['Normal']))
story.append(PageBreak())
chapters = [
    ('Chapter 1 — Introduction', 'India 487,707 accidents / 177,175 deaths (2024); severity 36.33; RQ1-RQ11 observational; objectives 1-13; scope 2018-2024 benchmark + conditional layers.'),
    ('Chapter 2 — Literature Review', 'LITERATURE REVIEW SOURCES REQUIRED — no external literature collected; nothing invented.'),
    ('Chapter 3 — Research Methodology', 'Per PHASE10_METHODOLOGY.md: verification by reconciliation; OLS/corr/chi2/Friedman + BH-FDR; lag-only ML vs naive; K-means K=2; seed 42.'),
    ('Chapter 4 — Data Sources and Validation', '254 state-years, 38 entities, 0 mismatches; NCRB separate (-19,740); IMD 236/18; 7 modules VERIFIED-MIRROR; TN reconciled; AR2017 conditional 12/12.'),
    ('Chapter 5 — India-Level Analysis', '+3.7% acc / +12.4% fat; 2020 dip; slopes ns (N=7).'),
    ('Chapter 6 — Geographical Analysis', 'Friedman chi2=25.29 p=3.0e-4 W=0.72 (descriptive); state slopes mostly non-detectable; no rankings.'),
    ('Chapter 7 — Temporal and Seasonal Analysis', 'Annual fluctuation; NCRB May 8.84% / July 7.46% (NCRB vintage, never merged).'),
    ('Chapter 8 — Environmental Analysis', 'Rain -0.234/-0.376; Tmax +0.452/+0.498; Tmin +0.366/+0.340 (FDR, N=236); severity null; never causal.'),
    ('Chapter 9 — Severity, Cause, Collision, Road-User', 'Over-speeding 70.3% (reported); Hit from Back leads; two-wheelers 46.2% (counts); licence/safety reported shares.'),
    ('Chapter 10 — Statistical Analysis', 'Full methods + FDR + effect sizes; near-zero rule documented.'),
    ('Chapter 11 — Machine Learning and Clustering', 'Naive RMSE 1038.6/286.3 beats all trained (honest null); K=2 silhouette 0.356 descriptive.'),
    ('Chapter 12 — Discussion', 'Per PHASE10_DISCUSSION_SECTION.md.'),
    ('Chapter 13 — Limitations', 'Vehicle stock, microdata, monthly MoRTH, N=213, vintages (full matrix).'),
    ('Chapter 14 — Contributions', '10 bounded contributions.'),
    ('Chapter 15 — Application Vision', 'Mode A/B platform; analytical tool, NOT proven predictor.'),
    ('Chapter 16 — Conclusion', 'Per PHASE10_CONCLUSION.md.'),
    ('References', 'Per FINAL_REFERENCES.md (mirrors labeled; nothing invented).'),
    ('Appendices', 'A dictionary; B availability; C statistics; D ML; E clustering; F graphs; G reproducibility.'),
]
for title, body in chapters:
    story.append(Paragraph(title, ss['Heading1']))
    story.append(Paragraph(body, ss['BodyText']))
figs = ['F01', 'F02', 'F03', 'F04', 'F07', 'F08', 'F09', 'F11', 'F13', 'F15', 'F16']
caps = {}
for line in open(f'{PKG}/05_FIGURES/FINAL_FIGURE_CAPTIONS.md', encoding='utf-8'):
    if line.startswith('F') and '.' in line[:6]:
        caps[line.split('.')[0]] = line.strip()
for fid in figs:
    story.append(Paragraph(f'<b>Figure {fid}.</b> ' + caps.get(fid, ''), cap))
    story.append(Image(f'{PKG}/FIGURES/{fid}.png', width=5.5 * inch, height=3.4 * inch))
story.append(Paragraph('<b>Tables 1-15.</b> Per FINAL_TABLES.md (values preserved exactly).', ss['Normal']))
doc.build(story)
print('report pdf saved')
