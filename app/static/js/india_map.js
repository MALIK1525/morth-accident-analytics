/* Phase 16 — India state-boundary layer + state intel panel + Weather Near Me.
   Boundaries: vendored simplified datameet Admin2 (see file properties for source).
   Accident stats: frozen benchmark via /api/live/state-intel (read-only, with years).
   No values invented; missing injuries render as "Not available for this year." */
let stateIntel = null;
let geoLayer = null;
let selectedState = null;
let nearMeMarker = null;

const GEO_ALIAS = {
  'dadra and nagar haveli and daman and diu':
    ['Dadra & Nagar Haveli and Daman & Diu', 'Dadra & Nagar Haveli', 'Daman & Diu'],
  'andaman and nicobar':
    ['Andaman & Nicobar Islands']
};
// Monitored weather city -> benchmark state (for tooltip temperature only).
const CITY_STATE = {
  'Delhi': 'Delhi', 'Mumbai': 'Maharashtra', 'Chennai': 'Tamil Nadu',
  'Kolkata': 'West Bengal', 'Bengaluru': 'Karnataka', 'Hyderabad': 'Telangana',
  'Ahmedabad': 'Gujarat', 'Pune': 'Maharashtra', 'Jaipur': 'Rajasthan',
  'Lucknow': 'Uttar Pradesh'
};
let choroBounds = null;
function normName(s) {
  return (s || '').toLowerCase().replace(/&/g, 'and').replace(/\s+/g, ' ').trim();
}
function entitiesFor(geoName) {
  const key = normName(geoName);
  if (GEO_ALIAS[key]) return GEO_ALIAS[key];
  if (!stateIntel) return [];
  const match = Object.keys(stateIntel).find(b => normName(b) === key);
  return match ? [match] : [];
}

async function loadStateIntel() {
  if (stateIntel) return stateIntel;
  const res = await fetch('/api/live/state-intel');
  const data = await res.json();
  if (data.status !== 'success') throw new Error('state intel unavailable');
  stateIntel = data.states;
  fillStateSearch();
  return stateIntel;
}

function stateStyle(selected) {
  return { color: '#1E3A5F', weight: selected ? 3 : 1, fillColor: '#1D4ED8',
           fillOpacity: selected ? 0.55 : 0.25, dashArray: '' };
}

// Choropleth fill by latest recorded accidents (counts only — NOT risk).
// Grayscale-safe: opacity encodes magnitude; legend states this explicitly.
function choroOpacity(name) {
  if (!choroBounds) return 0.25;
  const ents = entitiesFor(name);
  const vals = ents.map(e => stateIntel[e]).filter(Boolean)
    .map(e => e.latest.accidents).filter(v => typeof v === 'number');
  if (!vals.length) return 0.15;
  const v = Math.max(...vals);
  const t = (Math.log10(v + 1) - choroBounds[0]) / (choroBounds[1] - choroBounds[0] || 1);
  return 0.12 + 0.63 * Math.min(1, Math.max(0, t));
}
function computeChoro() {
  const vals = [];
  Object.values(stateIntel || {}).forEach(e => {
    if (typeof e.latest.accidents === 'number') vals.push(Math.log10(e.latest.accidents + 1));
  });
  if (vals.length) choroBounds = [Math.min(...vals), Math.max(...vals)];
}

function setBoundaryStatus(text, isError) {
  const el = document.getElementById('boundary-status');
  if (el) {
    el.innerText = text;
    el.className = 'text-[11px] mt-1 ' + (isError ? 'text-rose-700' : 'text-slate-500');
  }
}

async function initIndiaMap() {
  if (!map) { setBoundaryStatus('Map not ready — boundaries pending.', true); return; }
  try {
    setBoundaryStatus('Loading accident statistics…', false);
    await loadStateIntel();
    computeChoro();
    setBoundaryStatus('Loading state boundaries…', false);
    const res = await fetch('/static/geo/india_states.geojson?v=ph21');
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const geo = await res.json();
    if (!geo.features || !geo.features.length) throw new Error('empty GeoJSON');
    geoLayer = L.geoJSON(geo, {
      style: f => ({ color: '#1E3A5F', weight: 1, fillColor: '#1D4ED8',
                     fillOpacity: choroOpacity((f.properties || {}).name || ''),
                     interactive: true }),
      onEachFeature: (feature, layer) => {
        const name = (feature.properties || {}).name || 'Unknown';
        // Bind once: Leaflet opens sticky tooltips on hover automatically.
        layer.bindTooltip(() => stateTooltip(name), { sticky: true, direction: 'top' });
        layer.on('mouseover', () => {
          if (name !== selectedState) layer.setStyle({ weight: 2.5, fillOpacity: 0.45 });
        });
        layer.on('mouseout', () => {
          if (name !== selectedState && geoLayer) geoLayer.resetStyle(layer);
        });
        layer.on('click', () => selectState(name, layer));
      }
    }).addTo(map);
    try { map.fitBounds(geoLayer.getBounds().pad(-0.05)); } catch (e) { map.setView([22.5, 79.5], 5); }
    setBoundaryStatus(`State boundaries loaded: ${geo.features.length} polygons. Hover for statistics, click to select.`, false);
  } catch (e) {
    console.error('Boundary init failed:', e);
    setBoundaryStatus('State boundaries failed to load (' + (e.message || e) + '). Statistics remain available via search. [Retry]', true);
    const el = document.getElementById('boundary-status');
    if (el) el.innerHTML += ' <button id="btn-geo-retry" class="underline font-bold">Retry</button>';
    const rb = document.getElementById('btn-geo-retry');
    if (rb) rb.addEventListener('click', () => initIndiaMap().catch(() => {}));
    throw e;
  }
}

function stateTooltip(name) {
  const ents = entitiesFor(name);
  if (!ents.length) return `<b>${name}</b><br>Accident data: boundary-bound match unavailable — use search.`;
  const e = stateIntel[ents[0]];
  const inj = e.latest.injured === null || e.latest.injured === undefined
    ? 'Not available for this year' : e.latest.injured.toLocaleString('en-IN');
  let tempLine = 'Current temperature: unavailable (weather feed down or not loaded)';
  try {
    const pts = (typeof weatherPoints !== 'undefined' && weatherPoints) || [];
    const cities = Object.keys(CITY_STATE).filter(c => CITY_STATE[c] === ents[0] || ents.includes(CITY_STATE[c]));
    const hit = pts.find(p => cities.includes(p.name) && typeof p.temperature_c === 'number');
    if (hit) tempLine = `Current temperature: ${hit.temperature_c}°C at ${hit.name} (Open-Meteo, city proxy)`;
  } catch (err) {}
  return `<b>${ents[0]}</b> (${e.latest_year}, MoRTH benchmark)<br>` +
    `Accidents: ${e.latest.accidents.toLocaleString('en-IN')}<br>` +
    `Fatalities: ${e.latest.fatalities.toLocaleString('en-IN')}<br>` +
    `Injured: ${inj}<br>${tempLine}<br>` +
    `<span style="color:#64748B">Historical statistics — not live counts. Source: MoRTH.</span>`;
}

async function selectState(name, layer) {
  selectedState = name;
  if (geoLayer) geoLayer.eachLayer(l => geoLayer.resetStyle(l));
  if (layer) layer.setStyle(stateStyle(true));
  const panel = document.getElementById('state-panel');
  const ents = entitiesFor(name);
  if (!ents.length) {
    panel.innerHTML = `<b>${name}</b><br>No benchmark match for this boundary. Accident statistics: Not available.`;
    return;
  }
  let html = '';
  for (const ent of ents) {
    const e = stateIntel[ent];
    if (!e) continue;
    const inj = e.latest.injured === null || e.latest.injured === undefined
      ? 'Not available for this year' : e.latest.injured.toLocaleString('en-IN');
    const rows = Object.keys(e.years).sort().map(y => {
      const v = e.years[y];
      return `<tr><td>${y}</td><td>${v.accidents.toLocaleString('en-IN')}</td>` +
        `<td>${v.fatalities.toLocaleString('en-IN')}</td>` +
        `<td>${v.injured === null || v.injured === undefined ? 'Not available for this year' : v.injured.toLocaleString('en-IN')}</td></tr>`;
    }).join('');
    html += `<div class="border rounded-lg p-2 mb-2 bg-white">` +
      `<div class="font-bold">${ent} <span class="text-xs font-normal">(historical statistics, NOT live counts)</span></div>` +
      `<div>Reported accidents (${e.latest_year}): <b>${e.latest.accidents.toLocaleString('en-IN')}</b></div>` +
      `<div>Fatalities (${e.latest_year}): <b>${e.latest.fatalities.toLocaleString('en-IN')}</b></div>` +
      `<div>Injured (${e.latest_year}): <b>${inj}</b></div>` +
      `<div>Severity: <b>${e.severity_per_100} deaths / 100 accidents</b> (fatalities ÷ accidents)</div>` +
      `<div class="text-slate-500">Source: ${e.source} · Vintage: ${e.vintage}</div>` +
      `<details class="mt-1"><summary class="cursor-pointer text-blue-700">Year trend (${Object.keys(e.years).length} verified years)</summary>` +
      `<table class="w-full text-left mt-1"><thead><tr><th>Year</th><th>Accidents</th><th>Fatalities</th><th>Injured</th></tr></thead><tbody>${rows}</tbody></table></details>` +
      `</div>`;
  }
  // Current weather at polygon centroid (independent of accident year).
  let wxHtml = '<div>Weather: loading…</div>';
  panel.innerHTML = html + `<div id="state-wx">${wxHtml}</div>` +
    `<div class="text-[11px] text-slate-500 mt-1">Data-quality notes: state injuries unpublished for 2023–2024 (shown as Not available, never zero-filled). ` +
    `Counts are recorded occurrences, not exposure-normalized risk. Sources: ` +
    `<a class="underline" href="https://morth.nic.in/en/road-accident-in-india" target="_blank" rel="noopener">MoRTH</a> · ` +
    `<a class="underline" href="https://www.data.gov.in/" target="_blank" rel="noopener">data.gov.in</a></div>`;
  try {
    const c = layer ? layer.getBounds().getCenter() : null;
    const wres = await fetch(`/api/live/weather?lat=${c ? c.lat.toFixed(2) : 22.5}&lon=${c ? c.lng.toFixed(2) : 79.5}`);
    const w = await wres.json();
    const el = document.getElementById('state-wx');
    if (el) el.innerHTML = w.status === 'success'
      ? `<div class="border rounded-lg p-2 bg-sky-50"><b>Current temperature near ${ents[0]}:</b> ${w.temperature_c}°C (${w.condition}) · observed ${w.observed_at || 'n/a'} · Source: Open-Meteo (centroid proxy, not a state measurement)</div>`
      : `<div>Weather temporarily unavailable.</div>`;
  } catch (e) { /* weather stays in loading/unavailable state; panel intact */ }
}

function fillStateSearch() {
  const sel = document.getElementById('state-search');
  if (!sel || !stateIntel) return;
  sel.innerHTML = '<option value="">Select state / UT…</option>' +
    Object.keys(stateIntel).sort().map(s => `<option>${s}</option>`).join('');
}

function wireStateSearch() {
  const sel = document.getElementById('state-search');
  const btn = document.getElementById('btn-india-reset');
  if (sel) sel.addEventListener('change', () => {
    const ent = sel.value;
    if (!ent || !geoLayer) return;
    let found = null;
    geoLayer.eachLayer(l => {
      const n = (l.feature.properties || {}).name || '';
      const ents = entitiesFor(n);
      if (ents.includes(ent)) found = l;
    });
    if (found) { map.fitBounds(found.getBounds()); selectState((found.feature.properties || {}).name, found); }
    else {
      selectedState = ent;
      document.getElementById('state-panel').innerHTML =
        `<b>${ent}</b> — boundary polygon unavailable for this entity; verified statistics below.<br>` +
        `<span class="text-slate-500">Showing benchmark rows without a map polygon (no boundaries invented).</span>`;
      const e = stateIntel[ent];
      if (e) selectStateFromEntity(ent);
    }
  });
  if (btn) btn.addEventListener('click', () => {
    selectedState = null;
    if (sel) sel.value = '';
    if (geoLayer) { geoLayer.eachLayer(l => geoLayer.resetStyle(l)); try { map.fitBounds(geoLayer.getBounds().pad(-0.05)); } catch (e) {} }
    document.getElementById('state-panel').innerHTML = 'Select a state on the map or from the search to see verified statistics.';
  });
}

function selectStateFromEntity(ent) {
  const e = stateIntel[ent];
  const inj = e.latest.injured === null || e.latest.injured === undefined
    ? 'Not available for this year' : e.latest.injured.toLocaleString('en-IN');
  document.getElementById('state-panel').innerHTML =
    `<div class="border rounded-lg p-2 bg-white"><div class="font-bold">${ent} (historical statistics)</div>` +
    `<div>Reported accidents (${e.latest_year}): <b>${e.latest.accidents.toLocaleString('en-IN')}</b></div>` +
    `<div>Fatalities (${e.latest_year}): <b>${e.latest.fatalities.toLocaleString('en-IN')}</b></div>` +
    `<div>Injured (${e.latest_year}): <b>${inj}</b></div>` +
    `<div class="text-slate-500">Source: ${e.source}</div></div>`;
}

// ---- Weather Near Me (explicit opt-in only; never stored, never logged) ----
function wireNearMe() {
  const btn = document.getElementById('btn-near-me');
  const box = document.getElementById('near-me');
  if (!btn) return;
  btn.addEventListener('click', () => {
    if (!navigator.geolocation) {
      box.innerHTML = 'Geolocation is not supported by this browser. Please use the city search instead.';
      return;
    }
    box.innerHTML = 'Requesting location permission…';
    navigator.geolocation.getCurrentPosition(async pos => {
      const lat = pos.coords.latitude.toFixed(3), lon = pos.coords.longitude.toFixed(3);
      box.innerHTML = 'Location received — fetching current weather…';
      let timer = null;
      try {
        const ctrl = new AbortController();
        timer = setTimeout(() => ctrl.abort(), 25000);
        const res = await fetch(`/api/live/weather?lat=${lat}&lon=${lon}`, { signal: ctrl.signal });
        clearTimeout(timer);
        const w = await res.json();
        if (w.status !== 'success') throw new Error('empty');
        box.innerHTML = `<b>${w.temperature_c}°C, ${w.condition}</b> · observed ${w.observed_at || 'n/a'} · Source: Open-Meteo` +
          `<br><span class="text-slate-500">Your coordinates stay in this browser session only (nearest monitored-city average shown above is separate).</span>`;
        if (nearMeMarker) map.removeLayer(nearMeMarker);
        nearMeMarker = L.marker([lat, lon]).addTo(map).bindTooltip('<b>You (this session only)</b>').openTooltip();
      } catch (e) {
        if (timer) clearTimeout(timer);
        box.innerHTML = 'Weather request failed or timed out. Provider may be rate-limited — please use the city search instead.';
      }
    }, () => {
      box.innerHTML = 'Location permission denied or unavailable. Nothing breaks — please use the city search instead.';
    });
  });
}
