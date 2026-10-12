"""Poster PDF via reportlab (mirrors poster PPTX)."""
from reportlab.lib.pagesizes import landscape, A3
from reportlab.pdfgen import canvas

c = canvas.Canvas('FINAL_SUBMISSION_PACKAGE/POSTER/FINAL_PROJECT_POSTER.pdf', pagesize=landscape(A3))
W, H = landscape(A3)
c.setFont('Helvetica-Bold', 22)
c.drawCentredString(W / 2, H - 50, 'Data-Driven Road Traffic Accident Analysis in India')
c.setFont('Helvetica', 11)
lines = [
    'MoRTH 2018-2024 (254 state-years) | IMD weather 236 matched | NCRB monthly (separate vintage)',
    'FINDINGS: +3.7% accidents / +12.4% deaths; severity 36.33; rain r=-0.234, Tmax r=+0.498 (associations).',
    'ML NULL: naive RMSE 1038.6 beats all trained models. K=2 descriptive profiles (silhouette 0.356).',
    'READ FIRST: weather = association not cause; no exposure-normalized risk (vehicle stock unavailable);',
    '2014-17 conditional, not merged; NCRB monthly is a separate vintage.',
    'Live demo: https://morth-accident-analytics.onrender.com',
]
y = H - 100
for L in lines:
    c.drawString(60, y, L)
    y -= 22
c.save()
print('poster pdf saved')
