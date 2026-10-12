import asyncio
from playwright.async_api import async_playwright

URL = 'https://morth-accident-analytics.onrender.com/live'

def clean(s):
    return (s or '').encode('ascii', 'replace').decode()[:150]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        errors, tile_reqs, failed_tiles = [], [], []
        page.on('pageerror', lambda e: errors.append(str(e)[:200]))
        page.on('response', lambda r: (
            tile_reqs.append(r.url) if '/api/live/traffic/tile/' in r.url and r.status == 200
            else (failed_tiles.append(r.status) if '/api/live/traffic/tile/' in r.url else None)))
        await page.goto(URL, wait_until='networkidle', timeout=120000)
        await page.wait_for_timeout(8000)
        await page.click('#tab-traffic')
        await page.wait_for_timeout(6000)
        n0 = len(tile_reqs)
        print('INITIAL TILES:', n0)
        # pan west to Mumbai + zoom in/out
        await page.evaluate('''() => {
          const t = document.getElementById('traffic-city');
          t.value = 'Mumbai'; t.dispatchEvent(new Event('change'));
        }''')
        await page.wait_for_timeout(5000)
        # zoom via buttons twice
        for _ in range(2):
            await page.locator('#map-traffic .leaflet-control-zoom-in').click()
            await page.wait_for_timeout(2500)
        for _ in range(2):
            await page.locator('#map-traffic .leaflet-control-zoom-out').click()
            await page.wait_for_timeout(2500)
        print('TILES AFTER NAV:', len(tile_reqs), '| failed:', failed_tiles[:5] or 'none')
        # click a road for segment details
        await page.mouse.click(720, 450)
        await page.wait_for_timeout(4000)
        pop = await page.locator('.leaflet-popup-content').count()
        print('SEGMENT POPUP:', pop)
        # tab switch back and forth: no duplicate maps
        await page.click('#tab-weather')
        await page.wait_for_timeout(2000)
        await page.click('#tab-traffic')
        await page.wait_for_timeout(4000)
        maps = await page.evaluate('''() => {
          let n = 0;
          document.querySelectorAll('.leaflet-container').forEach(() => n++);
          return n;
        }''')
        print('LEAFLET CONTAINERS:', maps, '(expect 2: weather + traffic)')
        print('TOTAL TILE REQS:', len(tile_reqs), '(bounded: viewport-driven)')
        print('ERRORS:', errors if errors else 'none')
        await page.screenshot(path='live_mumbai.png')
        print('screenshot saved')
        await browser.close()

asyncio.run(main())
