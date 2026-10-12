"""Phase 12 DOCX builder (formatting only; content from Phase 11 files)."""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import pandas as pd

doc = Document()
st = doc.styles['Normal']
st.font.name = 'Calibri'
st.font.size = Pt(11)
for h, s in [('Heading 1', 16), ('Heading 2', 13), ('Heading 3', 11)]:
    doc.styles[h].font.color.rgb = RGBColor(0x1F, 0x3B, 0x63)

def H(t, l=1):
    doc.add_heading(t, level=l)

def P(t, bold=False, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(t)
    r.bold = bold
    r.italic = italic
    return p

def table_from_csv(path, max_rows=40):
    df = pd.read_csv(path)
    t = doc.add_table(rows=1, cols=len(df.columns))
    t.style = 'Light Grid Accent 1'
    for j, c in enumerate(df.columns):
        t.rows[0].cells[j].text = str(c)
    for _, row in df.head(max_rows).iterrows():
        cells = t.add_row().cells
        for j, v in enumerate(row):
            cells[j].text = '' if pd.isna(v) else str(v)
    return len(df)

def fig(fid, caption):
    P(f'Figure {fid}. {caption}', italic=True)
    doc.add_picture(f'FINAL_SUBMISSION_PACKAGE/FIGURES/{fid}.png', width=Inches(5.8))

# Cover
for _ in range(4):
    doc.add_paragraph()
P('A Multi-Level Data-Driven Analysis of Road Traffic Accidents in India:', bold=True).alignment = WD_ALIGN_PARAGRAPH.CENTER
P('Geographical, Temporal, Seasonal, Environmental and Severity Assessment', bold=True).alignment = WD_ALIGN_PARAGRAPH.CENTER
P('B.Tech Research Report — 2026 (department template unavailable; conventional B.Tech format used)').alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_page_break()

H('Declaration'); P('[Candidate declaration placeholder.]')
H('Certificate'); P('[Guide certificate placeholder.]')
H('Acknowledgement'); P('[Candidate to complete.]')
H('Abstract')
for line in open('FINAL_SUBMISSION_PACKAGE/03_ABSTRACT/FINAL_ABSTRACT.md', encoding='utf-8').read().split('\n\n')[1:]:
    P(line)
H('Table of Contents'); P('[Update fields in Word: TOC auto-generates from Headings 1-3.]')
H('List of Figures'); P('F01-F16 per FINAL_FIGURE_CAPTIONS.md.')
H('List of Tables'); P('Tables 1-15 per FINAL_TABLES.md.')
H('Abbreviations')
P('MoRTH, NCRB, ADSI, IMD, CMPG, ABDB, RGI, BRSI, TRW, OLS, FDR, BH, RMSE, MAE, KNN.')

chapters = [
    ('Chapter 1 — Introduction', None, None),
    ('Chapter 5 — India-Level Analysis', 'F01', 'India accidents 2018-2024 (MoRTH benchmark; counts are not risk).'),
    (None, 'F02', 'India fatalities 2018-2024 (fatalities +12.4%, outpacing accidents).'),
    (None, 'F03', 'Fatality ratio 33.50 to 36.33 per 100 accidents (case-fatality-style).'),
    ('Chapter 6 — Geographical Analysis', 'F04', 'Zone trends (descriptive; no ranking).'),
    (None, 'F05', 'State-year heatmap (NV shown as missing).'),
    (None, 'F06', 'State slopes with 95% CI (mostly non-detectable).'),
    ('Chapter 7 — Temporal and Seasonal Analysis', 'F13', 'NCRB 2024 monthly (NCRB vintage, NOT MoRTH).'),
    ('Chapter 8 — Environmental Analysis', 'F07', 'Rainfall vs accidents r=-0.234 pooled (associational).'),
    (None, 'F08', 'Tmax vs fatalities r=+0.498 pooled (not causal).'),
    ('Chapter 9 — Severity, Cause, Collision, Road-User', 'F09', 'Violation fatalities 2024 (reported category).'),
    (None, 'F10', 'Collision accidents 2024.'),
    (None, 'F11', 'Road-user fatalities 2024 (counts, not risk).'),
    (None, 'F12', 'Licence accidents 2024 (reported shares).'),
    ('Chapter 11 — Machine Learning and Clustering', 'F15', 'Actual vs predicted + RMSE: naive wins (honest null).'),
    (None, 'F16', 'K-means K=2 silhouette 0.356 (exploratory).'),
]
for ch, f, cap in chapters:
    if ch:
        H(ch)
    if f:
        fig(f, cap)

H('Chapter 10 — Statistical Tables (Tables 1-15)')
P('Full tables: FINAL_TABLES.md. Key values: Friedman chi2=25.29 p=3.0e-4 W=0.72; '
  'naive RMSE 1038.6/286.3; May 8.84% / July 7.46%; over-speeding 70.3%; two-wheelers 46.2%.')
H('Chapter 13 — Limitations'); P('Vehicle stock, microdata, monthly MoRTH, N=213, vintages (full matrix).')
H('Chapter 16 — Conclusion'); P('Per PHASE10_CONCLUSION.md: severity rises; associations associational; nulls preserved.')
H('References'); P('Per FINAL_REFERENCES.md (mirrors labeled; no invented citations).')
doc.save('FINAL_SUBMISSION_PACKAGE/01_FINAL_REPORT/FINAL_BTECH_RESEARCH_REPORT.docx')
print('docx saved')
