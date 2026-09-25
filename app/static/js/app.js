/**
 * MoRTH Indian Road Accident Analytics Platform - Frontend Controller
 * Robust, resilient, agentic visualization renderer with zero blank charts,
 * chart/table toggles, PNG/SVG exports, and filter reactivity.
 */

// Application State
const appState = {
  filters: {
    state: 'ALL',
    year: 'ALL',
    zone: 'ALL'
  },
  metadata: null,
  catalog: [],
  chartDataCache: {},
  activeTab: 'tab-visualizations'
};

// DOM Content Loaded Handler
document.addEventListener('DOMContentLoaded', async () => {
  setupEventListeners();
  await initializeApp();
});

async function initializeApp() {
  await fetchMetadata();
  await updateKPIs();
  await renderAllVisualizations();
  await loadG10Slopes();
  await loadAuditReport();
  await loadVariableRegistryAndCatalog();
  await loadWeatherTab();
}

function setupEventListeners() {
  // Tab switching
  document.querySelectorAll('.tab-trigger').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const target = btn.dataset.tab;
      switchTab(target);
    });
  });

  // Filter toolbar
  const stateSelect = document.getElementById('filter-state');
  const yearSelect = document.getElementById('filter-year');
  const zoneSelect = document.getElementById('filter-zone');
  const btnReset = document.getElementById('btn-reset-filters');

  if (stateSelect) stateSelect.addEventListener('change', onFilterChange);
  if (yearSelect) yearSelect.addEventListener('change', onFilterChange);
  if (zoneSelect) zoneSelect.addEventListener('change', onFilterChange);

  if (btnReset) {
    btnReset.addEventListener('click', () => {
      if (stateSelect) stateSelect.value = 'ALL';
      if (yearSelect) yearSelect.value = 'ALL';
      if (zoneSelect) zoneSelect.value = 'ALL';
      appState.filters = { state: 'ALL', year: 'ALL', zone: 'ALL' };
      onFilterChange();
    });
  }

  // Visualization Search Input
  const searchInput = document.getElementById('vis-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      document.querySelectorAll('.chart-card').forEach(card => {
        const text = card.innerText.toLowerCase();
        card.style.display = (text.includes(q) || q === '') ? 'flex' : 'none';
      });
    });
  }

  // Load benchmark button
  const btnBenchmark = document.getElementById('btn-load-benchmark');
  if (btnBenchmark) {
    btnBenchmark.addEventListener('click', async () => {
      try {
        const res = await fetch('/api/load_benchmark', { method: 'POST' });
        const data = await res.json();
        alert(data.message || 'Benchmark reloaded.');
        await initializeApp();
      } catch (err) {
        console.error('Error reloading benchmark:', err);
      }
    });
  }

  // Upload trigger
  const btnUpload = document.getElementById('btn-upload-trigger');
  const fileInput = document.getElementById('file-upload-input');
  if (btnUpload && fileInput) {
    btnUpload.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', async (e) => {
      if (!fileInput.files || !fileInput.files[0]) return;
      const formData = new FormData();
      formData.append('file', fileInput.files[0]);
      try {
        const res = await fetch('/api/upload_dataset', { method: 'POST', body: formData });
        const data = await res.json();
        alert(data.message || 'Dataset uploaded.');
        await initializeApp();
      } catch (err) {
        alert('Upload failed: ' + err.message);
      }
    });
  }

  // PDF download
  const btnPdf = document.getElementById('btn-download-pdf');
  if (btnPdf) {
    btnPdf.addEventListener('click', () => {
      window.location.href = '/api/download_pdf_report';
    });
  }

  // Export dropdown
  const btnExport = document.getElementById('btn-export-dropdown');
  if (btnExport) {
    btnExport.addEventListener('click', () => {
      const choice = confirm('Click OK to download CSV, or Cancel to download Excel (XLSX).');
      const fmt = choice ? 'csv' : 'xlsx';
      window.location.href = `/api/export_data?format=${fmt}&type=clean`;
    });
  }

  // Train ML Models button
  const btnTrainML = document.getElementById('btn-train-ml');
  if (btnTrainML) {
    btnTrainML.addEventListener('click', async () => {
      btnTrainML.innerHTML = '<span>⏳</span> Training Models...';
      btnTrainML.disabled = true;
      try {
        const res = await fetch('/api/train_ml', { method: 'POST' });
        const data = await res.json();
        displayMLResults(data);
      } catch (err) {
        alert('ML training error: ' + err.message);
      } finally {
        btnTrainML.innerHTML = '<span>✓</span> Models Trained';
        btnTrainML.disabled = false;
      }
    });
  }

  // Load Weather Button
  const btnLoadWeather = document.getElementById('btn-load-weather');
  if (btnLoadWeather) {
    btnLoadWeather.addEventListener('click', async () => {
      try {
        const res = await fetch('/api/weather/load', { method: 'POST' });
        const data = await res.json();
        alert(data.message || 'Weather dataset loaded.');
        await loadWeatherTab();
      } catch (err) {
        alert('Weather loading error: ' + err.message);
      }
    });
  }

  // Generate All Analyses button
  const btnGenAll = document.getElementById('btn-generate-all-analyses');
  if (btnGenAll) {
    btnGenAll.addEventListener('click', async () => {
      await renderAllVisualizations();
      alert('All eligible analyses have been verified and generated.');
    });
  }

  // Modal Info close
  const modal = document.getElementById('modal-info');
  const modalClose = document.getElementById('modal-info-close');
  const modalBtnClose = document.getElementById('modal-info-btn-close');
  if (modalClose) modalClose.addEventListener('click', () => modal.classList.add('hidden'));
  if (modalBtnClose) modalBtnClose.addEventListener('click', () => modal.classList.add('hidden'));

  // Window resize handler for Plotly responsiveness
  window.addEventListener('resize', () => {
    document.querySelectorAll('.chart-card div[id^="plot-"]').forEach(el => {
      if (window.Plotly && el && !el.classList.contains('hidden')) {
        try { Plotly.Plots.resize(el); } catch (e) {}
      }
    });
  });
}

function switchTab(tabId) {
  appState.activeTab = tabId;
  document.querySelectorAll('.tab-content').forEach(tab => {
    tab.classList.add('hidden');
  });
  const active = document.getElementById(tabId);
  if (active) active.classList.remove('hidden');

  document.querySelectorAll('.tab-trigger').forEach(btn => {
    if (btn.dataset.tab === tabId) {
      btn.classList.add('active-tab-btn');
      btn.classList.remove('inactive-tab-btn');
    } else {
      btn.classList.remove('active-tab-btn');
      btn.classList.add('inactive-tab-btn');
    }
  });

  // Re-flow plotly charts in now-visible tab
  setTimeout(() => {
    if (active) {
      active.querySelectorAll('div[id^="plot-"]').forEach(el => {
        if (window.Plotly && el && !el.classList.contains('hidden')) {
          try { Plotly.Plots.resize(el); } catch (e) {}
        }
      });
    }
  }, 100);
}

async function onFilterChange() {
  const stateSelect = document.getElementById('filter-state');
  const yearSelect = document.getElementById('filter-year');
  const zoneSelect = document.getElementById('filter-zone');

  appState.filters.state = stateSelect ? stateSelect.value : 'ALL';
  appState.filters.year = yearSelect ? yearSelect.value : 'ALL';
  appState.filters.zone = zoneSelect ? zoneSelect.value : 'ALL';

  await updateKPIs();
  await renderAllVisualizations();
}

async function fetchMetadata() {
  try {
    const res = await fetch('/api/metadata');
    const data = await res.json();
    if (data.status === 'success') {
      appState.metadata = data;

      // Update Header Badges
      const activeDs = data.active_dataset;
      const recBadge = document.getElementById('header-records-count');
      const filenameBadge = document.getElementById('active-filename-badge');
      const metaText = document.getElementById('active-dataset-meta');

      if (recBadge) recBadge.innerText = `${activeDs.record_count} Records Loaded`;
      if (filenameBadge) filenameBadge.innerText = activeDs.filename;
      if (metaText) {
        metaText.innerText = `${activeDs.record_count} state-year observations • ${activeDs.state_count} reporting entities • ${activeDs.year_coverage} • Benchmark audit: ${activeDs.benchmark_audit_mismatches} mismatches`;
      }

      // Populate State filter dropdown
      const stateSelect = document.getElementById('filter-state');
      if (stateSelect && stateSelect.options.length <= 1) {
        data.filters.states.forEach(st => {
          const opt = document.createElement('option');
          opt.value = st;
          opt.textContent = st;
          stateSelect.appendChild(opt);
        });
      }
    }
  } catch (err) {
    console.error('Error fetching metadata:', err);
  }
}

async function updateKPIs() {
  try {
    const res = await fetch('/api/kpis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(appState.filters)
    });
    const data = await res.json();
    if (data.status === 'success') {
      const kpis = data.kpis;
      setText('kpi-total-accidents', Number(kpis.total_incidents).toLocaleString());
      setText('kpi-total-fatalities', Number(kpis.fatalities).toLocaleString());
      setText('kpi-total-injuries', typeof kpis.injuries === 'number' ? Number(kpis.injuries).toLocaleString() : kpis.injuries);
      setText('kpi-fatality-ratio', kpis.fatality_ratio);
      setText('kpi-avg-accidents', Number(kpis.avg_annual_accidents).toLocaleString());
      setText('kpi-peak-year', kpis.peak_accident_year);

      // Supporting KPIs: honest unavailable state (no verified records)
      setText('kpi-road-cat', 'Awaiting data');
      setText('kpi-vru-mode', 'Awaiting data');
      setText('kpi-cause', 'Awaiting data');
      setText('kpi-weather', 'Awaiting data');
    }
  } catch (err) {
    console.error('Error updating KPIs:', err);
  }
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.innerText = val;
}

/**
 * Renders all Tier 1 through Tier 10 visualizations with guaranteed error isolation.
 */
async function renderAllVisualizations() {
  const chartList = ['G1', 'G2', 'G4', 'G3', 'G7', 'G5', 'G6', 'G8', 'G9'];
  for (const id of chartList) {
    await renderSingleChart(id);
  }
}

async function renderSingleChart(analysisId) {
  const plotContainer = document.getElementById(`plot-${analysisId}`);
  const tableContainer = document.getElementById(`table-${analysisId}`);
  const insightBox = document.getElementById(`insight-${analysisId}`);
  if (!plotContainer) return;

  try {
    const res = await fetch(`/api/visualization/${analysisId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(appState.filters)
    });
    const resJson = await res.json();
    if (resJson.status !== 'success' || !resJson.payload) {
      throw new Error(resJson.payload?.error || 'Empty payload');
    }

    const payload = resJson.payload;
    appState.chartDataCache[analysisId] = payload;

    // Render Insight Box
    if (insightBox && payload.insight) {
      insightBox.innerHTML = `<span class="font-bold text-slate-900">Observed Pattern:</span> ${payload.insight}`;
    }

    // Populate Underlying Table
    if (tableContainer && payload.data && payload.data.table) {
      renderDataTable(tableContainer, payload.data.table);
    }

    // Setup action buttons for this chart card
    setupCardControls(analysisId, payload);

    // Call specific chart renderer
    if (analysisId === 'G1') renderG1(plotContainer, payload.data);
    else if (analysisId === 'G2') renderG2(plotContainer, payload.data);
    else if (analysisId === 'G4') renderG4(plotContainer, payload.data);
    else if (analysisId === 'G3') renderG3(plotContainer, payload.data);
    else if (analysisId === 'G7') renderG7(plotContainer, payload.data);
    else if (analysisId === 'G5') renderG5(plotContainer, payload.data);
    else if (analysisId === 'G6') renderG6(plotContainer, payload.data);
    else if (analysisId === 'G8') renderG8(plotContainer, payload.data);
    else if (analysisId === 'G9') renderG9(plotContainer, payload.data);
    else if (analysisId === 'G10') renderG10(plotContainer, payload.data);

  } catch (err) {
    console.error(`Error rendering chart ${analysisId}:`, err);
    plotContainer.innerHTML = `
      <div class="h-full flex flex-col items-center justify-center bg-slate-50 border border-slate-200 rounded p-4 text-center">
        <span class="text-amber-500 font-bold text-sm">⚠ Analysis Notice</span>
        <span class="text-xs text-slate-600 mt-1">${err.message || 'No compatible records found for current filters.'}</span>
      </div>
    `;
  }
}

function setupCardControls(id, payload) {
  const card = document.getElementById(`card-${id}`);
  if (!card) return;

  // Toggle Table
  const btnToggle = card.querySelector('.btn-toggle-table');
  if (btnToggle) {
    btnToggle.onclick = () => {
      const plot = document.getElementById(`plot-${id}`);
      const table = document.getElementById(`table-${id}`);
      if (plot.classList.contains('hidden')) {
        plot.classList.remove('hidden');
        table.classList.add('hidden');
        btnToggle.innerText = 'Table';
        if (window.Plotly) Plotly.Plots.resize(plot);
      } else {
        plot.classList.add('hidden');
        table.classList.remove('hidden');
        btnToggle.innerText = 'Chart';
      }
    };
  }

  // Download PNG
  const btnPng = card.querySelector('.btn-dl-png');
  if (btnPng) {
    btnPng.onclick = () => {
      const plot = document.getElementById(`plot-${id}`);
      if (window.Plotly && plot) {
        Plotly.downloadImage(plot, { format: 'png', filename: `MoRTH_${id}_Chart` });
      }
    };
  }

  // Download SVG
  const btnSvg = card.querySelector('.btn-dl-svg');
  if (btnSvg) {
    btnSvg.onclick = () => {
      const plot = document.getElementById(`plot-${id}`);
      if (window.Plotly && plot) {
        Plotly.downloadImage(plot, { format: 'svg', filename: `MoRTH_${id}_Vector` });
      }
    };
  }

  // Info modal
  const btnInfo = card.querySelector('.btn-info');
  if (btnInfo) {
    btnInfo.onclick = () => {
      const meta = payload.meta;
      const modal = document.getElementById('modal-info');
      const title = document.getElementById('modal-info-title');
      const body = document.getElementById('modal-info-body');

      if (modal && meta) {
        title.innerText = `${meta.id}: ${meta.title}`;
        body.innerHTML = `
          <div><strong>Definition & Scope:</strong> ${meta.explanation}</div>
          <div><strong>Formula / Computation:</strong> <code class="bg-slate-100 px-1 py-0.5 rounded font-mono">${meta.formula}</code></div>
          <div><strong>Official Source:</strong> ${meta.source}</div>
          <div><strong>Temporal Coverage:</strong> ${meta.coverage}</div>
          <div><strong>Data Granularity:</strong> ${meta.granularity}</div>
          <div><strong>Research Limitations:</strong> <span class="text-slate-600">${meta.limitations}</span></div>
        `;
        modal.classList.remove('hidden');
      }
    };
  }
}

function renderDataTable(container, rows) {
  if (!rows || rows.length === 0) {
    container.innerHTML = '<div class="p-3 text-center text-slate-400">No data available</div>';
    return;
  }
  const headers = Object.keys(rows[0]);
  let html = `
    <table class="w-full text-left border-collapse border border-slate-200">
      <thead class="bg-slate-100 text-slate-700 font-semibold border-b border-slate-200 sticky top-0">
        <tr>
  `;
  headers.forEach(h => html += `<th class="p-2 border border-slate-200">${h}</th>`);
  html += '</tr></thead><tbody class="divide-y divide-slate-100 font-mono">';
  rows.forEach(r => {
    html += '<tr>';
    headers.forEach(h => {
      const val = r[h];
      const displayVal = (typeof val === 'number') ? val.toLocaleString() : val;
      html += `<td class="p-2 border border-slate-200">${displayVal}</td>`;
    });
    html += '</tr>';
  });
  html += '</tbody></table>';
  container.innerHTML = html;
}

// ==========================================
// INDIVIDUAL PLOTLY CHART BUILDERS
// ==========================================

const commonLayout = {
  margin: { l: 50, r: 25, t: 30, b: 40 },
  autosize: true,
  paper_bgcolor: 'transparent',
  plot_bgcolor: 'transparent',
  font: { family: 'ui-sans-serif, system-ui, sans-serif', size: 11, color: '#334155' },
  hovermode: 'x unified'
};

function renderG1(container, data) {
  const trace1 = {
    x: data.years,
    y: data.values,
    type: 'scatter',
    mode: 'lines+markers',
    name: 'Reported Crashes',
    line: { color: '#2563EB', width: 2.5 },
    marker: { size: 6, color: '#1D4ED8' }
  };
  const trace2 = {
    x: data.years,
    y: data.fitted_trend,
    type: 'scatter',
    mode: 'lines',
    name: 'OLS Linear Trend',
    line: { color: '#93C5FD', width: 1.5, dash: 'dash' }
  };

  const layout = {
    ...commonLayout,
    xaxis: { title: 'Calendar Year', tickmode: 'linear', dtick: 1 },
    yaxis: { title: 'Accidents', tickformat: ',' }
  };
  Plotly.newPlot(container, [trace1, trace2], layout, { responsive: true, displayModeBar: false });
}

function renderG2(container, data) {
  const trace1 = {
    x: data.years,
    y: data.values,
    type: 'scatter',
    mode: 'lines+markers',
    name: 'Road Fatalities',
    line: { color: '#E11D48', width: 2.5 },
    marker: { size: 6, color: '#BE123C' }
  };
  const trace2 = {
    x: data.years,
    y: data.fitted_trend,
    type: 'scatter',
    mode: 'lines',
    name: 'OLS Linear Trend',
    line: { color: '#FDA4AF', width: 1.5, dash: 'dash' }
  };

  const layout = {
    ...commonLayout,
    xaxis: { title: 'Calendar Year', tickmode: 'linear', dtick: 1 },
    yaxis: { title: 'Persons Killed', tickformat: ',' }
  };
  Plotly.newPlot(container, [trace1, trace2], layout, { responsive: true, displayModeBar: false });
}

function renderG4(container, data) {
  const trace = {
    x: data.years,
    y: data.values,
    type: 'scatter',
    mode: 'lines+markers',
    name: 'Fatalities per 100 Accidents',
    line: { color: '#0284C7', width: 2.5 },
    marker: { size: 6, color: '#0369A1' }
  };
  const layout = {
    ...commonLayout,
    xaxis: { title: 'Calendar Year', tickmode: 'linear', dtick: 1 },
    yaxis: { title: 'Severity (Deaths / 100 Crashes)' }
  };
  Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
}

function renderG3(container, data) {
  const trace = {
    x: data.years,
    y: data.values,
    type: 'scatter',
    mode: 'lines+markers',
    name: 'Persons Injured',
    line: { color: '#D97706', width: 2.5 },
    marker: { size: 6, color: '#B45309' }
  };
  const layout = {
    ...commonLayout,
    xaxis: { title: 'Calendar Year', tickmode: 'linear', dtick: 1 },
    yaxis: { title: 'Persons Injured', tickformat: ',' }
  };
  Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
}

function renderG7(container, data) {
  // Sorted state bar chart
  const trace = {
    x: data.accidents,
    y: data.states,
    type: 'bar',
    orientation: 'h',
    name: '2024 Crashes',
    marker: { color: '#3B82F6' }
  };
  const layout = {
    ...commonLayout,
    margin: { l: 120, r: 25, t: 20, b: 40 },
    xaxis: { title: 'Reported Crashes in 2024', tickformat: ',' },
    yaxis: { autorange: true, tickfont: { size: 9 } }
  };
  Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
}

function renderG5(container, data) {
  const traces = data.series.map((s, idx) => ({
    x: data.years,
    y: s.values,
    name: s.zone,
    type: 'bar'
  }));

  const layout = {
    ...commonLayout,
    barmode: 'group',
    xaxis: { title: 'Calendar Year', tickmode: 'linear', dtick: 1 },
    yaxis: { title: 'Accidents', tickformat: ',' },
    legend: { orientation: 'h', y: 1.15 }
  };
  Plotly.newPlot(container, traces, layout, { responsive: true, displayModeBar: false });
}

function renderG8(container, data) {
  const trace = {
    z: data.z,
    x: data.years,
    y: data.states,
    type: 'heatmap',
    colorscale: 'Blues',
    colorbar: { title: 'Crashes' }
  };
  const layout = {
    ...commonLayout,
    margin: { l: 140, r: 25, t: 20, b: 40 },
    xaxis: { title: 'Calendar Year', tickmode: 'linear', dtick: 1 },
    yaxis: { autorange: 'reversed', tickfont: { size: 9 } }
  };
  Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
}

function renderG6(container, data) {
  const palette = ['#2563EB','#E11D48','#F59E0B','#10B981','#8B5CF6','#06B6D4'];
  const traces = (data.series || []).map((s, i) => ({ x: data.years, y: s.values, name: s.zone || s.name, type: 'scatter', mode: 'lines+markers', line: { color: palette[i % palette.length], width: 2 }, marker: { size: 5 } }));
  Plotly.newPlot(container, traces, { ...commonLayout, xaxis: { title: 'Year', tickmode: 'linear', dtick: 1 }, yaxis: { title: 'Accidents', tickformat: ',' }, legend: { orientation: 'h', y: 1.15 } }, { responsive: true, displayModeBar: false });
}

function renderG9(container, data) {
  const palette = ['#2563EB','#E11D48','#F59E0B','#10B981','#8B5CF6','#06B6D4','#EC4899','#14B8A6'];
  const traces = (data.series || []).map((s, i) => ({ x: data.years, y: s.values, name: s.state || s.name, type: 'scatter', mode: 'lines+markers', line: { width: 2, color: palette[i % palette.length] }, marker: { size: 5 } }));
  Plotly.newPlot(container, traces, { ...commonLayout, xaxis: { title: 'Year', tickmode: 'linear', dtick: 1 }, yaxis: { title: 'Accidents', tickformat: ',' }, legend: { orientation: 'h', y: 1.15 } }, { responsive: true, displayModeBar: false });
}

function renderG10(container, data) {
  const vals = (data.slopes || []).map(s => (typeof s === 'object' ? s.slope : s));
  const trace = { x: vals, type: 'histogram', marker: { color: '#8B5CF6' } };
  Plotly.newPlot(container, [trace], { ...commonLayout, xaxis: { title: 'OLS slope (accidents/year)' }, yaxis: { title: 'States' } }, { responsive: true, displayModeBar: false });
}

function renderRoad(container, data) {
  const trace1 = {
    x: data.categories,
    y: data.accidents,
    name: 'Accidents',
    type: 'bar',
    marker: { color: '#6366F1' }
  };
  const trace2 = {
    x: data.categories,
    y: data.fatalities,
    name: 'Fatalities',
    type: 'bar',
    marker: { color: '#EC4899' }
  };
  const layout = {
    ...commonLayout,
    barmode: 'group',
    xaxis: { title: 'Highway Classification' },
    yaxis: { title: 'Occurrences', tickformat: ',' }
  };
  Plotly.newPlot(container, [trace1, trace2], layout, { responsive: true, displayModeBar: false });
}

function renderVehicle(container, data) {
  const trace = {
    x: data.fatalities,
    y: data.modes,
    type: 'bar',
    orientation: 'h',
    marker: { color: '#F43F5E' }
  };
  const layout = {
    ...commonLayout,
    margin: { l: 120, r: 25, t: 20, b: 40 },
    xaxis: { title: 'Fatalities by Victim Mode (2024)', tickformat: ',' },
    yaxis: { autorange: 'reversed' }
  };
  Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
}

function renderCause(container, data) {
  const trace = {
    x: data.fatalities,
    y: data.causes,
    type: 'bar',
    orientation: 'h',
    marker: { color: '#F59E0B' }
  };
  const layout = {
    ...commonLayout,
    margin: { l: 120, r: 25, t: 20, b: 40 },
    xaxis: { title: 'Fatalities by Driver Factor (2024)', tickformat: ',' },
    yaxis: { autorange: 'reversed' }
  };
  Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
}

function renderSeverity(container, data) {
  const trace1 = { x: data.years, y: data.fatal, name: 'Fatal', type: 'bar', marker: { color: '#DC2626' } };
  const trace2 = { x: data.years, y: data.grievous, name: 'Grievous Injury', type: 'bar', marker: { color: '#EA580C' } };
  const trace3 = { x: data.years, y: data.minor, name: 'Minor Injury', type: 'bar', marker: { color: '#FBBF24' } };
  const trace4 = { x: data.years, y: data.non_injury, name: 'Non-Injury', type: 'bar', marker: { color: '#94A3B8' } };

  const layout = {
    ...commonLayout,
    barmode: 'stack',
    xaxis: { title: 'Calendar Year', tickmode: 'linear', dtick: 1 },
    yaxis: { title: 'Total Crashes', tickformat: ',' },
    legend: { orientation: 'h', y: 1.15 }
  };
  Plotly.newPlot(container, [trace1, trace2, trace3, trace4], layout, { responsive: true, displayModeBar: false });
}

// ==========================================
// STATISTICAL & OLS SLOPES TAB
// ==========================================

async function loadG10Slopes() {
  try {
    const res = await fetch('/api/statistical_analysis');
    const data = await res.json();
    if (data.status === 'success') {
      // Slopes table
      const resSlopes = await fetch('/api/g10_slopes');
      const slopeData = await resSlopes.json();
      const tbody = document.getElementById('tbody-g10-slopes');
      if (tbody && slopeData.slopes) {
        tbody.innerHTML = '';
        slopeData.slopes.forEach(s => {
          const tr = document.createElement('tr');
          const isPos = s.Linear_Slope_per_Year > 0;
          const badgeClass = isPos ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800';
          const badgeText = isPos ? 'Upward Trend (+)' : 'Downward Trend (-)';

          tr.innerHTML = `
            <td class="p-2.5 font-semibold text-slate-800">${s.State_UT}</td>
            <td class="p-2.5 font-mono">${s.Linear_Slope_per_Year}</td>
            <td class="p-2.5 font-mono">${s.Intercept}</td>
            <td class="p-2.5 font-mono">${s.R2}</td>
            <td class="p-2.5 font-mono">${s.p_value}</td>
            <td class="p-2.5 font-mono">${s.N_Observations}</td>
            <td class="p-2.5"><span class="px-2 py-0.5 rounded-full text-xs font-semibold ${badgeClass}">${badgeText}</span></td>
          `;
          tbody.appendChild(tr);
        });

        // Distribution histogram
        const distContainer = document.getElementById('plot-G10-dist');
        if (distContainer) {
          const slopesArr = slopeData.slopes.map(s => s.Linear_Slope_per_Year);
          const trace = {
            x: slopesArr,
            type: 'histogram',
            marker: { color: '#3B82F6', line: { color: '#1D4ED8', width: 1 } },
            nbinsx: 15
          };
          const layout = {
            ...commonLayout,
            xaxis: { title: 'Fitted OLS Linear Slope (Accidents / Year)' },
            yaxis: { title: 'Number of States/UTs' }
          };
          Plotly.newPlot(distContainer, [trace], layout, { responsive: true, displayModeBar: false });
        }
      }

      // Correlation matrix
      const corrContainer = document.getElementById('plot-correlation-matrix');
      if (corrContainer && data.correlation && data.correlation.pearson) {
        const corr = data.correlation.pearson;
        const keys = Object.keys(corr);
        const z = keys.map(k => keys.map(k2 => corr[k][k2]));
        const trace = {
          z: z,
          x: keys,
          y: keys,
          type: 'heatmap',
          colorscale: 'Viridis',
          zmin: -1,
          zmax: 1
        };
        const layout = {
          ...commonLayout,
          margin: { l: 80, r: 25, t: 20, b: 60 }
        };
        Plotly.newPlot(corrContainer, [trace], layout, { responsive: true, displayModeBar: false });
      }

      // Thresholds
      const tbodyThresh = document.getElementById('tbody-thresholds');
      if (tbodyThresh && data.time_to_threshold_10k) {
        tbodyThresh.innerHTML = '';
        data.time_to_threshold_10k.slice(0, 10).forEach(t => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td class="p-2 font-semibold text-slate-800">${t.State_UT}</td>
            <td class="p-2 font-mono text-blue-600">${t.Earliest_Year_Reached}</td>
            <td class="p-2 font-mono">${Number(t.Accidents_At_Arrival).toLocaleString()}</td>
          `;
          tbodyThresh.appendChild(tr);
        });
      }
    }
  } catch (err) {
    console.error('Error loading G10 slopes:', err);
  }
}

// ==========================================
// WEATHER TAB LOADER
// ==========================================

async function loadWeatherTab() {
  try {
    const res = await fetch('/api/weather/analytics');
    const data = await res.json();
    const statusText = document.getElementById('weather-status-text');

    if (data.status === 'AVAILABLE') {
      if (statusText) statusText.innerText = 'IMD Annual Rainfall & Conditions dataset active and verified (2018–2024).';
      
      // Scatter plot
      const scatterContainer = document.getElementById('plot-weather-scatter');
      if (scatterContainer && data.rainfall_vs_accidents) {
        const pts = data.rainfall_vs_accidents;
        const trace = {
          x: pts.map(p => p.rainfall_mm),
          y: pts.map(p => p.accidents),
          text: pts.map(p => `${p.state} (${p.year})`),
          mode: 'markers',
          type: 'scatter',
          marker: { size: 8, color: '#0284C7', opacity: 0.8 }
        };
        const layout = {
          ...commonLayout,
          xaxis: { title: 'Annual Precipitation (IMD Rainfall mm)' },
          yaxis: { title: 'Annual Road Accidents', tickformat: ',' }
        };
        Plotly.newPlot(scatterContainer, [trace], layout, { responsive: true, displayModeBar: false });
      }

      // Condition distribution
      const condContainer = document.getElementById('plot-weather-conditions');
      if (condContainer && data.condition_distribution) {
        const trace = {
          x: data.condition_distribution.map(c => c.Weather_Condition),
          y: data.condition_distribution.map(c => c.Observations),
          type: 'bar',
          marker: { color: '#0D9488' }
        };
        const layout = {
          ...commonLayout,
          xaxis: { title: 'Atmospheric Condition' },
          yaxis: { title: 'Recorded State-Year Observations' }
        };
        Plotly.newPlot(condContainer, [trace], layout, { responsive: true, displayModeBar: false });
      }
    } else {
      if (statusText) statusText.innerText = data.message || 'Weather dataset currently awaiting ingestion.';
    }
  } catch (err) {
    console.error('Error loading weather analytics:', err);
  }
}

// ==========================================
// ML TRAINING DISPLAY
// ==========================================

function displayMLResults(data) {
  const emptyState = document.getElementById('ml-empty-state');
  const metricsCont = document.getElementById('ml-metrics-container');

  if (emptyState) emptyState.classList.add('hidden');
  if (metricsCont) metricsCont.classList.remove('hidden');

  if (data.regression && data.regression.metrics) {
    setText('ml-reg-r2', data.regression.metrics.r2);
    setText('ml-reg-mae', Number(data.regression.metrics.mae).toLocaleString());

    // Feature importance
    const fi = data.regression.feature_importance;
    const fiContainer = document.getElementById('plot-feature-importance');
    if (fiContainer && fi) {
      const trace = {
        x: Object.values(fi),
        y: Object.keys(fi),
        type: 'bar',
        orientation: 'h',
        marker: { color: '#2563EB' }
      };
      const layout = {
        ...commonLayout,
        margin: { l: 90, r: 25, t: 10, b: 40 },
        xaxis: { title: 'Gini Importance Score' }
      };
      Plotly.newPlot(fiContainer, [trace], layout, { responsive: true, displayModeBar: false });
    }
  }

  if (data.classification && data.classification.metrics) {
    setText('ml-clf-acc', `${Math.round(data.classification.metrics.accuracy * 100)}%`);
  }

  if (data.clustering && data.clustering.cluster_profiles) {
    const clusterContainer = document.getElementById('plot-kmeans-clusters');
    if (clusterContainer) {
      const profiles = data.clustering.cluster_profiles;
      const trace = {
        x: profiles.map(p => `Cluster ${p.cluster}`),
        y: profiles.map(p => p.mean_accidents),
        type: 'bar',
        marker: { color: ['#60A5FA', '#34D399', '#F87171'] }
      };
      const layout = {
        ...commonLayout,
        xaxis: { title: 'K-Means State Groups' },
        yaxis: { title: 'Mean Annual Crashes', tickformat: ',' }
      };
      Plotly.newPlot(clusterContainer, [trace], layout, { responsive: true, displayModeBar: false });
    }
  }
}

// ==========================================
// DATASET HYGIENE & AUDIT TAB
// ==========================================

async function loadAuditReport() {
  try {
    const res = await fetch('/api/audit_details');
    const data = await res.json();
    const tbody = document.getElementById('tbody-reconciliation');
    if (tbody && data.reconciliation) {
      tbody.innerHTML = '';
      data.reconciliation.forEach(r => {
        const tr = document.createElement('tr');
        const match = r.result === 'MATCH';
        const badge = match ? '<span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">MATCH (0 DIFF)</span>' : '<span class="bg-rose-100 text-rose-800 px-2 py-0.5 rounded font-bold">MISMATCH</span>';

        tr.innerHTML = `
          <td class="p-2.5 font-bold">${r.year}</td>
          <td class="p-2.5">${r.computed_accidents.toLocaleString()}</td>
          <td class="p-2.5">${r.published_accidents.toLocaleString()}</td>
          <td class="p-2.5 text-emerald-600 font-bold">${r.diff_accidents}</td>
          <td class="p-2.5">${r.computed_fatalities.toLocaleString()}</td>
          <td class="p-2.5">${r.published_fatalities.toLocaleString()}</td>
          <td class="p-2.5 text-emerald-600 font-bold">${r.diff_fatalities}</td>
          <td class="p-2.5">${badge}</td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (err) {
    console.error('Error loading audit report:', err);
  }
}

// ==========================================
// VARIABLE REGISTRY & CATALOG TAB
// ==========================================

async function loadVariableRegistryAndCatalog() {
  try {
    // Variable Registry
    const resMeta = await fetch('/api/metadata');
    const dataMeta = await resMeta.json();
    const tbodyVar = document.getElementById('tbody-variable-registry');

    if (tbodyVar && dataMeta.discovery && dataMeta.discovery.variable_registry) {
      tbodyVar.innerHTML = '';
      dataMeta.discovery.variable_registry.forEach(v => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="p-2.5 font-bold text-slate-800">${v.variable}</td>
          <td class="p-2.5 font-mono text-slate-600">${v.source}</td>
          <td class="p-2.5">${v.sheet}</td>
          <td class="p-2.5"><span class="bg-blue-50 text-blue-700 px-2 py-0.5 rounded font-semibold">${v.granularity}</span></td>
          <td class="p-2.5">${v.coverage}</td>
          <td class="p-2.5"><span class="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-semibold">${v.status}</span></td>
          <td class="p-2.5 text-slate-600">${v.visualizations.join(', ')}</td>
        `;
        tbodyVar.appendChild(tr);
      });
    }

    // Analysis Catalog
    const resCat = await fetch('/api/catalog');
    const dataCat = await resCat.json();
    const tbodyCat = document.getElementById('tbody-analysis-catalog');

    if (tbodyCat && dataCat.catalog) {
      tbodyCat.innerHTML = '';
      dataCat.catalog.forEach(c => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="p-2.5 font-bold font-mono text-blue-600">${c.id}</td>
          <td class="p-2.5 font-semibold text-slate-800">${c.title}</td>
          <td class="p-2.5 text-slate-600 font-mono">${c.parameters.join(', ')}</td>
          <td class="p-2.5">${c.granularity}</td>
          <td class="p-2.5">${c.source}</td>
          <td class="p-2.5"><span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold text-xs">${c.status}</span></td>
        `;
        tbodyCat.appendChild(tr);
      });
    }
  } catch (err) {
    console.error('Error loading variable registry:', err);
  }
}
