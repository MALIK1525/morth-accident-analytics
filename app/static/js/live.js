/* Phase 13.2 Live Monitor frontend. Backend is the only caller of Open-Meteo. */
const REFRESH_MS = 5 * 60 * 1000;
let map, markersLayer;

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
      markersLayer = L.layerGroup().addTo(map);
    } else { markersLayer.clearLayers(); }
    data.points.forEach(p => {
      const icon = L.divIcon({
        className: '',
        html: `<div class="wx-marker wx-${p.shape}"><span>${p.icon}</span></div>`,
        iconSize: [34, 34]
      });
      const m = L.marker([p.lat, p.lon], { icon });
      m.bindTooltip(`<b>${p.name}</b><br>${p.condition}<br>${fmt(p.temperature_c, '°C', 1)}`);
      m.on('click', () => showDetail(p));
      markersLayer.addLayer(m);
    });
    const s = data.summary;
    document.getElementById('kpi-locs').innerText = s.locations_monitored;
    document.getElementById('kpi-rain').innerText = s.rain_affected;
    document.getElementById('kpi-avg').innerText = fmt(s.avg_temp_c, '°C', 1);
    document.getElementById('kpi-range').innerText =
      (s.max_temp_c !== null ? s.max_temp_c + '° / ' + s.min_temp_c + '°C' : '—');
    document.getElementById('live-clock').innerText = 'Last updated: ' + data.fetched_at + (data.cached ? ' (cached)' : '');
    badge.className = 'text-[11px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800';
    badge.innerText = '🟢 LIVE Source: Open-Meteo Updated: ' + data.fetched_at;
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

async function loadAvailability() {
  try {
    const res = await fetch('/api/live/status');
    const data = await res.json();
    const dot = { AVAILABLE: '🟢', AWAITING_API_KEY: '🟡', AWAITING_API: '🟡', PARTIAL: '🟡', PLANNED: '🟡', NOT_AVAILABLE: '🔴' };
    document.getElementById('availability').innerHTML = data.layers.map(
      l => `<div>${dot[l.state] || '⚪'} <b>${l.layer}</b> — ${l.note}</div>`).join('');
  } catch (e) { document.getElementById('availability').innerText = 'Availability unknown.'; }
}

document.getElementById('btn-refresh').addEventListener('click', () => loadLive(true));
loadLive(false); loadAvailability();
setInterval(() => loadLive(false), REFRESH_MS);
