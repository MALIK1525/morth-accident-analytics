import asyncio
from playwright.async_api import async_playwright

URL = 'https://morth-accident-analytics.onrender.com/live'
IDS = ['#card-weather', '#card-traffic', '#card-nearme', '#card-hazards', '#card-wxhaz',
       '#card-avail-wx', '#card-avail-traf', '#live-kpis', '#live-kpis-traffic',
       '#legend-states', '#legend-weather', '#legend-flow', '#legend-inc', '#legend-haz',
       '#sections-wx', '#sections-traf']

def clean(s):
    return (s or '').encode('ascii', 'replace').decode()[:200]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)[:200]))
        await page.goto(URL, wait_until='networkidle', timeout=120000)
        await page.wait_for_timeout(9000)

        async def state():
            out = {}
            for sel in IDS:
                out[sel] = await page.evaluate(
                    "(s) => { const el = document.querySelector(s); "
                    "return el ? (el.classList.contains('hidden') ? 'H' : 'V') : 'MISSING'; }", sel)
            return out

        w = await state()
        print('WEATHER MODE:')
        for k, v in w.items():
            print('  %s %s' % (v, k))
        assert w['#card-weather'] == 'V' and w['#card-traffic'] == 'H'
        assert w['#card-hazards'] == 'H' and w['#card-wxhaz'] == 'V'
        assert w['#card-avail-traf'] == 'H' and w['#card-avail-wx'] == 'V'
        assert w['#legend-flow'] == 'H' and w['#legend-inc'] == 'H' and w['#legend-haz'] == 'H'
        assert w['#legend-states'] == 'V' and w['#legend-weather'] == 'V'
        wx_avail = clean(await page.inner_text('#availability-wx'))
        print('WX AVAIL:', wx_avail.replace(chr(10), ' | '))
        assert 'TomTom' not in wx_avail, 'traffic status leaks into weather availability'
        await page.screenshot(path='ph261_weather.png')

        await page.click('#tab-traffic')
        await page.wait_for_timeout(7000)
        t = await state()
        print('TRAFFIC MODE:')
        for k, v in t.items():
            print('  %s %s' % (v, k))
        assert t['#card-traffic'] == 'V' and t['#card-weather'] == 'H'
        assert t['#card-hazards'] == 'V' and t['#card-wxhaz'] == 'H'
        assert t['#card-avail-wx'] == 'H' and t['#card-avail-traf'] == 'V'
        assert t['#legend-flow'] == 'V' and t['#legend-inc'] == 'V'
        assert t['#legend-states'] == 'H' and t['#legend-weather'] == 'H'
        tr_avail = clean(await page.inner_text('#availability-traf'))
        print('TRAF AVAIL:', tr_avail.replace(chr(10), ' | '))
        assert 'Open-Meteo' not in tr_avail, 'weather status leaks into traffic availability'
        await page.screenshot(path='ph261_traffic.png')

        await page.click('#tab-weather')
        await page.wait_for_timeout(3000)
        w2 = await state()
        assert w2 == w, 'round-trip mismatch: %s' % {k: (w[k], w2[k]) for k in w if w[k] != w2[k]}
        print('ROUND TRIP: identical')
        print('ERRORS:', [clean(e) for e in errors] if errors else 'none')
        await browser.close()

asyncio.run(main())
