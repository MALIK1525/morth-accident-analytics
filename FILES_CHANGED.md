# Files Changed — Website Phase 1

| File | Reason | Change | Research Impact | Test Coverage |
|---|---|---|---|---|
| app/static/js/app.js | SVG export silently failed (no promise handling) | Added `.catch` + explicit user message; fallback message when Plotly not loaded | None | Manual code review; export path unchanged |
| (pycache removed) | Stale `__pycache__` contained pre-fix hardcoded strings | Deleted all `__pycache__` dirs | None | 28/28 pytest pass |

No research values, methodology, or datasets modified.
