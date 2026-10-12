"""Phase 12 poster (PPTX + PDF) with mandatory honesty panel."""
from pptx import Presentation
from pptx.util import Inches
import qrcode

prs = Presentation()
prs.slide_width = Inches(33.867)
prs.slide_height = Inches(19.05)
s = prs.slides.add_slide(prs.slide_layouts[6])
def box(l, t, w, h, text):
    tx = s.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h)).text_frame
    tx.text = text
    tx.word_wrap = True

box(1, 0.3, 31, 1.5, 'Data-Driven Road Traffic Accident Analysis in India — MoRTH 2018-2024 (254 state-years)')
box(1, 2, 9, 6, 'PROBLEM/QUESTION\nCounts without exposure; fragmented vintages.\nRQ1-RQ11 (observational).')
box(11, 2, 10, 6, 'DATA\nBenchmark 254 obs; IMD 236 matched; NCRB monthly (separate); 7 modules; TN districts; conditional history.')
box(22, 2, 10, 6, 'METHODS\nReconciliation; OLS/corr/chi2/Friedman + FDR; lag-only ML vs naive; K-means K=2.')
box(1, 8.5, 9, 6, 'FINDINGS\n+3.7% acc / +12.4% fat; severity 36.33; rain -0.234, Tmax +0.498 (associations).')
box(11, 8.5, 10, 6, 'ML NULL RESULT\nNaive RMSE 1038.6 beats all trained models. Persistence dominates; honestly reported.')
box(22, 8.5, 10, 6, 'READ THIS FIRST (limits)\n- ML did NOT beat the naive baseline.\n- Weather = association, not cause.\n- No exposure-normalized risk (vehicle stock unavailable).\n- 2014-17 conditional, not merged.\n- NCRB monthly is a separate vintage.')
box(1, 15, 20, 2.5, 'CONCLUSION: severity rises while counts fluctuate; counts are not risk; associations are not causes.')
qr = qrcode.make('https://morth-accident-analytics.onrender.com')
qr.save('FINAL_SUBMISSION_PACKAGE/FIGURES/qr_site.png')
s.shapes.add_picture('FINAL_SUBMISSION_PACKAGE/FIGURES/qr_site.png', Inches(28), Inches(15), width=Inches(2.5))
prs.save('FINAL_SUBMISSION_PACKAGE/POSTER/FINAL_PROJECT_POSTER.pptx')
print('poster pptx saved')
