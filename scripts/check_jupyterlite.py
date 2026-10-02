"""Run representative notebooks in the real browser Pyodide kernel.

Requires internet access for the initial Pyodide runtime/package downloads.
Run after the site build; use --channel msedge for an installed Edge browser.
"""
import argparse
import json
from pathlib import Path
import re
import time
from playwright.sync_api import sync_playwright
from site_server import start_server

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',default='_build/html')
    parser.add_argument('--base-url',default='/')
    parser.add_argument('--channel',default=None)
    args=parser.parse_args()
    server,base=start_server(args.root,args.base_url)
    screenshots=ROOT/'test-results';screenshots.mkdir(exist_ok=True)
    notebooks=['01_aquarium_motion.ipynb','06_globe_projections.ipynb','08_neighborhood_3d.ipynb','13_lorenz_chaos.ipynb']
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(channel=args.channel,headless=True)
            # Clear saved execution output only in responses to this test browser.
            # This prevents a false pass on the precomputed native-Python outputs.
            def fresh_notebook(route):
                response=route.fetch()
                nb=response.json()
                for cell in nb['cells']:
                    if cell['cell_type']=='code':cell['outputs']=[];cell['execution_count']=None
                route.fulfill(response=response,json=nb)
            for name in notebooks:
                print(f'LOAD browser Pyodide: {name}',flush=True)
                # Isolate IndexedDB, service workers and restored workspaces per notebook.
                context=browser.new_context(viewport={'width':1400,'height':1000})
                context.route(re.compile(r'/files/[^/?]+\.ipynb(?:\?.*)?$'),fresh_notebook)
                page=context.new_page()
                page.goto(f'{base}/lite/lab/index.html?path={name}',wait_until='domcontentloaded')
                page.get_by_role('menuitem',name='Run',exact=True).wait_for(timeout=60000)
                page.locator('.jp-Notebook').wait_for(timeout=60000)
                page.locator('.jp-InputPrompt').first.wait_for(timeout=60000,state='attached')
                assert all(not text.strip() or text.strip()=='[ ]:' for text in page.locator('.jp-InputPrompt').all_text_contents()),'Test must start with cleared execution counts'
                page.get_by_role('menuitem',name='Run',exact=True).click()
                page.get_by_role('menuitem',name='Run All Cells',exact=True).click()
                print(f'RUN browser Pyodide: {name}',flush=True)
                count=sum(c['cell_type']=='code' for c in json.loads((ROOT/'content/notebooks'/name).read_text(encoding='utf-8'))['cells'])
                deadline=time.monotonic()+180
                while time.monotonic()<deadline:
                    page.wait_for_timeout(1000)
                    body=page.locator('body').inner_text()
                    if 'Traceback (most recent call last)' in body:
                        raise AssertionError(f'{name}:\n{body[-9000:]}')
                    prompts=page.locator('.jp-InputPrompt').all_text_contents()
                    if 'Python (Pyodide) | Idle' in body and f'[{count}]:' in prompts and '[*]:' not in prompts:
                        break
                else:
                    raise AssertionError(f'Kernel did not finish {name}: {body[-2000:]}')
                if name in ['01_aquarium_motion.ipynb','13_lorenz_chaos.ipynb']:
                    frame=page.frame_locator('iframe').last
                    frame.get_by_role('button',name='Play',exact=True).click(timeout=15000)
                    page.wait_for_timeout(250)
                    frame.get_by_role('button',name='Pause',exact=True).click()
                    assert frame.locator('#frame').input_value()!='0'
                page.screenshot(path=str(screenshots/f'pyodide-{name[:-6]}.png'),full_page=True)
                print(f'PASS browser Pyodide: {name}',flush=True)
                context.close()
            browser.close()
    finally:
        server.shutdown();server.server_close()


if __name__=='__main__':
    main()
