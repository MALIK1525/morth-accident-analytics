"""Step 2: full-spec 25-slide PPTX (dark academic theme, notes, QR, audits)."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

BG = RGBColor(0x0F, 0x1B, 0x2D)
FG = RGBColor(0xF2, 0xF5, 0xF9)
ACC = RGBColor(0x2D, 0xD4, 0xBF)
MUT = RGBColor(0x9F, 0xB3, 0xC8)
GREEN = RGBColor(0x7D, 0xE3, 0x8B)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]


def bg(s):
    fill = s.background.fill
    fill.solid()
    fill.fore_color.rgb = BG


def tb(s, l, t, w, h):
    return s.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h)).text_frame


def title(s, t):
    f = tb(s, 0.6, 0.25, 12.1, 0.9)
    p = f.paragraphs[0]
    p.text = t
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = FG
    p.font.name = 'Calibri'
    r = f.add_paragraph()
    r.text = ''
    from pptx.util import Pt as _P
    line = tb(s, 0.6, 1.05, 2.2, 0.06)
    line.paragraphs[0].text = ''
    shp = s.shapes.add_shape(1, Inches(0.6), Inches(1.08), Inches(2.2), Pt(3))
    shp.fill.solid()
    shp.fill.fore_color.rgb = ACC
    shp.line.fill.background()


def bullets(s, items, l=0.6, t=1.5, w=5.6, size=20):
    f = tb(s, l, t, w, 5.2)
    f.word_wrap = True
    for i, b in enumerate(items):
        p = f.paragraphs[0] if i == 0 else f.add_paragraph()
        p.text = b
        p.font.size = Pt(size)
        p.font.color.rgb = FG
        p.font.name = 'Calibri'
        p.space_after = Pt(8)
        p.level = 0


def footer(s, src):
    f = tb(s, 0.6, 7.0, 12.1, 0.35)
    p = f.paragraphs[0]
    p.text = 'Source: ' + src
    p.font.size = Pt(12)
    p.font.color.rgb = MUT
    p.font.name = 'Calibri'


def fig(s, fid, l=6.6, t=1.5, w=6.1):
    s.shapes.add_picture(f'FINAL_SUBMISSION_PACKAGE/FIGURES/{fid}.png',
                         Inches(l), Inches(t), width=Inches(w))


def note(s, t):
    s.notes_slide.placeholders[1].text = t


SL = []
SL.append(('A Multi-Level Data-Driven Analysis of Road Traffic Accidents in India',
           ['Data-Driven Road Traffic Accident Analysis in India',
            'B.Tech Research Project — 2026', '[Candidate / Programme / University / Guide]'],
           None, 'MoRTH benchmark 2018-2024',
           'Title slide: state full title once, then use short title. Say candidate, programme, guide.'))
SL.append(('Problem Statement',
           ['Road accidents remain a major public-safety problem.',
            'National totals alone do not explain geography, time, environment, severity.',
            'Official datasets differ in definitions and vintages.',
            'A validated multi-level analytical framework is required.'],
           None, 'MoRTH 2024: 487,707 accidents, 177,175 deaths',
           'Say: scale of the problem in one line; then why totals are not enough.'))
SL.append(('Motivation',
           ['India-wide understanding of accident patterns.',
            'State/zone differences for targeted analysis.',
            'Temporal and weather associations.', 'Severity beyond counts.',
            'Honest predictive evaluation.', 'Future decision-support application.'],
           None, 'Project scope RQ1-RQ11',
           'Say: why this matters analytically. Do NOT promise policy impact.'))
SL.append(('Research Question',
           ['"How do geographical, temporal, seasonal, environmental, roadway, vehicle and other',
            'available factors associate with the occurrence and severity of road traffic',
            'accidents across India?"', 'Observational study — association, not causation.'],
           None, 'RQ1-RQ11, association framing',
           'Say: read the question; stress association-not-causation upfront.'))
SL.append(('Objectives',
           ['Geographical: states/UTs + six zones.', 'Temporal: annual + NCRB monthly.',
            'Environmental: verified rain/Tmax/Tmin.', 'Severity: ratios, causes, collisions, road-users.',
            'Statistical: validated inference + FDR.', 'Predictive: models vs naive baseline; K-means typology.',
            'Application: reusable analytics platform.'],
           None, '13 approved objectives',
           'Say: grouped objectives in one breath each. No new objectives.'))
SL.append(('Research Framework',
           ['INDIA > ZONES > STATES/UTs > TEMPORAL > WEATHER > ROAD/VEHICLE/CAUSE >',
            'SEVERITY > STATISTICS > ML / CLUSTERING > APPLICATION',
            'Each layer gated by source verification and vintage labels.'],
           None, 'Analytical hierarchy (this slide is the map; refer back to it).',
           'Say: walk the hierarchy top to bottom; this is the talk roadmap.'))
SL.append(('Data Sources',
           ['PRIMARY: MoRTH benchmark 2018-2024 (254 state-years, 38 entities).',
            'SEPARATE: NCRB ADSI 2024 monthly; IMD weather (236 matched / 18 excluded).',
            'SEPARATE: 7 supporting MoRTH-2024 modules; TN districts; conditional 2014-17 history.'],
           None, 'MoRTH primary; NCRB/IMD/supporting kept vintage-separate',
           'Say: primary vs separate sources; vintages never merged.'))
SL.append(('Data Validation & Coverage',
           ['254 state-years, 38 entities, 0 benchmark mismatches.',
            '236 usable weather matches, 18 excluded with reasons.',
            'Provenance + SHA-256 for every file; reconciliation gates.',
            'Source-vintage separation enforced throughout.'],
           None, 'Validation checklist design',
           'Say: numbers that prove the data are trustworthy.'))
SL.append(('India-Level Trends',
           ['Accidents: 470,403 to 487,707 (+3.7%).', 'Fatalities: 157,593 to 177,175 (+12.4%).',
            '2020 major decline, then recovery.', 'OLS slopes not significant (N=7) — describe, do not overstate.'],
           'F01', 'MoRTH benchmark CLEAN',
           'Say: deaths outpace accidents; 2020 dip; slopes are descriptive only.'))
SL.append(('Geographical Analysis',
           ['Six-zone framework; 38-entity heterogeneity.',
            'Counts reflect exposure — recorded counts, never risk.',
            'No state is labeled most dangerous / safest / best / worst.'],
           'F05', 'MoRTH benchmark + zone mapping',
           'Say: variation is real; risk language is forbidden without denominators.'))
SL.append(('Zone Analysis',
           ['Friedman chi2 = 25.29, p = 3.0e-4, Kendall W = 0.72.',
            'Repeated-year zone differences statistically detectable.',
            'Zones are NOT ranked.'],
           'F04', 'Zone-year analysis; years as blocks',
           'Say: what Friedman tests here and what W means; no ranking.'))
SL.append(('State Trend Analysis',
           ['Accidents: 17 positive / 15 negative / 6 near-zero.',
            'Fatalities: 26 / 10 / 2. Only a minority statistically detectable.',
            'Wide CIs (N=7); no state ranking.'],
           'F06', 'OLS per state + 95% CI',
           'Say: most slopes non-detectable; that is normal at N=7.'))
SL.append(('Temporal Analysis',
           ['Annual granularity in benchmark (2018-2024).',
            'Hour/day accident-level timing NOT in state-year benchmark.',
            'Monthly detail comes only from NCRB (next slide).'],
           'F02', 'MoRTH benchmark',
           'Say: what time scales we have and which we do not.'))
SL.append(('Seasonal / Monthly (NCRB vintage)',
           ['NCRB ADSI 2024 Road-States, separate vintage.',
            'May 8.84% peak; July 7.46% trough; chi2 = 1276.',
            'Calendar quarters only — no India-wide climate-season claim.'],
           'F13', 'NCRB ADSI 2024 Table 1A.5 — NOT MoRTH',
           'Say: monthly shares + MoM; never call it MoRTH data.'))
SL.append(('Weather Analysis',
           ['Rain: r=-0.234 acc / -0.376 fat.', 'Tmax: +0.452 / +0.498. Tmin: +0.366 / +0.340.',
            'N=236 pooled; FDR-held; scale confounding disclosed.',
            'Statistical associations — NOT causal effects.'],
           'F07', 'IMD-derived integration (236 matched)',
           'Say: r values + N; pooled scale caveat; never "heat causes accidents".'))
SL.append(('Severity Analysis',
           ['Fatality ratio 33.50 to 36.33 per 100 accidents.',
            'Case-fatality-style measure — NOT a population death rate.',
            'Severity rises while counts fluctuate.'],
           'F03', 'Derived: deaths/accidents x 100',
           'Say: define the ratio carefully; it is conditional on recorded accidents.'))
SL.append(('Violations / Reported Causes',
           ['2024: over-speeding 70.7% of accidents, 70.3% of fatalities.',
            '"Reported violation category" — NOT "overspeeding caused 70.7%".',
            'Recording share vs causal mechanism.'],
           'F09', 'MoRTH AR2024 mirror, India-level',
           'Say: the exact 70.3% with the reported-category qualifier.'))
SL.append(('Collision & Road-User Analysis',
           ['Hit from Back most frequent; Hit-and-Run highest ratio (~0.50).',
            'Two-wheelers 46.2%, pedestrians 20.6% of 2024 deaths.',
            'Shares of recorded deaths — NOT exposure-normalized risk.'],
           'F11', 'MoRTH AR2024 mirror, India-level',
           'Say: counts first, risk disclaimer immediately after.'))
SL.append(('Licence & Safety Devices',
           ['Valid licence: 68.2% of reported accidents.',
            'No-helmet deaths 54,122; no-seatbelt deaths 14,466 (2024).',
            'Observed toll counts — no effectiveness/causation claim.'],
           'F12', 'MoRTH AR2024 mirror, India-level',
           'Say: toll, not proof of effectiveness.'))
SL.append(('Statistical Analysis',
           ['Descriptives, OLS + CI, Pearson + Spearman, chi-square, Friedman.',
            'Effect sizes (r, R2, Kendall W); BH-FDR multiple-testing control.',
            'Sensitivity: vintages, pooled vs within-state, per-pair N.'],
           None, 'Methods matrix (Phase 7/8)',
           'Say: one method per breath; FDR means all tests reported.'))
SL.append(('ML Methodology',
           ['Unit: State-Year. Train 2019-2022 (N=141); test 2023-2024 (N=72).',
            'Targets: accidents, fatalities. Lag-only features (cutoff T-1).',
            'Linear, Ridge, RF, GBR, KNN (supervised) vs naive persistence.',
            'Rolling-origin validation; no test-set tuning; leakage audit (4 exclusions).'],
           None, 'Leakage-safe design',
           'Say: design before results; KNN is supervised — say it explicitly.'))
SL.append(('ML Results — the honest null',
           ['Naive RMSE: 1038.6 (acc) / 286.3 (fat) — beats ALL trained models.',
            'Best trained: GBR 2148.6 / LinReg 766.7. GBR train R2~1.0 = overfitting.',
            'Persistence dominates short panels. This null IS the finding.'],
           'F15', 'Stored test predictions',
           'Say: do not soften; the null result is the headline. Never market prediction.'))
SL.append(('K-Means State Typology',
           ['Standardized profiles; K=2-6 diagnostics; K=2 (silhouette 0.356).',
            'Sizes 17 / 6; ARI stability; PCA display.',
            'Descriptive labels only — never high-risk / safe. K-means is unsupervised.'],
           'F16', 'State profiles (means, ratios, slopes, weather)',
           'Say: exploratory grouping; labels describe counts, not risk.'))
SL.append(('Limitations & Contributions',
           ['Limits: no microdata/coords, partial districts, no vehicle stock/AADT, limited weather,',
            '2023-24 state injuries N/A, conditional history, N=213.',
            'Contributions: verified benchmark, integrations, honest nulls, provenance, platform.'],
           None, 'Phase 10 matrices',
           'Say: limits first, then bounded contributions; no novelty overclaim.'))
SL.append(('Conclusion & Application Vision',
           ['Validated multi-level framework; severity rises; pooled weather links; honest ML null.',
            'Vision: benchmark + uploads + analytics + statistics + ML + future GIS.',
            'morth-accident-analytics.onrender.com',
            '"From descriptive statistics toward a reproducible road-safety analytics platform."'],
           None, 'QR links to live site',
           'Say: close with the platform sentence; ML is not production-grade prediction.')

assert len(SL) == 25, len(SL)
for i, (title, bullets_, fid, src, notes) in enumerate(SL):
    s = prs.slides.add_slide(blank)
    bg(s)
    title(s, f'{i+1:02d}  {title}')
    bullets(s, bullets_)
    footer(s, src)
    if fid:
        fig(s, fid)
    if i == 24:
        s.shapes.add_picture('FINAL_SUBMISSION_PACKAGE/FIGURES/qr_site.png', Inches(11.3), Inches(5.2), width=Inches(1.4))
    note(s, notes)

prs.save('FINAL_SUBMISSION_PACKAGE/06_PRESENTATION/FINAL_BTECH_PRESENTATION.pptx')
print('pptx saved:', len(prs.slides.__iter__.__self__._sldIdLst), 'slides')
