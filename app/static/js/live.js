/* Phase 13.2–13.3 Live Monitor frontend. Backend proxies all provider APIs. */
const REFRESH_MS = 5 * 60 * 1000;
let map, weatherLayer, trafficLayer, incidentLayer;
let weatherPoints = [], trafficPoints = [], incidentPoints = [];
let weatherMarkers = {};

function highlightMarker(marker) {
  document.querySelectorAll('#live-map .wx-selected').forEach(el => el.classList.remove('wx-selected'));
  const el = marker && marker.getElement ? marker.getElement().querySelector('.wx-marker') : null;
  if (el) el.classList.add('wx-selected');
}

const TRAFFIC_DASH = { 'solid': '', 'dash': '6 4', 'dot': '2 3', 'dashdot': '8 3 2 3' };
const layerEpoch = { weather: null, traffic: null, incidents: null };

function ageStr(epoch) {
  if (!epoch) return '—';
  const s = Math.max(0, Math.round((Date.now() - epoch) / 1000));
  if (s < 60) return s + 's ago';
  return Math.floor(s / 60) + ' min ago';
}
function tickAges() {
  const el = document.getElementById('layer-ages');
  if (el) el.innerText = `Freshness: weather ${ageStr(layerEpoch.weather)} · traffic ${ageStr(layerEpoch.traffic)} · incidents ${ageStr(layerEpoch.incidents)}`;
}
setInterval(tickAges, 30000);

function drawHazards() {
  const box = document.getElementById('hazards');
  if (!box) return;
  const out = [];
  trafficPoints.forEach(p => {
    if (p.road_closure) out.push(`⛔ Reported road closure near ${p.name} (TomTom flow feed)`);
    else if (p.condition === 'Very heavy' || p.condition === 'Heavy') out.push(`🚦 ${p.condition} congestion near ${p.name} (TomTom flow feed)`);
  });
  weatherPoints.forEach(p => {
    if (p.condition === 'Thunderstorm') out.push(`⛈ Thunderstorm observed at ${p.name} (Open-Meteo)`);
    else if (p.condition === 'Fog') out.push(`🌫 Fog observed at ${p.name} (Open-Meteo)`);
    else if (typeof p.precipitation_mm === 'number' && p.precipitation_mm >= 5) out.push(`🌧 Heavy rain observed at ${p.name}: ${p.precipitation_mm} mm (Open-Meteo)`);
  });
  incidentPoints.slice(0, 300).forEach(p => {
    if (p.category === 'Road closed' || p.category === 'Flooding') out.push(`⚠ ${p.category}: ${p.road || 'location undisclosed'} (TomTom incidents)`);
  });
  box.innerHTML = out.length ? out.slice(0, 20).map(h => `<div>• ${h}</div>`).join('') : 'No hazards currently derived from loaded live feeds.';
}

function fmt(v, suffix, digits) {
  if (v === null || v === undefined) return 'Not available';
  const n = Number(v);
  if (Number.isNaN(n)) return 'Not available';
  return (digits !== undefined ? n.toFixed(digits) : n) + (suffix || '');
}

function showDetail(p) {
  const el = document.getElementById('weather-detail');
  document.getElementById('detail-sub').innerText = '— ' + p.name;
  el.innerHTML =
    `<div class="text-lg font-bold">${p.icon} ${p.name} <span class="text-sm font-normal">(${p.condition})</span></div>` +
    `<div>Temperature: <b>${fmt(p.temperature_c, '°C', 1)}</b></div>` +
    `<div>Rain: <b>${fmt(p.precipitation_mm, ' mm', 1)}</b></div>` +
    `<div>Humidity: <b>${fmt(p.humidity_pct, '%', 0)}</b></div>` +
    `<div>Wind: <b>${fmt(p.wind_speed_kmh, ' km/h', 1)}</b> ${p.wind_direction_deg !== null && p.wind_direction_deg !== undefined ? '(' + p.wind_direction_deg + '°)' : ''}</div>` +
    `<div>Visibility: <b>${p.visibility_m !== null && p.visibility_m !== undefined ? (p.visibility_m / 1000).toFixed(1) + ' km' : 'Not available'}</b></div>` +
    `<div>Observed: <b>${p.observed_at || 'Not available'}</b></div>` +
    `<div>Source: <b>${p.source || 'Open-Meteo'}</b></div>`;
}

async function loadLive(force) {
  const badge = document.getElementById('badge-weather');
  try {
    const res = await fetch('/api/live/weather/summary' + (force ? '?refresh=1' : ''));
    const data = await res.json();
    if (data.status !== 'success' || !data.points || !data.points.length) throw new Error('empty');
    if (!map) {
      map = L.map('live-map').setView([22.5, 79.5], 5);
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        { maxZoom: 12, attribution: '© OpenStreetMap contributors' }).addTo(map);
      weatherLayer = L.layerGroup().addTo(map);
      trafficLayer = L.layerGroup().addTo(map);
      incidentLayer = L.layerGroup().addTo(map);
      wireToggles();
      if (typeof initIndiaMap === 'function') initIndiaMap().catch(e => console.error('State boundaries unavailable:', e));
      if (typeof wireStateSearch === 'function') wireStateSearch();
      if (typeof wireNearMe === 'function') wireNearMe();
    } else { weatherLayer.clearLayers(); }
    weatherPoints = data.points;
    drawWeather();
    drawHazards();
    layerEpoch.weather = Date.now(); tickAges();
    fillCityFilter();
    const s = data.summary;
    document.getElementById('kpi-locs').innerText = s.locations_monitored;
    document.getElementById('kpi-rain').innerText = s.rain_affected;
    document.getElementById('kpi-avg').innerText = fmt(s.avg_temp_c, '°C', 1);
    document.getElementById('kpi-range').innerText =
      (s.max_temp_c !== null ? s.max_temp_c + '° / ' + s.min_temp_c + '°C' : '—');
    document.getElementById('live-clock').innerText = 'Last updated: ' + data.fetched_at + (data.cached ? ' (cached)' : '');
    badge.className = 'text-[11px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800';
    badge.innerText = '🟢 LIVE Source: Open-Meteo Updated: ' + data.fetched_at;
    if (data.stale) {
      badge.className = 'text-[11px] px-2 py-0.5 rounded bg-amber-100 text-amber-800';
      badge.innerText = '🟡 STALE — ' + (data.stale_note || ('last successful update ' + data.fetched_at));
    }
    if (data.failed && data.failed.length) {
      badge.innerText += ` (${data.failed.length} location(s) unavailable)`;
    }
  } catch (e) {
    console.error('Live weather failed:', e);
    badge.className = 'text-[11px] px-2 py-0.5 rounded bg-rose-100 text-rose-800';
    badge.innerText = '🔴 Weather temporarily unavailable';
    const prev = document.getElementById('live-clock').innerText;
    if (prev === 'Last updated: —') document.getElementById('live-clock').innerText = 'Weather temporarily unavailable';
  }
}

function wireToggles() {
  const apply = () => {
    if (!map) return;
    const w = document.getElementById('lyr-weather').checked;
    const t = document.getElementById('lyr-traffic').checked;
    const ii = document.getElementById('lyr-incidents').checked;
    [ [weatherLayer, w], [trafficLayer, t], [incidentLayer, ii] ].forEach(([lyr, on]) => {
      if (on && !map.hasLayer(lyr)) lyr.addTo(map);
      if (!on && map.hasLayer(lyr)) map.removeLayer(lyr);
    });
  };
  ['lyr-weather', 'lyr-traffic', 'lyr-incidents'].forEach(id =>
    document.getElementById(id).addEventListener('change', apply));
  ['flt-city', 'flt-inc', 'flt-traf'].forEach(id =>
    document.getElementById(id).addEventListener('change', () => { drawWeather(); drawTraffic(); drawIncidents(); }));
}

function passFilters(p, kind) {
  const city = document.getElementById('flt-city').value;
  if (city && p.name !== city) return false;
  if (kind === 'traffic') {
    const t = document.getElementById('flt-traf').value;
    if (t && p.condition !== t) return false;
  }
  if (kind === 'incident') {
    const t = document.getElementById('flt-inc').value;
    if (t && p.category !== t) return false;
  }
  return true;
}

function drawWeather() {
  if (!weatherLayer) return;
  weatherLayer.clearLayers();
  weatherMarkers = {};
  weatherPoints.filter(p => passFilters(p)).forEach(p => {
    const icon = L.divIcon({
      className: '',
      html: `<div class="wx-marker wx-${p.shape}"><span>${p.icon}</span></div>`,
      iconSize: [34, 34]
    });
    const m = L.marker([p.lat, p.lon], { icon });
    m.bindTooltip(`<b>${p.name}</b><br>${p.condition}<br>${fmt(p.temperature_c, '°C', 1)}`);
    m.on('click', () => { highlightMarker(m); showDetail(p); });
    weatherMarkers[p.name] = m;
    weatherLayer.addLayer(m);
  });
}

function fillCityFilter() {
  const sel = document.getElementById('flt-city');
  const cur = sel.value;
  sel.innerHTML = '<option value="">All</option>' + weatherPoints.map(p => `<option>${p.name}</option>`).join('');
  sel.value = cur;
  const chips = document.getElementById('city-chips');
  if (chips) {
    chips.innerHTML = '';
    weatherPoints.forEach(p => {
      const b = document.createElement('button');
      b.className = 'city-chip';
      b.innerText = `${p.icon} ${p.name} ${fmt(p.temperature_c, '°C', 0)}`;
      b.setAttribute('aria-label', `Show weather for ${p.name}`);
      b.addEventListener('click', () => {
        showDetail(p);
        const m = weatherMarkers[p.name];
        if (m) { map.panTo(m.getLatLng()); highlightMarker(m); }
      });
      chips.appendChild(b);
    });
  }
}

async function loadTraffic(force) {
  const badge = document.getElementById('badge-traffic');
  const sec = document.getElementById('sec-traffic');
  const secI = document.getElementById('sec-incidents');
  try {
    const res = await fetch('/api/live/traffic/flow' + (force ? '?refresh=1' : ''));
    const data = await res.json();
    if (data.status === 'awaiting_key') {
      badge.className = 'text-[11px] px-2 py-0.5 rounded bg-amber-100 text-amber-800';
      badge.innerText = '🟡 Traffic: Awaiting API key';
      sec.innerText = '🟡 awaiting traffic API key — set TOMTOM_API_KEY in server environment (Render → Environment) to enable; weather and map unaffected';
      secI.innerText = '🟡 awaiting traffic API key (server configuration pending)';
      return;
    }
    if (data.status !== 'success' || !data.points) throw new Error('empty');
    trafficPoints = data.points;
    drawTraffic();
    drawHazards();
    layerEpoch.traffic = Date.now(); tickAges();
    badge.className = 'text-[11px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800';
    badge.innerText = '🟢 LIVE Source: TomTom Updated: ' + data.fetched_at + (data.cached ? ' (cached)' : '');
    sec.innerText = '🟢 live (TomTom)';
  } catch (e) {
    console.error('Live traffic failed:', e);
    badge.className = 'text-[11px] px-2 py-0.5 rounded bg-rose-100 text-rose-800';
    badge.innerText = '🔴 Traffic temporarily unavailable';
    if (sec) sec.innerText = '🔴 temporarily unavailable (weather unaffected)';
  }
}

function drawTraffic() {
  if (!trafficLayer) return;
  trafficLayer.clearLayers();
  trafficPoints.filter(p => passFilters(p, 'traffic')).forEach(p => {
    const html = `<div class="wx-marker wx-circle" title="${p.condition}"><span style="font-weight:bold">${(p.condition || '?')[0]}</span></div>`;
    const m = L.marker([p.lat, p.lon], { icon: L.divIcon({ className: '', html, iconSize: [30, 30] }) });
    m.bindTooltip(`<b>${p.name} — ${p.condition}</b><br>Current: ${fmt(p.current_speed_kmh, ' km/h', 0)}<br>Free-flow: ${fmt(p.free_flow_speed_kmh, ' km/h', 0)}<br>Delay: ${fmt(p.delay_s, ' s', 0)}`);
    m.on('click', () => {
      highlightMarker(m);
      document.getElementById('detail-sub').innerText = '— ' + p.name + ' traffic';
      document.getElementById('weather-detail').innerHTML =
        `<div class="text-lg font-bold">${p.name} traffic — ${p.condition}</div>` +
        `<div>Current speed: <b>${fmt(p.current_speed_kmh, ' km/h', 0)}</b></div>` +
        `<div>Free-flow speed: <b>${fmt(p.free_flow_speed_kmh, ' km/h', 0)}</b></div>` +
        `<div>Travel time: <b>${fmt(p.travel_time_s, ' s', 0)}</b></div>` +
        `<div>Delay: <b>${fmt(p.delay_s, ' s', 0)}</b></div>` +
        `<div>Road closure reported: <b>${p.road_closure ? 'YES' : 'no'}</b></div>` +
        `<div>Source: <b>TomTom Traffic API</b></div>`;
    });
    trafficLayer.addLayer(m);
    if (p.current_speed_kmh !== null && p.current_speed_kmh !== undefined) {
      L.circle([p.lat, p.lon], { radius: 22000, color: '#111827', weight: p.line_weight || 2,
        dashArray: TRAFFIC_DASH[p.line_dash] || '', fill: false }).addTo(trafficLayer);
    }
  });
}

async function loadIncidents(force) {
  const secI = document.getElementById('sec-incidents');
  try {
    const res = await fetch('/api/live/traffic/incidents' + (force ? '?refresh=1' : ''));
    const data = await res.json();
    if (data.status === 'awaiting_key') { if (secI) secI.innerText = '🟡 awaiting traffic API key (server configuration pending)'; return; }
    if (data.status !== 'success') throw new Error('empty');
    incidentPoints = (data.points || []).filter(p => p.lat !== null && p.lon !== null);
    drawIncidents();
    drawHazards();
    layerEpoch.incidents = Date.now(); tickAges();
    fillIncidentFilter();
    if (secI) secI.innerText = `🟢 live — ${incidentPoints.length} reported incident(s) (TomTom, NOT official records)`;
  } catch (e) {
    console.error('Live incidents failed:', e);
    if (secI) secI.innerText = '🔴 temporarily unavailable (weather unaffected)';
  }
}

function drawIncidents() {
  if (!incidentLayer) return;
  incidentLayer.clearLayers();
  incidentPoints.filter(p => passFilters(p, 'incident')).slice(0, 300).forEach(p => {
    const m = L.marker([p.lat, p.lon], { icon: L.divIcon({
      className: '', html: `<div class="wx-marker wx-${p.shape}"><span>${p.symbol}</span></div>`, iconSize: [30, 30] }) });
    m.bindTooltip(`<b>${p.category}</b><br>${p.road || ''}`);
    m.on('click', () => {
      highlightMarker(m);
      document.getElementById('detail-sub').innerText = '— reported incident';
      document.getElementById('weather-detail').innerHTML =
        `<div class="text-lg font-bold">${p.symbol} ${p.category} (reported traffic incident)</div>` +
        `<div>Description: <b>${p.description || 'Not available'}</b></div>` +
        `<div>Road: <b>${p.road || 'Not available'}</b></div>` +
        `<div>Start: <b>${p.start_time || 'Not available'}</b></div>` +
        `<div>Expected end: <b>${p.end_time || 'Not available'}</b></div>` +
        `<div>Source: <b>TomTom Traffic API — NOT an official accident record</b></div>`;
    });
    incidentLayer.addLayer(m);
  });
}

function fillIncidentFilter() {
  const sel = document.getElementById('flt-inc');
  const cur = sel.value;
  const cats = [...new Set(incidentPoints.map(p => p.category))].sort();
  sel.innerHTML = '<option value="">All</option>' + cats.map(c => `<option>${c}</option>`).join('');
  sel.value = cur;
}
let watchData = { datasets: [], pages: [] };

async function loadWatch(force) {
  const box = document.getElementById('watch-items');
  const scanEl = document.getElementById('watch-scan');
  try {
    box.innerHTML = 'Scanning official sources…';
    const res = await fetch('/api/live/watch/scan' + (force ? '?refresh=1' : ''));
    const data = await res.json();
    if (data.status !== 'success') throw new Error('empty');
    watchData = data;
    scanEl.innerText = 'Last scan: ' + data.scanned_at + (data.cached ? ' (cached)' : '') +
      ` — ${data.counts.new} new, ${data.counts.updated} updated, ${data.counts.total} tracked`;
    fillWatchSourceFilter();
    watchShown = WATCH_PAGE;
    drawWatch();
  } catch (e) {
    console.error('Data Watch failed:', e);
    box.innerHTML = 'Source temporarily unavailable. Previous results (if any) are not shown as current.';
  }
}

function watchItems() {
  const pages = (watchData.pages || []).map(p => ({ ...p, kind: 'page' }));
  const dss = (watchData.datasets || []).map(d => ({ ...d, kind: 'dataset' }));
  return pages.concat(dss);
}

function fillWatchSourceFilter() {
  const sel = document.getElementById('wflt-src');
  const cur = sel.value;
  const srcs = [...new Set(watchItems().map(i => i.source))].sort();
  sel.innerHTML = '<option value="">All</option>' + srcs.map(s => `<option>${s}</option>`).join('');
  sel.value = cur;
  const gsel = document.getElementById('wflt-geo');
  const gcur = gsel.value;
  const geos = [...new Set(watchItems().flatMap(i => (i.compatibility || {}).geography || []))].sort();
  gsel.innerHTML = '<option value="">All</option>' + geos.map(g => `<option>${g}</option>`).join('');
  gsel.value = gcur;
}

let watchShown = 12;
const WATCH_PAGE = 12;
const WSTATUS = {
  NEW: { icon: '✦', cls: 'bg-blue-100 text-blue-900 border-blue-300' },
  UPDATED: { icon: '↻', cls: 'bg-amber-100 text-amber-900 border-amber-300' },
  KNOWN: { icon: '✓', cls: 'bg-slate-100 text-slate-700 border-slate-300' },
  SOURCE_UNAVAILABLE: { icon: '⚠', cls: 'bg-rose-100 text-rose-900 border-rose-300 border-dashed' }
};

function drawWatch() {
  const box = document.getElementById('watch-items');
  const moreBtn = document.getElementById('btn-wmore');
  const fS = document.getElementById('wflt-src').value;
  const fT = document.getElementById('wflt-status').value;
  const fR = document.getElementById('wflt-rel').value;
  const fV = document.getElementById('wflt-vin').value;
  const fG = document.getElementById('wflt-geo').value;
  const fE = document.getElementById('wflt-exp').checked;
  const list = watchItems().filter(i =>
    (!fS || i.source === fS) && (!fT || i.status === fT) &&
    (!fR || i.relevance === fR) &&
    (!fV || ((i.compatibility || {}).vintage) === fV) &&
    (!fG || ((i.compatibility || {}).geography || []).includes(fG)) &&
    (!fE || i.exposure_candidate));
  const counts = watchData.counts || { new: 0, updated: 0, total: list.length };
  document.getElementById('wsum-new').innerText = counts.new;
  document.getElementById('wsum-upd').innerText = counts.updated;
  document.getElementById('wsum-tot').innerText = counts.total;
  const srcs = [...new Set(watchItems().map(i => i.source))];
  document.getElementById('wsum-src').innerText = srcs.length + ' sources';
  if (!list.length) {
    box.innerHTML = '<div class="col-span-full border border-dashed rounded-lg p-6 text-center text-slate-500">No datasets match the current filters.</div>';
    moreBtn.classList.add('hidden');
    return;
  }
  const shown = list.slice(0, watchShown);
  box.innerHTML = shown.map(i => {
    const c = i.compatibility || {};
    const geo = (c.geography || []).join(', ');
    const st = WSTATUS[i.status] || { icon: '•', cls: 'bg-slate-100 text-slate-700 border-slate-300' };
    const official = /OFFICIAL/.test(i.source_badge || '');
    return `<div class="border ${st.cls} rounded-lg p-3 bg-white shadow-sm flex flex-col gap-1">` +
      `<div><span class="inline-block border rounded px-1.5 py-0.5 text-[11px] font-bold ${st.cls}">${st.icon} ${i.status}</span></div>` +
      `<div class="font-bold text-[13px] leading-snug">${i.title}</div>` +
      `<div>Source: <b>${i.source_badge || i.source}</b>${official ? '' : ''}</div>` +
      `<div>Relevance: <b>${i.relevance || '—'}</b></div>` +
      (c.vintage ? `<div>Vintage: <b>${c.vintage}</b>${c.vintage_warning ? ' — <b>' + c.vintage_warning + '</b>' : ''}</div>` : '') +
      (geo ? `<div>Geography: ${geo}</div>` : '') +
      (i.exposure_candidate ? `<div class="border border-amber-400 rounded p-1 bg-amber-50">⚠ <b>EXPOSURE CANDIDATE</b> (${i.stock_or_flow}) — vehicle-stock/exposure candidate, requires validation before any risk-rate calculation.</div>` : '') +
      (i.status === 'SOURCE_UNAVAILABLE' ? `<div>Automated access unavailable. Manual verification required.</div>` : '') +
      `<div class="text-slate-500">Detected: ${i.detected_at || i.first_seen || '—'}</div>` +
      `<div class="mt-auto pt-1 flex gap-3"><a class="text-blue-700 underline font-semibold" href="${i.url}" target="_blank" rel="noopener">View Source</a>` +
      (i.kind === 'dataset' ? `<button class="text-indigo-700 underline font-semibold" data-compat="${i.id}">Review Compatibility</button>` : '') +
      `</div><div class="compat text-slate-600 hidden mt-1"></div></div>`;
  }).join('');
  if (list.length > watchShown) {
    moreBtn.classList.remove('hidden');
    moreBtn.innerText = `Show More (showing ${shown.length} of ${list.length})`;
  } else { moreBtn.classList.add('hidden'); }
  box.querySelectorAll('[data-compat]').forEach(btn => btn.addEventListener('click', () => {
    const item = watchItems().find(x => x.id === btn.getAttribute('data-compat'));
    const panel = btn.closest('div.border').querySelector('.compat');
    panel.classList.toggle('hidden');
    panel.innerText = 'Compatibility (metadata guess — verify definitions before any use): ' + JSON.stringify(item.compatibility);
  }));
}

function clearWatchFilters() {
  ['wflt-src', 'wflt-status', 'wflt-rel', 'wflt-vin', 'wflt-geo'].forEach(id => document.getElementById(id).value = '');
  document.getElementById('wflt-exp').checked = false;
  watchShown = WATCH_PAGE;
  drawWatch();
}
document.getElementById('btn-wclear').addEventListener('click', clearWatchFilters);
document.getElementById('btn-wmore').addEventListener('click', () => { watchShown += WATCH_PAGE; drawWatch(); });

['wflt-src', 'wflt-status', 'wflt-rel', 'wflt-vin', 'wflt-geo'].forEach(id =>
  document.getElementById(id).addEventListener('change', () => { watchShown = WATCH_PAGE; drawWatch(); }));
document.getElementById('wflt-exp').addEventListener('change', () => { watchShown = WATCH_PAGE; drawWatch(); });
document.getElementById('btn-watch').addEventListener('click', () => loadWatch(true));

async function loadAvailability() {
  try {
    const res = await fetch('/api/live/status');
    const data = await res.json();
    const dot = { AVAILABLE: '🟢', AWAITING_API_KEY: '🟡', AWAITING_API: '🟡', PARTIAL: '🟡', PLANNED: '🟡', NOT_AVAILABLE: '🔴' };
    document.getElementById('availability').innerHTML = data.layers.map(
      l => `<div>${dot[l.state] || '⚪'} <b>${l.layer}</b> — ${l.note}</div>`).join('');
  } catch (e) { document.getElementById('availability').innerText = 'Availability unknown.'; }
}

document.getElementById('btn-refresh').addEventListener('click', () => { loadLive(true); loadTraffic(true); loadIncidents(true); });
loadLive(false); loadTraffic(false); loadIncidents(false); loadAvailability(); loadWatch(false);
setInterval(() => { loadLive(false); loadTraffic(false); loadIncidents(false); }, REFRESH_MS);
