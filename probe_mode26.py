import asyncio
from playwright.async_api import async_playwright

URL = 'https://morth-accident-analytics.onrender.com/live'

def clean(s):
    return (s or '').encode('ascii', 'replace').decode()[:300]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)[:200]))
        await page.goto(URL, wait_until='networkidle', timeout=120000)
        await page.wait_for_timeout(9000)
        async def vis(sel):
            return await page.evaluate(
                "(sel) => { const el = document.querySelector(sel); "
                "return el ? !el.classList.contains('hidden') : 'MISSING'; }", sel)
        print('WEATHER MODE: card-weather=%s card-traffic=%s card-nearme=%s kpis=%s kpisT=%s'
              % (await vis('#card-weather'), await vis('#card-traffic'),
                 await vis('#card-nearme'), await vis('#live-kpis'),
                 await vis('#live-kpis-traffic')))
        # click a weather marker -> weather card
        await page.click('#tab-traffic')
        await page.wait_for_timeout(7000)
        print('TRAFFIC MODE: card-weather=%s card-traffic=%s card-nearme=%s kpis=%s kpisT=%s'
              % (await vis('#card-weather'), await vis('#card-traffic'),
                 await vis('#card-nearme'), await vis('#live-kpis'),
                 await vis('#live-kpis-traffic')))
        print('TRAFFIC KPIs:', clean(await page.inner_text('#live-kpis-traffic')))
        # click first incident in list -> traffic card must show it, weather card untouched
        items = await page.locator('#incident-list [data-inc]').count()
        print('INCIDENT BUTTONS:', items)
        w_before = await page.inner_text('#weather-detail')
        if items:
            await page.locator('#incident-list [data-inc]').first.click()
            await page.wait_for_timeout(4000)
        t_detail = await page.inner_text('#traffic-detail')
        w_after = await page.inner_text('#weather-detail')
        print('TRAFFIC DETAIL HEAD:', clean(t_detail[:220].replace(chr(10), ' | ')))
        print('WEATHER UNCHANGED:', w_before == w_after)
        await page.screenshot(path='ph26_traffic.png')
        # switch back to weather
        await page.click('#tab-weather')
        await page.wait_for_timeout(3000)
        print('BACK TO WEATHER: card-weather=%s card-traffic=%s'
              % (await vis('#card-weather'), await vis('#card-traffic')))
        print('WEATHER DETAIL STILL WEATHER:',
              'TomTom' not in await page.inner_text('#weather-detail'))
        await page.screenshot(path='ph26_weather.png')
        print('ERRORS:', [clean(e) for e in errors] if errors else 'none')
        await browser.close()

asyncio.run(main())
