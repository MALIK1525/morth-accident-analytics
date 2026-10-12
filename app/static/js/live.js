/* Phase 13.2–13.3 Live Monitor frontend. Backend proxies all provider APIs. */
const REFRESH_MS = 5 * 60 * 1000;
let map, weatherLayer;
let mapTraffic = null, trafficLayerT = L.layerGroup(), incidentLayerT = null;
const CITY_DEG = 0.25; // must match backend CITY_BBOX_HALF_DEG

function makeIncidentLayer() {
  // Real clustering when the CDN plugin loads; plain group otherwise.
  // Cluster counts always equal distinct markers added (backend dedupes by id).
  if (typeof L.markerClusterGroup === 'function') {
    return L.markerClusterGroup({ showCoverageOnHover: true, spiderfyOnMaxZoom: true,
      maxClusterRadius: 60, chunkedLoading: true });
  }
  return L.layerGroup();
}
incidentLayerT = makeIncidentLayer();
let activeTab = 'weather';
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
  // Weather-derived hazards → weather card; traffic-derived → traffic card. Never mixed.
  const wxBox = document.getElementById('hazards-wx');
  if (wxBox) {
    const out = [];
    weatherPoints.forEach(p => {
      if (p.condition === 'Thunderstorm') out.push(`⛈ Thunderstorm observed at ${p.name} (Open-Meteo)`);
      else if (p.condition === 'Fog') out.push(`🌫 Fog observed at ${p.name} (Open-Meteo)`);
      else if (typeof p.precipitation_mm === 'number' && p.precipitation_mm >= 5) out.push(`🌧 Heavy rain observed at ${p.name}: ${p.precipitation_mm} mm (Open-Meteo)`);
    });
    wxBox.innerHTML = out.length ? out.slice(0, 20).map(h => `<div>• ${h}</div>`).join('') : 'No severe weather currently observed at monitored locations.';
  }
  const box = document.getElementById('hazards');
  if (!box) return;
  const out = [];
  trafficPoints.forEach(p => {
    if (p.road_closure) out.push(`⛔ Reported road closure near ${p.name} (TomTom flow feed)`);
    else if (p.condition === 'Very heavy' || p.condition === 'Heavy') out.push(`🚦 ${p.condition} congestion near ${p.name} (TomTom flow feed)`);
  });
  incidentPoints.slice(0, 300).forEach(p => {
    if (p.category === 'Road closed' || p.category === 'Flooding') out.push(`⚠ ${p.category}: ${p.road || 'location undisclosed'} (TomTom incidents)`);
  });
  box.innerHTML = out.length ? out.slice(0, 20).map(h => `<div>• ${h}</div>`).join('') : 'No reported closures or heavy congestion in monitored areas right now.';
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

function ensureMap() {
  if (map || typeof L === 'undefined') return map;
  const el = document.getElementById('live-map');
  if (!el) return null;
  try {
    map = L.map('live-map').setView([22.5, 79.5], 5);
    const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',
      { maxZoom: 12, attribution: '© OpenStreetMap contributors' });
    tiles.on('tileerror', () => {
      const n = document.getElementById('tile-notice');
      if (n) n.classList.remove('hidden');
    });
    tiles.addTo(map);
    weatherLayer = L.layerGroup().addTo(map);
    wireToggles();
    setTimeout(() => { try { map.invalidateSize(); } catch (e) {} }, 300);
  } catch (e) {
    console.error('Map init failed:', e);
    el.innerHTML = '<div class="p-6 text-center text-sm">Map failed to initialize. State statistics remain available via search below.</div>';
    map = null;
  }
  return map;
}

async function loadLive(force) {
  const badge = document.getElementById('badge-weather');
  try {
    const res = await fetch('/api/live/weather/summary' + (force ? '?refresh=1' : ''));
    const data = await res.json();
    if (data.status !== 'success' || !data.points || !data.points.length) throw new Error('empty');
    ensureMap();
    if (weatherLayer) weatherLayer.clearLayers();
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
    badge.innerText = '🟢 LIVE Source: ' + (data.source || 'Open-Meteo') + ' Updated: ' + data.fetched_at;
    if (data.stale) {
      badge.className = 'text-[11px] px-2 py-0.5 rounded bg-amber-100 text-amber-800';
      badge.innerText = '🟡 STALE — ' + (data.stale_note || ('last successful update ' + data.fetched_at));
    }
    if (data.failed && data.failed.length) {
      badge.innerText += ` (${data.failed.length} location(s) unavailable)`;
    }
  } catch (e) {
    console.error('Live weather failed:', e);
    // Map and state statistics are independent of weather — keep them working.
    ensureMap();
    badge.className = 'text-[11px] px-2 py-0.5 rounded bg-rose-100 text-rose-800';
    badge.innerText = '🔴 Weather temporarily unavailable';
    const prev = document.getElementById('live-clock').innerText;
    if (prev === 'Last updated: —') document.getElementById('live-clock').innerText = 'Weather temporarily unavailable';
  }
}

// NOTE: cross-file boot lives at the end of india_map.js (which loads last),
// because live.js executes before india_map.js is parsed.

function ensureTrafficMap() {
  if (mapTraffic) return mapTraffic;
  const el = document.getElementById('map-traffic');
  if (!el || typeof L === 'undefined' || !el.offsetParent) return null;
  try {
    mapTraffic = L.map('map-traffic').setView([22.5, 79.5], 5);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',
      { maxZoom: 12, attribution: '© OpenStreetMap contributors' }).addTo(mapTraffic);
    // Provider flow tiles via same-origin proxy (key stays server-side).
    // relative0: green near free flow → orange/red slowing → white closed.
    const flow = L.tileLayer('/api/live/traffic/tile/relative0/{z}/{x}/{y}.png',
      { maxZoom: 12, opacity: 0.85,
        attribution: 'Flow © TomTom', errorTileUrl: '' });
    let tileErrs = 0;
    flow.on('tileerror', () => {
      tileErrs += 1;
      const n = document.getElementById('traffic-tile-notice');
      if (n && tileErrs >= 3) n.classList.remove('hidden');
    });
    flow.addTo(mapTraffic);
    window._flowTiles = flow;
    trafficLayerT.addTo(mapTraffic);
    incidentLayerT.addTo(mapTraffic);
    mapTraffic.on('click', onTrafficMapClick);
    applyToggles();
    setTimeout(() => { try { mapTraffic.invalidateSize(); } catch (e) {} }, 100);
  } catch (e) {
    console.error('Traffic map init failed:', e);
    mapTraffic = null;
  }
  return mapTraffic;
}

async function onTrafficMapClick(e) {
  if (!mapTraffic) return;
  const box = document.getElementById('traffic-status');
  try {
    const res = await fetch(`/api/live/traffic/segment?lat=${e.latlng.lat.toFixed(3)}&lon=${e.latlng.lng.toFixed(3)}`);
    const d = await res.json();
    if (d.status !== 'success') throw new Error('empty');
    const segHtml =
      `<div class="text-lg font-bold">Selected road segment</div>` +
      `<div>Current speed: <b>${fmt(d.current_speed_kmh, ' km/h', 0)}</b></div>` +
      `<div>Free-flow speed: <b>${fmt(d.free_flow_speed_kmh, ' km/h', 0)}</b></div>` +
      `<div>Travel time: <b>${fmt(d.travel_time_s, ' s', 0)}</b></div>` +
      `<div>Confidence: <b>${d.confidence !== null && d.confidence !== undefined ? d.confidence : 'Not available'}</b></div>` +
      `<div>Closure: <b>${d.road_closure ? 'YES' : 'no'}</b></div>` +
      `<div class="text-slate-500">One sampled segment — not a whole highway. Source: TomTom, fetched ${d.fetched_at || ''} (fetch time; provider observation time not supplied)</div>`;
    showTrafficDetail(segHtml, 'road segment');
    L.popup().setLatLng(e.latlng).setContent(
      `<b>Road segment</b> (nearest provider segment)<br>` +
      `Current speed: <b>${fmt(d.current_speed_kmh, ' km/h', 0)}</b><br>` +
      `Free-flow speed: <b>${fmt(d.free_flow_speed_kmh, ' km/h', 0)}</b><br>` +
      `Travel time: <b>${fmt(d.travel_time_s, ' s', 0)}</b><br>` +
      `Confidence: <b>${d.confidence !== null && d.confidence !== undefined ? d.confidence : 'Not available'}</b><br>` +
      `Closure: <b>${d.road_closure ? 'YES' : 'no'}</b><br>` +
      `<span style="color:#64748B">One sampled segment — not a whole highway. Source: TomTom, fetched ${d.fetched_at || ''} (fetch time; provider observation time not supplied)</span>`
    ).openOn(mapTraffic);
  } catch (err) {
    if (box) box.innerText = 'Segment details unavailable for this point. Coverage: monitored areas where the provider returns flow.';
  }
}

function showTrafficDetail(html, sub) {
  const el = document.getElementById('traffic-detail');
  const s = document.getElementById('traffic-detail-sub');
  if (s) s.innerText = '— ' + (sub || 'selected');
  if (el) el.innerHTML = html;
}

const WX_AVAIL = ['Weather', 'Official accident records', 'Hazards', 'Government data watch'];
const TRAF_AVAIL = ['Traffic', 'Reported incidents'];

function applyModePanels(which) {
  const traffic = which === 'traffic';
  const pairs = [
    ['card-weather', traffic], ['card-traffic', !traffic], ['card-nearme', traffic],
    ['live-kpis', traffic], ['live-kpis-traffic', !traffic],
    ['kpi-note-weather', traffic], ['kpi-note-traffic', !traffic],
    ['card-hazards', !traffic], ['card-wxhaz', traffic],
    ['card-avail-wx', traffic], ['card-avail-traf', !traffic],
    ['legend-states', traffic], ['legend-weather', traffic],
    ['legend-flow', !traffic], ['legend-inc', !traffic], ['legend-haz', !traffic],
    ['sections-wx', traffic], ['sections-traf', !traffic],
    ['lbl-lyr-weather', traffic], ['lbl-lyr-traffic', !traffic],
    ['lbl-lyr-incidents', !traffic], ['badge-weather', traffic], ['badge-traffic', !traffic],
  ];
  pairs.forEach(([id, hide]) => {
    const el = document.getElementById(id);
    if (el) el.classList.toggle('hidden', hide);
  });
}

function showTab(which) {
  activeTab = which;
  applyModePanels(which);
  const w = document.getElementById('map-weather-wrap');
  const t = document.getElementById('map-traffic-wrap');
  const bw = document.getElementById('tab-weather');
  const bt = document.getElementById('tab-traffic');
  const on = 'px-3 py-1.5 rounded bg-blue-600 text-white';
  const off = 'px-3 py-1.5 rounded bg-slate-200 text-slate-700';
  if (which === 'traffic') {
    w.classList.add('hidden'); t.classList.remove('hidden');
    bw.className = off; bt.className = on;
    bw.setAttribute('aria-selected', 'false'); bt.setAttribute('aria-selected', 'true');
    ensureTrafficMap();
    setTimeout(() => { try { mapTraffic && mapTraffic.invalidateSize(); } catch (e) {} }, 60);
    drawTraffic(); drawIncidents();
  } else {
    t.classList.add('hidden'); w.classList.remove('hidden');
    bt.className = off; bw.className = on;
    bt.setAttribute('aria-selected', 'false'); bw.setAttribute('aria-selected', 'true');
    setTimeout(() => { try { map && map.invalidateSize(); } catch (e) {} }, 60);
  }
}

function wireTabs() {
  const bw = document.getElementById('tab-weather');
  const bt = document.getElementById('tab-traffic');
  if (bw) bw.addEventListener('click', () => showTab('weather'));
  if (bt) bt.addEventListener('click', () => showTab('traffic'));
}

function applyToggles() {
  const w = document.getElementById('lyr-weather').checked;
  const t = document.getElementById('lyr-traffic').checked;
  const ii = document.getElementById('lyr-incidents').checked;
  if (map && weatherLayer) {
    if (w && !map.hasLayer(weatherLayer)) weatherLayer.addTo(map);
    if (!w && map.hasLayer(weatherLayer)) map.removeLayer(weatherLayer);
  }
  if (mapTraffic) {
    const fl = window._flowTiles;
    if (fl) {
      if (t && !mapTraffic.hasLayer(fl)) fl.addTo(mapTraffic);
      if (!t && mapTraffic.hasLayer(fl)) mapTraffic.removeLayer(fl);
    }
    if (ii && !mapTraffic.hasLayer(incidentLayerT)) incidentLayerT.addTo(mapTraffic);
    if (!ii && mapTraffic.hasLayer(incidentLayerT)) mapTraffic.removeLayer(incidentLayerT);
  }
}

function wireToggles() {
  const apply = () => { applyToggles(); };
  ['lyr-weather', 'lyr-traffic', 'lyr-incidents', 'flt-city', 'flt-inc'].forEach(id => {
    const el = document.getElementById(id);
    if (id.startsWith('flt-')) { if (el) el.addEventListener('change', () => { drawWeather(); drawTraffic(); drawIncidents(); }); }
    else if (el) el.addEventListener('change', applyToggles);
  });
}

function passFilters(p, kind) {
  const city = document.getElementById('flt-city').value;
  if (city && p.name !== city) return false;
  if (kind === 'traffic') {
    const tel = document.getElementById('flt-traf');
    const t = tel ? tel.value : '';
    if (t && p.condition !== t) return false;
  }
  if (kind === 'incident') {
    const t = document.getElementById('flt-inc').value;
    if (t && p.category !== t) return false;
    const qEl = document.getElementById('incident-search');
    const q = qEl ? qEl.value.toLowerCase().trim() : '';
    if (q && !((p.road || '') + ' ' + (p.description || '') + ' ' + (p.category || '')).toLowerCase().includes(q)) return false;
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
    fillTrafficCities();
    drawHazards();
    layerEpoch.traffic = Date.now(); tickAges();
    badge.className = 'text-[11px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800';
    badge.innerText = '🟢 LIVE Source: TomTom Updated: ' + data.fetched_at + (data.cached ? ' (cached)' : '');
    sec.innerText = '🟢 live (TomTom)';
    const tf = document.getElementById('kpi-tflow');
    if (tf) tf.innerText = data.points && data.points.length ? '🟢 Live' : 'Empty';
    const tc = document.getElementById('kpi-tcov');
    if (tc) tc.innerText = 'Monitored-city areas';
  } catch (e) {
    console.error('Live traffic failed:', e);
    badge.className = 'text-[11px] px-2 py-0.5 rounded bg-rose-100 text-rose-800';
    badge.innerText = '🔴 Traffic temporarily unavailable';
    if (sec) sec.innerText = '🔴 temporarily unavailable (weather unaffected)';
    const tf = document.getElementById('kpi-tflow');
    if (tf) tf.innerText = 'Unavailable';
  }
}

function drawTraffic() {
  // Flow is rendered as provider tiles on the traffic map; per-city points
  // feed only the city selector, badges and coverage (no point markers).
  fillTrafficCities();
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
    const ti = document.getElementById('kpi-tinc');
    if (ti) ti.innerText = incidentPoints.length;
    const tcl = document.getElementById('kpi-tclose');
    if (tcl) tcl.innerText = incidentPoints.filter(p => /clos/i.test(p.category || '')).length;
  } catch (e) {
    console.error('Live incidents failed:', e);
    if (secI) secI.innerText = '🔴 temporarily unavailable (weather unaffected)';
    const ti = document.getElementById('kpi-tinc');
    if (ti) ti.innerText = 'Unavailable';
  }
}

function drawIncidents() {
  incidentLayerT.clearLayers();
  const list = incidentPoints.filter(p => passFilters(p, 'incident')).slice(0, 300);
  window._incidentMarkers = {};
  list.forEach((p, idx) => {
    const m = L.marker([p.lat, p.lon], { icon: L.divIcon({
      className: '', html: `<div class="wx-marker wx-${p.shape}"><span>${p.symbol}</span></div>`, iconSize: [30, 30] }) });
    m.bindTooltip(`<b>${p.category}</b><br>${p.road || ''}`);
    m.on('click', () => {
      highlightMarker(m);
      showTrafficDetail(
        `<div class="text-lg font-bold">${p.symbol} ${p.category} (reported traffic incident)</div>` +
        `<div>Type: <b>${p.category}</b></div>` +
        `<div>Description: <b>${p.description || 'Not available'}</b></div>` +
        (p.delay_label ? `<div>Severity: <b>${p.delay_label}</b> (provider-reported)</div>` : '') +
        `<div>Road: <b>${p.road || 'Not available'}</b></div>` +
        (p.near ? `<div>Nearest monitored city: <b>${p.near}</b> (query area, not exact scope)</div>` : '') +
        `<div>Start: <b>${p.start_time || 'Not available'}</b></div>` +
        `<div>Expected end: <b>${p.end_time || 'Not available'}</b></div>` +
        `<div>Source: <b>TomTom Traffic API — NOT an official accident record</b></div>`,
        'reported incident');
    });
    window._incidentMarkers[p.id || ('n' + idx)] = m;
    incidentLayerT.addLayer(m);
  });
  drawIncidentList(list);
  updateIncidentLegend(list);
}

// Live counts per normalized category (only categories actually present).
function updateIncidentLegend(list) {
  const el = document.getElementById('legend-inc-counts');
  if (!el) return;
  const counts = {};
  list.forEach(p => { counts[p.category || 'Unknown'] = (counts[p.category || 'Unknown'] || 0) + 1; });
  const keys = Object.keys(counts).sort();
  el.innerHTML = keys.length
    ? keys.map(k => `${k}: <b>${counts[k]}</b>`).join(' · ')
    : 'No incidents in current filter.';
}

function drawIncidentList(list) {
  const box = document.getElementById('incident-list');
  if (!box) return;
  if (!list.length) {
    box.innerHTML = incidentPoints.length
      ? 'No incidents match the current filters. <button id="btn-inc-clear" class="underline font-bold">Clear incident filters</button>'
      : 'No reported incidents in monitored areas right now.';
    const c = document.getElementById('btn-inc-clear');
    if (c) c.addEventListener('click', () => {
      document.getElementById('flt-inc').value = '';
      const q = document.getElementById('incident-search');
      if (q) q.value = '';
      drawIncidents();
    });
    return;
  }
  const shown = list.slice(0, 50);
  box.innerHTML = shown.map((p, idx) => {
    const key = p.id || ('n' + idx);
    return `<div><button class="underline text-left" data-inc="${key}"><b>${p.category}</b> — ${p.road || 'road undisclosed'} <span class="text-slate-500">${p.start_time || ''}</span></button></div>`;
  }).join('') + (list.length > 50 ? `<div class="text-slate-500">Showing 50 of ${list.length} — refine search.</div>` : '');
  box.querySelectorAll('[data-inc]').forEach(btn => btn.addEventListener('click', () => {
    const m = window._incidentMarkers[btn.getAttribute('data-inc')];
    if (m && mapTraffic) {
      if (activeTab !== 'traffic') showTab('traffic');
      setTimeout(() => {
        if (incidentLayerT.zoomToShowLayer) {
          incidentLayerT.zoomToShowLayer(m, () => { highlightMarker(m); m.fire('click'); });
        } else {
          mapTraffic.setView(m.getLatLng(), 13);
          highlightMarker(m);
          m.fire('click');
        }
      }, 150);
    }
  }));
}

function fillTrafficCities() {
  const sel = document.getElementById('traffic-city');
  if (!sel) return;
  const names = [...new Set(trafficPoints.map(p => p.name))].sort();
  const cur = sel.value;
  sel.innerHTML = '<option value="">India overview</option>' + names.map(n => `<option>${n}</option>`).join('');
  sel.value = cur;
}

function wireTrafficNav() {
  const sel = document.getElementById('traffic-city');
  const reset = document.getElementById('btn-traffic-india');
  const search = document.getElementById('incident-search');
  const cov = document.getElementById('traffic-coverage');
  if (sel && !sel.dataset.wired) {
    sel.dataset.wired = '1';
    sel.addEventListener('change', () => {
      const p = trafficPoints.find(x => x.name === sel.value);
      if (p && mapTraffic) {
        mapTraffic.fitBounds([[p.lat - CITY_DEG, p.lon - CITY_DEG], [p.lat + CITY_DEG, p.lon + CITY_DEG]]);
        if (cov) cov.innerText = `Coverage: ±0.25° around ${p.name} (monitored-city area, not nationwide).`;
      } else if (mapTraffic) {
        mapTraffic.setView([22.5, 79.5], 5);
        if (cov) cov.innerText = 'Coverage: monitored-city areas (not nationwide).';
      }
    });
  }
  if (reset && !reset.dataset.wired) {
    reset.dataset.wired = '1';
    reset.addEventListener('click', () => {
      if (sel) sel.value = '';
      if (mapTraffic) mapTraffic.setView([22.5, 79.5], 5);
      if (cov) cov.innerText = 'Coverage: monitored-city areas (not nationwide).';
    });
  }
  if (search && !search.dataset.wired) {
    search.dataset.wired = '1';
    search.addEventListener('input', () => drawIncidents());
  }
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
  const render = (elId, layers) => {
    const el = document.getElementById(elId);
    if (!el) return;
    const dot = { AVAILABLE: '🟢', AWAITING_API_KEY: '🟡', AWAITING_API: '🟡', PARTIAL: '🟡', PLANNED: '🟡', NOT_AVAILABLE: '🔴' };
    el.innerHTML = layers.map(
      l => `<div>${dot[l.state] || '⚪'} <b>${l.layer}</b> — ${l.note}</div>`).join('');
  };
  try {
    const res = await fetch('/api/live/status');
    const data = await res.json();
    const layers = data.layers || [];
    render('availability-wx', layers.filter(l => WX_AVAIL.includes(l.layer)));
    render('availability-traf', layers.filter(l => TRAF_AVAIL.includes(l.layer)));
  } catch (e) {
    ['availability-wx', 'availability-traf'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.innerText = 'Availability unknown.';
    });
  }
}

document.getElementById('btn-refresh').addEventListener('click', () => { loadLive(true); loadTraffic(true); loadIncidents(true); });
loadLive(false); loadTraffic(false); loadIncidents(false); loadAvailability(); loadWatch(false);
setInterval(() => { loadLive(false); loadTraffic(false); loadIncidents(false); }, REFRESH_MS);
